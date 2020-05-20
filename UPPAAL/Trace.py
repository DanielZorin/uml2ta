class StateNode:
    ''' UPPAAL trace state
    
    :param lst: list of states of each of the automata
    :param vars: list of variable values
    :param clocks: list of clock intervals'''
    def __init__(self, lst, vars, clocks):
        self.states = lst
        self.vars = vars
        self.clocks = clocks
        
    def __str__(self):
        return ','.join([str(s) for s in self.states])

class TransitionNode:
    ''' UPPAAL trace transition
    
    :param lst: list of activated transitions'''
    def __init__(self, lst):
        self.trans = lst
        
    def __str__(self):
        return ','.join([str(s) for s in self.trans])

class Trace:
    ''' UPPAAL trace'''
    def __init__(self):
        self.states = []
        self.transitions = []

    def getName(self, s, data):
        for ln in data["renamed"]:
            if ln[1] == s and ln[0] == None:
                return None
        res = s
        for i in range(len(data["renamed"]))[::-1]:
            if data["renamed"][i][1] == res:
                res = data["renamed"][i][0]
        return res
    
    def solveTimers(self, array):
        ''' Finds intervals for all timers instead of their differences'''
        values = []
        for cl in array:
            if cl[0] == "0":
                values.append([cl[1], " >= ", -cl[2] / 2])
            elif cl[1] == "0":
                values.append([cl[0], " <= ", cl[2] / 2])
        while True:
            leng = len(values)
            for cl in array:
                for v in values:
                    if v[0] == cl[1] and v[1] == " <= " and cl[0] != "0":
                        s = [cl[0], " <= ", v[2] + cl[2] / 2]
                        add = True
                        for v in values:
                            if s[0] == v[0] and s[1] == v[1]:
                                if v[1] == " <= " and v[2] <= s[2]:
                                    add = False
                                if v[1] == " >= " and v[2] >= s[2]:
                                    add = False
                        if add:
                            values.append(s)
                    if v[0] == cl[0] and v[1] == " >= " and cl[1] != "0":
                        s = [cl[1], " >= ", v[2] - cl[2] / 2]
                        add = True
                        for v in values:
                            if s[0] == v[0] and s[1] == v[1]:
                                if v[1] == " <= " and v[2] <= s[2]:
                                    add = False
                                if v[1] == " >= " and v[2] >= s[2]:
                                    add = False
                        if add:
                            values.append(s)
            if len(values) == leng:
                break
        return values
        
    def Import(self, file, data):
        ''' Loads trace from .xtr file
        
        :param file: .xtr file name
        :param data: upp data about state names'''
        f = open(file, "r")
        lines = f.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].replace("\n", "")
        i = 0
        # Read initial state
        framesize = 0
        curstate = []
        while lines[i] != ".":
            framesize += 1
            curstate.append(int(lines[i]))
            i += 1
        clocknames = ["0"]
        for c in data["clocks"]:
            clocknames.append(c)
        # Parse clocks
        clocks = []
        while not (lines[i] == "." and lines[i+1] == "."):
            i += 1
            c1 = clocknames[int(lines[i])]
            c2 = clocknames[int(lines[i+1])]
            limit = int(lines[i+2])
            clocks.append((c1, c2, limit))
            i += 3
        varnames = []
        for v in data["vars"]:
            varnames.append(v.name)
        # Parse variables
        i += 2
        vars = {}
        for v in varnames:
            vars[v] = int(lines[i])
            i += 1
        self.states.append(StateNode(curstate, vars, clocks))
        i += 1
        while i < len(lines) - 1:
            curstate = []
            for j in range(framesize):
                curstate.append(int(lines[i + j]))
            i += framesize
            # Parse clocks
            clocks = []
            while not (lines[i] == "." and lines[i+1] == "."):
                i += 1
                c1 = clocknames[int(lines[i])]
                c2 = clocknames[int(lines[i+1])]
                limit = int(lines[i+2])
                clocks.append((c1, c2, limit))
                i += 3
            # Parse variables
            i += 2
            vars = {}
            for v in varnames:
                vars[v] = int(lines[i])
                i += 1
            curtrans = []
            i += 1
            while lines[i] != ".":
                space = lines[i].index(" ")
                curtrans.append((int(lines[i][:space]), int(lines[i][space+1:])))
                i += 1
            i += 1
            self.states.append(StateNode(curstate, vars, clocks))
            self.transitions.append(TransitionNode(curtrans))
        f.close()
            
    def PrintTrace(self, data, vars=True, clocks=False):
        ''' :returns: string containing UML trace
        
        :param data: UPP data
        :param vars: boolean flag, if true, prints values of all variables on each step
        :param clocks: boolean flag, if true, prints values of all clocks on each step'''
        filtered = self.states
        counter = 1
        output = ""
        oldvalues = {}
        for c in data["clocks"]:
            oldvalues[c] = {"lower":-1, "upper":-1}
        for i in range(1, len(filtered)):
            valid = False
            for j in range(len(filtered[i].states)):
                if filtered[i].states[j] != filtered[i-1].states[j]:
                    s1 = self.getName(data["states"][j][filtered[i-1].states[j]], data)
                    s2 = self.getName(data["states"][j][filtered[i].states[j]], data)
                    if s1 and s2:
                        output += "Step " + str(counter) + "\n" 
                        output += data["processes"][j] + " :: " + s1 + " --> " + s2 + "\n"
                        valid = True
                        print counter
                        counter += 1
            if not valid:
                continue
            if vars:        
                for v in filtered[i].vars.keys():
                    if filtered[i].vars[v] != filtered[i-1].vars[v]:
                        output +=  v + " = " + str(filtered[i].vars[v]) + "\n"
            # Print clock ranges
            if False:
                for cl in filtered[i].clocks:
                    if cl[0] == "0":
                        print cl[1], " >= ", -cl[2] / 2
                    elif cl[1] == "0":
                        print cl[0], " <= ", cl[2] / 2
                    else:
                        print cl[0], " - ", cl[1], " <= ", cl[2] / 2
            if clocks:
                values = self.solveTimers(filtered[i].clocks)
                for v in values:
                    if v[1] == " >= " and oldvalues[v[0]]["lower"] != v[2]:
                        output += v[0] + v[1] + str(v[2]) + "\n"
                        oldvalues[v[0]]["lower"] = v[2]
                    elif v[1] == " <= " and oldvalues[v[0]]["upper"] != v[2]:
                        output += v[0] + v[1] + str(v[2]) + "\n"
                        oldvalues[v[0]]["upper"] = v[2]
        return output
                    