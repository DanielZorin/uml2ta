from UMLStateMachine.Model import Model
from UMLStateMachine.State import *
from UMLStateMachine.Transition import *
from UMLStateMachine.StateMachine import *
from UMLStateMachine.Parsers.ActionParser import AssignStatement
from UMLStateMachine.Parsers.DeclarationsParser import ClockVar
from UMLStateMachine.Parsers.GuardParser import AndAtom
import copy, random, re
import subprocess, os

statenames = []
varnames = []
    
def findInitialStates(sm):
    ''' Finds the initial states of the whole state machine and marks them with setInitial()'''
    tmp = sm.getChildren()
    while True:
        res = [x for x in tmp if isinstance(x, InitialState)]
        if len(res) > 0:
            break
        tmp2 = []
        for t in tmp:
            tmp2 += t.getChildren()
        tmp = [x for x in tmp2]
    init = [res[0]]
    while True:
        newInit = []
        for t in init:
            trans = [x.target for x in sm.findTransitions(src=t)]
            for s in trans:
                if isinstance(s, InitialState):
                    newInit.append(s)
                else:
                    s.setInitial()
        if newInit == []:
            break
        init = [x for x in newInit]

def insertSubMachines(sm, prev):
    ''' Inserts all submachines into the main state machine, renaming states and variables to avoid collision'''
    subStates = [s for s in sm.getAllChildren() if isinstance(s, SubMachineState)]
    for s in subStates:
        s.statemachine = insertSubMachines(s.statemachine, prev + [s.name])
        #if s.statemachine in newInserted:
        s.statemachine = s.statemachine.getCopy()
        #s.statemachine.name += "_double"
        for stub in s.getChildren():
            stub.ref_state = (st for st in s.statemachine.getAllChildren() if st.name == stub.ref_state.name).next()
        #else:
        #    newInserted.append(s.statemachine)
        ch = s.statemachine.getChildren()
        transin = sm.findTransitions(src = None, dst = s)
        transout = sm.findTransitions(src = s, dst = None)
        
        # Renaming states to avoid name collision
        for st in s.statemachine.getAllChildren():
            oldname = st.name       
            if sm.containsState(st.name):
                st.name += "_from_" + s.name
            if sm.containsState(st.name):
                i = 1
                while True:
                    if not sm.containsState(st.name + "_" + str(i)):
                        st.name = st.name + "_" + str(i)
                        break
                    i += 1  
            statenames.append(['::'.join(prev + [s.name, oldname]), st.name])  
                
        if len(ch) == 1 and ch[0].isXor():
            cont = ch[0]
            s.parent.addState(cont)
            cont.setParent(s.parent)
            for t in transin:
                t.setDst(cont)
            for t in transout:
                t.setSrc(cont)
            for t in s.statemachine.transitions:
                sm.transitions.append(t)
        else:
            newXor = CompositeState(s.name + "_replacement")
            s.parent.addState(newXor)
            newXor.setParent(s.parent)

            for newState in ch:
                newXor.addState(newState)
                newState.setParent(newXor)

            for t in s.statemachine.transitions:
                sm.transitions.append(t)             
            for t in transin:
                t.setDst(newXor)
            for t in transout:
                t.setSrc(newXor)
         
        for st in s.getChildren():
            for t in sm.findTransitions(src = None, dst = st):
                t.setDst(st.ref_state)    
            for t in sm.findTransitions(src = st, dst = None):
                t.setSrc(st.ref_state)
            
        def RenameAll(oldVar, newVar):
            for t in s.statemachine.transitions:
                if t.guard:
                    t.guard.Rename(oldVar, newVar)
                if t.effect:
                    for g in t.effect:
                        g.Rename(oldVar, newVar)
                if t.trigger:
                    if t.trigger.type != 'timeout':
                        if t.trigger.name == oldVar:
                            t.trigger.name = newVar
                    else:
                        t.trigger.expression.Rename(oldVar, newVar)
            for st in s.statemachine.getAllChildren():
                if st.invariant:
                    st.invariant.Rename(oldVar, newVar)
            varnames.append(['::'.join(prev + [s.name, oldVar]) , newVar])

        for v in s.statemachine.variables.keys():
            if not sm.hasVariable(v):
                sm.addVariable(s.statemachine.getVariable(v))
                varnames.append(['::'.join(prev + [s.name, v]) , v])
            else:                
                oldVar = s.statemachine.variables[v].name
                newVar = oldVar + "_" + s.name
                s.statemachine.variables[v].name = newVar
                RenameAll(oldVar, newVar)          
                sm.addVariable(s.statemachine.getVariable(v))
        if s.code:
            string = s.code.replace(" ", "").replace("\n", "")
            vars = string.split(";")
            for v in vars:
                parts = v.split("=")
                if len(parts) == 2 and parts[0].startswith("@"):
                    RenameAll(parts[0][1:], parts[1])
            s.code = None
                
        new = []
        for st in s.parent.states:
            if st != s:
                new.append(st)
        s.parent.states = new  
        
    return sm

def correctAndStates(sm):
    ''' Adds explicit entries and exits to AND states and change transitions accordingly'''
    andStates = [s for s in sm.getAllChildren() if s.isAnd()]
    for s in andStates:
        entry = InitialState(s.name + "_entry")
        entry.setParent(s)
        s.addState(entry)
        
        exit = FinalState(s.name + "_exit")
        exit.setParent(s)
        s.addState(exit)

        for t in sm.findTransitions(src = None, dst = s):
            t.setDst(entry)
            
        for t in sm.findTransitions(src = s, dst = None):
            t.setSrc(exit)
            
def correctXorStates(sm):
    ''' Changes transitions so that they end in entry/exit states instead of compound states'''
    xorStates = [s for s in sm.getAllChildren() if s.isXor()]
    for s in xorStates:
        # normal = False => all children are compound. Otherwise, there MUST be an entry and an exit
        normal = False
        for c in s.getChildren():
            if not (c.isComposite() or c.isBasic()):
                normal = True

        if normal == False:
            # TODO: test
            entry = InitialState(s.name + "_entry")
            entry.setParent(s)
            s.addState(entry)
            
            exit = FinalState(s.name + "_exit")
            exit.setParent(s)
            s.addState(exit)
            for t in sm.findTransitions(src = None, dst = s):
                t.setDst(entry)
                
            for t in sm.findTransitions(src = s, dst = None):
                t.setSrc(exit)
            continue
        
        if s.parent.isAnd():
            entry = (e for e in s.getChildren() if e.isEntry()).next()
            try:
                exit = (e for e in s.getChildren() if e.isExit()).next()
            except StopIteration:
                exit = FinalState(s.name + "_exit")
                s.addState(exit)
                exit.setParent(s)
            andentry = (p for p in s.parent.getChildren() if p.isEntry()).next()
            andexit = (p for p in s.parent.getChildren() if p.isExit()).next()
            sm.addTransition(Transition(andentry, entry, None, None, None))
            sm.addTransition(Transition(exit, andexit, None, None, None))
        else:
            inTrans = sm.findTransitions(src = None, dst = s)
            outTrans = sm.findTransitions(src = s, dst = None)
            if inTrans:
                entry = (e for e in s.getChildren() if e.isEntry()).next()
                for t in inTrans:
                    t.setDst(entry)
            if outTrans:
                exit = (e for e in s.getChildren() if e.isExit()).next()
                for t in outTrans:
                    t.setSrc(exit)
                    
def addExits(sm):
    ''' Adds missing but implied exit states'''
    def isDescendant(s1, s2):
        ''' Checks if s1 belongs to an ancestor of s2 (s2 is nested in s1.parent)'''
        tmp = s2.parent
        while tmp != None:
            if s1.parent == tmp:
                return True
            try:
                tmp = tmp.parent
            except:
                tmp = None
        return False
    
    while True:
        clear = True
        newTrans = []
        for t in sm.transitions:
            if ((t.dst.isBasic() or t.dst.isExit()) and not t.src.isExit() and t.src.parent != t.dst.parent) or \
            ((t.dst.isBasic() or t.dst.isExit()) and t.src.isExit() and t.src.parent.parent != t.dst.parent) or \
            ((t.dst.isEntry() and not t.src.isExit()) and t.src.parent != t.dst.parent.parent) or \
            ((t.dst.isEntry() and t.src.isExit()) and t.src.parent.parent != t.dst.parent.parent):
                clear = False
                if isDescendant(t.src, t.dst):
                    newentry = InitialState(t.dst.name + "_extra_entry")
                    if t.dst.isEntry():
                        t.dst.parent.parent.addState(newentry)
                        newentry.setParent(t.dst.parent.parent)                          
                    else:
                        t.dst.parent.addState(newentry)
                        newentry.setParent(t.dst.parent)
                    newTrans.append(Transition(newentry, t.dst, None, None, None))
                    t.setDst(newentry)
                else:
                    newexit = FinalState(t.src.name + "_extra_exit")
                    if t.src.isExit():
                        t.src.parent.parent.addState(newexit)
                        newexit.setParent(t.src.parent.parent)
                    else:
                        t.src.parent.addState(newexit)
                        newexit.setParent(t.src.parent)                       
                    newTrans.append(Transition(newexit, t.dst, None, None, None))
                    t.setDst(newexit)
        
        for t in newTrans:
            sm.addTransition(t)
        if clear:
            return
        
def clearExits(sm):
    ''' Removes guards and effects from transitions terminating in exit states'''
    # TODO: fix the case with exit -> exit transitions
    for s in sm.getAllChildren():
        if (s.isExit() or s.isEntry()) and not s.parent.isAnd():
            if s.parent.isXor() and s.parent.parent.isAnd():
                #TODO
                '''
                if t.guard != None or t.effect != None or t.trigger != None:
                    s = SimpleState("before_exit_" + t.dst.name)
                    statenames.append([None, t.dst.parent.name + ".before_exit_" + t.dst.name])
                    t.src.parent.addState(s)
                    s.setParent(t.dst.parent)
                    sm.addTransition(Transition(s, t.dst, None, None, None))
                    t.setDst(s)
                if t.src.isEntry():
                    if t.guard != None or t.effect != None or t.trigger != None:
                        s = SimpleState("after_entry_" + t.dst.name)
                        statenames.append([None, t.dst.parent.name + ".after_entry_" + t.dst.name])
                        t.dst.parent.addState(s)
                        s.setParent(t.src.parent)
                        sm.addTransition(Transition(t.src, s, None, None, None))
                        t.setSrc(s)
                '''
            else:
                # Simple -> exit -> simple, not a part of AND structure
                intrans = [t for t in sm.transitions if t.dst == s]
                outtrans = [t for t in sm.transitions if t.src == s]
                if len(intrans) > 0 and len(outtrans) > 0:
                    inNotEmpty = [t for t in intrans if t.guard != None or t.effect != None or t.trigger != None]
                    outNotEmpty = [t for t in outtrans if t.guard != None or t.effect != None or t.trigger != None]
                    if len(inNotEmpty) == 0 and len(outNotEmpty) == 0:
                        newTrans = [t for t in sm.transitions if not t in intrans and not t in outtrans]
                        for s1 in [t.src for t in intrans]:
                            for s2 in [t.dst for t in outtrans]:
                                tr = Transition(s1, s2, None, None, None)
                                newTrans.append(tr)
                        sm.transitions = newTrans
                    elif len(inNotEmpty) > 0 and len(outNotEmpty) == 0:
                        newTrans = [t for t in sm.transitions if not t in intrans and not t in outtrans]
                        for t in intrans: 
                            for s2 in [t.dst for t in outtrans]:
                                tr = Transition(t.src, s2, t.guard, t.effect, t.trigger)
                                newTrans.append(tr)
                        sm.transitions = newTrans     
                    elif len(inNotEmpty) == 0 and len(outNotEmpty) > 0:
                        newTrans = [t for t in sm.transitions if not t in intrans and not t in outtrans]
                        for t in outtrans: 
                            for s1 in [t.src for t in intrans]:
                                tr = Transition(s1, t.dst, t.guard, t.effect, t.trigger)
                                newTrans.append(tr)
                        sm.transitions = newTrans
                    else:
                        news = SimpleState(s.name)
                        for t in intrans:
                            t.dst = news
                        for t in outtrans:
                            t.src = news
                        s.parent.states = [q for q in s.parent.states if q != s]        
                
def deleteXor(sm):
    ''' Flattens the state machine by optimizing XOr states inserted one into another'''
    # Skip top-level states and concurrent regions
    xorStates = []
    newtrans = []
    
    for s in sm.getChildren():
        xorStates += [s for s in s.getAllChildren() if s.isXor() and not s.parent.isAnd() and not isinstance(s.parent, Model)]
        
    newchild = [x for x in sm.getAllChildren() if x not in xorStates and x.parent not in xorStates]    
    for s in xorStates:
        child = s.getChildren()
        for c in child:
            if s.invariant:
                if c.invariant:
                    c.invariant += s.invariant
                else:
                    c.invariant = s.invariant
            s.parent.addState(c)
            c.setParent(s.parent)
        
        for c in child:
            if c.isEntry():
                try:
                    # TODO: this shouldn't be happening
                    ent = sm.findTransitions(src=c, dst=None)[0].dst
                    for t in sm.findTransitions(src=None, dst=c):
                        t.setDst(ent)
                except:
                    newchild.append(c)
            elif c.isExit():
                try:
                    inSet = [t for t in sm.findTransitions(src=None, dst=c)]
                    outSet = [t for t in sm.findTransitions(src=c, dst=None)]
                    exit = sm.findTransitions(src=c)[0].dst
                    for t in inSet:
                        for t2 in outSet:
                            sm.transitions.append(Transition(t.src, t2.dst, t.trigger, t.guard, t.effect))
                except:
                    newchild.append(c)
            else:
                newchild.append(c)
    for t in sm.transitions:
        if (t.src in newchild) and (t.dst in newchild):
            newtrans.append(t)
    sm.transitions = newtrans
                    
    for s in sm.getAllChildren():
        s.states = [x for x in s.states if not x in xorStates and x in newchild]

def getTimeEstimate(basicBlockCode):
    ''' Calculates execution time using WCET methods

    :param basicBlockCode: string var with C code of the basic block
    '''    
    dirName = '../wcet/'
    tmpDirName = '../wcet/tmp/'
    fileWithCode = open(tmpDirName + 'code.c', "w")
    fileWithCode.write(basicBlockCode)
    fileWithCode.close()
    
    cmdline = dirName + 'count_wcet_basic_block.sh ' + tmpDirName + 'code.c'

    proc = subprocess.Popen(
        cmdline,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = proc.communicate()
    os.remove(tmpDirName + 'code.c')

    try:
        wcet = int(stdoutdata)
        return wcet
    except ValueError:
        print "Error while counting wcet"
        if len(stderrdata) > 0:
           print '   ' + stderrdata
    return random.randint(0, 10)

def estimateTime(sm, timers):
    ''' Invokes WCET in all nodes where it is necessary

    :param timers: timers created by `createWcetTimers` function'''
    addedTimers = set([])
    for s in sm.getAllChildren():
        if s.isBasic() and s.code:
            exp = re.compile(r"wcet( )*\{([^\}]*)\}")
            m = exp.match(s.code)
            if m:
                limit = getTimeEstimate(m.group(2))
                addedTimers.add(timers[s])
                for t in sm.findTransitions(src=None, dst=s):
                    assign = AssignStatement(timers[s], "0")
                    tmp = str(assign)
                    if not t.effect:
                        t.effect = [assign]
                    else:
                        skip = False
                        for e in t.effect:
                            if str(e) == tmp:                                                  
                                skip = True
                        if not skip:
                            t.effect += [assign]
                if not s.invariant:
                    s.invariant = timers[s] + "<=" + str(limit)
                else:
                    s.invariant = AndAtom([s.invariant, timers[s] + "<=" + str(limit)])
                s.code = None
    for t in addedTimers:
        sm.addVariable(ClockVar(t))

def createWcetTimers(sm):
    ''' Creates timers for WCET estimate. Timers are created only when necessary, e.g. a second timer 
    is added only when two timers have to be run in concurrent regions'''
    clocks = ["wcet_clock_1"]
    todo = sm.getChildren()
    result = {}
    
    for s in sm.getChildren():
        result[s] = "wcet_clock_1"
    while len(todo) > 0:
        newtodo = []
        for s in todo:
            if not s.isAnd():
                for c in s.getChildren():
                    result[c] = result[s]
                    newtodo.append(c)
            else:
                child = s.getChildren()
                if len(child) >= 1:
                    result[child[0]] = result[s]
                    newtodo.append(child[0])
                for c in child[1:]:
                    result[c] = "wcet_clock_" + str(len(clocks) + 1)
                    newtodo.append(c)
        todo = newtodo
    return result                

def NormalizeStateMachine(sm, flatten=True, deadlines=False):
    ''' Converts a State Machine defined by ArgoUML to an HTA-like structure that 
    can be converted to UPPAAL TA with TranslationAlgorithm'''
    newsm = copy.deepcopy(sm)
    # All renamed states are mentioned here
    newsm = insertSubMachines(newsm, [])
    print "Adding missing entry and exit states..."
    correctAndStates(newsm)
    correctXorStates(newsm)
    print "Flattening the statechart..."  
    deleteXor(newsm)
    print "Correcting exit transitions..."
    clearExits(newsm)
    addExits(newsm)
    print "Searching initial states..."
    findInitialStates(newsm)
    if deadlines:
        print "Estimating execution time..."
        timers = createWcetTimers(newsm)
        estimateTime(newsm, timers)
    return newsm, [statenames, varnames]
