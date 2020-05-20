# Uppaal Timed Automata grammar can be downloaded from here: http://www.cs.aau.dk/~behrmann/utap/syntax.html
from UPPAAL.Process import Process
from UPPAAL.Location import Location
from UPPAAL.Channel import Channel
import xml.dom.minidom, pickle

class TimedAutomaton:
    ''' UPPAAL timed automaton'''

    def __init__(self):
        self.processes = []
        self.channels = []
        self.variables = []
        # Clocks are represented by strings
        self.clocks = []
        
    def addProcess(self, process):
        ''' Add a new :class:`~UPPAAL.Process.Process`'''
        self.processes.append(process)
    
    def addClock(self, s):
        ''' Add a new clock
        
        :param s: clock name'''
        self.clocks.append(s)
        self.clocks = list(set(self.clocks))
        
    def addChannel(self, channel):
        ''' Add a new :class:`~UPPAAL.Channel.Channel`'''
        # Using a generator object for lazy search
        try:
            exists = (c for c in self.channels if c.name == channel.name).next()
            # TODO: if the types aren't identical, it'd probably be better to raise some kind of error
            # or at least write a message to the log
            return
        except StopIteration:
            pass
        self.channels.append(channel)
        
    def addVariable(self, var):
        ''' Add a new :class:`~UPPAAL.Variable.Variable`'''
        try:
            exists = (c for c in self.variables if c.name == var.name).next()
            return
        except StopIteration:
            pass
        self.variables.append(var)
        
    def getVariable(self, name):
        ''' :returns: varibale with the given name'''
        try:
            exists = (c for c in self.variables if c.name == name).next()
            return exists
        except StopIteration:
            pass            
        
    def __str__(self):
        s = ''
        s += reduce(lambda x,y: x + y.name + "_proc = " + y.name + '();\n', self.processes, '')
        s += 'system ' + ', '.join([p.name + "_proc" for p in self.processes]) + ';\n'
        return s
    
    def ClearUp(self):
        newp = []
        for p in self.processes:
            if len(p.transitions) > 0:
                p.ClearUp()
                newp.append(p)
        self.processes = newp
        if len(self.processes) == 0:
            p = Process("single_process")
            idle = Location("idle")
            p.addLocation(idle)
            self.processes = [p]

    def ExportToUpp(self, filename, renamed):
        ''' Exports the auxiliary data about renamed states to .upp'''
        data = {}
        data["vars"] = self.variables
        data["clocks"] = self.clocks
        data["renamed"] = renamed[0]
        data["renamedvars"] = renamed[1]
        data["processes"] = {}
        data["states"] = {}
        data["statenames"] = {}
        for i in range(len(self.processes)):
            data["processes"][i] = self.processes[i].name
            data["states"][i] = {}
            j = 0
            for l in self.processes[i].locations.values():
                data["states"][i][j] = l.oldname
                data["statenames"][l.oldname] = l.name
                j += 1
        
        f = open(filename, "wb")
        p = pickle.Pickler(f)
        p.dump(data)
        f.close()
    
    def ExportToXml(self):
        ''' Creates a UPPAAL XML file
        
        :returns: prettified XML as a string'''
        dom = xml.dom.minidom.Document()
        nta = dom.createElement("nta")
        dom.appendChild(nta)
        
        decl = dom.createElement("declaration")
        s = reduce(lambda x, y: x + str(y) + "\n", self.channels, "")
        s += reduce(lambda x, y: x + str(y) + "\n", self.variables, "")
        s += reduce(lambda x, y: x + "clock " + str(y) + ";\n", self.clocks, "")
        decltext = dom.createTextNode(s)
        decl.appendChild(decltext)
        nta.appendChild(decl)
           
        for p in self.processes:
            nta.appendChild(p.GetXml())
        
        system = dom.createElement("system")
        txt = dom.createTextNode(str(self))
        system.appendChild(txt)
        nta.appendChild(system)
        return dom.toxml()
