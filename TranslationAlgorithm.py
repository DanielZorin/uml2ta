from UPPAAL.Location import Location
from UPPAAL.Process import Process
from UPPAAL.Transition import Transition
from UPPAAL.Channel import Channel
from UPPAAL.Variable import Variable
from UPPAAL.TimedAutomaton import TimedAutomaton

def add_sync_transition(p, source, target, g, syn):
    ''' Adds a transition with guard and synchronization'''
    t = Transition(source, target)
    if not g is None:
        t.addGuard(str(g))
    if not syn is None:
        if syn.type != 'timeout':
            t.addSync(syn.name + "?")
            '''t2 = Transition(source, target)
            t2.guard = t.guard
            t2.assign = t.assign
            t2.addSync(syn.name + "_urg?")
            p.addTransition(t2)'''
        else:
            timeout = syn.expression
            if str(timeout).find("self.c") != -1:
                # Maximum beedlowcode
                # Clock is named "s_timeout", and here the name of the state is
                # "s_active_in_parent", so the first word is used
                name = t.src.name[:t.src.name.index("_active")] + "_timeout"
                timeout.Rename("self.c", name)
                t.addGuard(str(timeout))
                for tran in p.findTransitions(src = None, dst = t.src):
                    tran.addAssign(name + " = 0")
            else:
                t.addGuard(str(timeout))
    p.addTransition(t)
    return t

def add_assign(ta, t, r):
    ''' Adding assignment in a separate function because we need to get the information about variables
    to add a correct equivalent of x=random()'''
    if not r is None:
        for assign in r:
            if assign.type == 'signal':
                t.addSync(str(assign).replace("!!", "").replace(";", "") + "!")
            elif assign.type == 'randomassign':
                # Not checking whether such variable exists because it's checked during XMI parsing
                v = ta.getVariable(assign.var_name)
                name = t.addSelect(v.start, v.end)
                t.addAssign(assign.var_name + "=" + name)
            else:
                t.addAssign(str(assign).replace(";", ""))

def make_tree_set(sm, b):
    ''' Calculates the tree set of exit cascades'''
    if not b.isExit():
        return [[]]
    result = []
    inSet = [p.src for p in sm.findTransitions(src = None, dst = b)]
    tempSets = [make_tree_set(sm, b0) for b0 in inSet]
    if b.parent.isAnd():
        result = [[b]]
        for tmp in tempSets:
            tmpresult = []
            for r in result:
                for x in tmp:
                    new = r + x
                    tmpresult.append(list(set(new)))
            result = tmpresult
    if b.parent.isXor():
        for tmp in tempSets:
            if tmp == [[]]:
                result.append([b])
            else:
                for tmpi in tmp:
                    tmpi.append(b)
                    result.append(list(set(tmpi)))
    return result

def add_exit_cascades(sm, ta, s, p):
    ''' Adds exit cascades denoting exit from composite states'''
    child = s.getChildren()
    twoChild = []
    for c in child:
        twoChild.extend(c.getChildren())
    for ex in twoChild:
        exTrans = sm.findTransitions(src = ex, dst = None)
        try:
            # Apparently it's Basic, entry and exit
            gen = (t for t in exTrans if t.dst.isEntry() or t.dst.isExit() or t.dst.isBasic()).next()
        except StopIteration:
            continue
        
        treeSet = make_tree_set(sm, ex)
        k = 0
        for t in treeSet:
            k += 1
            tleaves = []
            for v in t:
                if v.isExit() and len([x for x in sm.findTransitions(src = None, dst = v) if x.src.isBasic()]) > 0:
                    tleaves.append(v)
                    
            tleaves2 = [z for z in t if z.isExit()]
                    
            for e in tleaves:
                var = Variable('int', "exit_" + e.name + "_ready", 0, 0, 1)
                ta.addVariable(var)

            
            for trans in exTrans:
                if trans.dst.isBasic() or trans.dst.isEntry():                   
                    if tleaves == []:
                        continue 
                    for i in range(1, len(tleaves2) + 1):
                        l = Location("exit_cascade_" + ex.name + "_" + str(k) + "_" + str(i), commit=True, invariant="true")
                        p.addLocation(l)
                    
                    newt = add_sync_transition(p, p.locations[ex.parent.name + "_active_in_" + s.name],
                                        p.locations["exit_cascade_" + ex.name + "_" + str(k) + "_1"],
                                        trans.guard, trans.trigger)
                    
                    for e in tleaves:
                        newt.addGuard("exit_" + e.name + "_ready == 1")
                    
                    for i in tleaves2:
                        c = Channel("exit_" + i.parent.name, "h", False)
                        ta.addChannel(c)
                    
                    for i in range(1, len(tleaves2)):
                        newt = Transition(p.locations["exit_cascade_" + ex.name + "_" + str(k) + "_" + str(i)],
                                          p.locations["exit_cascade_" + ex.name + "_" + str(k) + "_" + str(i + 1)],
                                          sync = "exit_" + tleaves2[i - 1].parent.name + "!")
                        p.addTransition(newt)
                       
                    b = trans.dst    
                    if b.isBasic():
                        newt = Transition(p.locations["exit_cascade_" + ex.name + "_" + str(k) + "_" + str(len(tleaves2))],
                                          p.locations[b.name + "_active_in_" + s.name],
                                          sync = "exit_" + tleaves2[len(tleaves2) - 1].parent.name + "!")
                        add_assign(ta, newt, trans.effect)
                        p.addTransition(newt)
                    
                    if b.isEntry():
                        newt = Transition(p.locations["exit_cascade_" + ex.name + "_" + str(k) + "_" + str(len(tleaves2))],
                                          p.locations[s.name + "_aux_" + b.parent.name + "_" + b.name],
                                          sync = "exit_" + tleaves2[len(tleaves2) - 1].parent.name + "!")
                        add_assign(ta, newt, trans.effect)
                        p.addTransition(newt)
        
def add_exit_guards(sm, ta, s, p):
    ''' Adds guards to exit cascades'''
    for ex in [e for e in s.getChildren() if e.isExit()]:
        inSet = [t.src for t in sm.findTransitions(src=None, dst=ex) if t.src.isBasic()]
        for b in inSet:
            for t in p.transitions:
                res = False
                if t.src.name == b.name + "_active_in_" + s.name:
                    if t.dst.name.endswith("_active_in_" + s.name):
                        all = s.getAllChildren()
                        for a in all:
                            if t.dst.name.startswith(a.name):
                                if a.isBasic() and a in inSet:
                                    res = True
                    if res == False and not ex.isBasic():
                        v = Variable('int', "exit_" + ex.name + "_ready", 0, 0, 1)
                        ta.addVariable(v)
                        t.addAssign("exit_" + ex.name + "_ready := 0")
                        
            for t in p.transitions:
                res = False
                if t.dst.name == b.name + "_active_in_" + s.name:
                    if t.src.name.endswith("_active_in_" + s.name):
                        all = s.getAllChildren()
                        for a in all:
                            if t.src.name.startswith(a.name):
                                if a.isBasic() and a in inSet:
                                    res = True
                    if res == False and not ex.isBasic():
                        v = Variable('int', "exit_" + ex.name + "_ready", 0, 0, 1)
                        ta.addVariable(v)
                        t.addAssign("exit_" + ex.name + "_ready := 1")

def process_and(sm, ta, s, p):
    ''' Translates a concurrent composite state to UPPAAL'''
    child = [x for x in s.getChildren() if x.isBasic() or x.isAnd() or x.isXor()]
    l = Location(s.name + "_active", commit=False)
    l.oldname = s.name
    if s.invariant:
        l.addInvariant(s.invariant)
    p.addLocation(l)
    if s.initial:
        tr = Transition(p.locations[s.name + "_idle"], p.locations[s.name + "_active"], sync="init_" + s.name + "?")
        p.addTransition(tr)
    
    for e in s.getChildren():
        if e.isEntry():
            for b in child:
                l = Location("enter_" + e.name + "_loc_" + b.name, commit=True, invariant="true")
                p.addLocation(l)
            c = Channel("enter_" + s.name + "_via_" + e.name + "_in_" + s.parent.name, "h", False)
            ta.addChannel(c)
            tr = Transition(p.locations[s.name + "_idle"],
                            # TODO: check that child isn't []
                            p.locations["enter_" + e.name + "_loc_" + child[0].name], 
                            sync="enter_" + s.name + "_via_" + e.name + "_in_" + s.parent.name + "?")
            p.addTransition(tr)
            
            for i in range(len(child) - 1):
                try:
                    entry = (p for p in child[i].getChildren() if p.isEntry()).next()
                except:
                    print child[i], [p for p in child[i].getChildren()]
                    raise 9
                tr = Transition(p.locations["enter_" + e.name + "_loc_" + child[i].name],
                            p.locations["enter_" + e.name + "_loc_" + child[i + 1].name], 
                            sync="enter_" + child[i].name + "_via_" + entry.name + "_in_" + s.name + "!")
                p.addTransition(tr)
            
            entry = (p for p in child[len(child)-1].getChildren() if p.isEntry()).next()
            tr = Transition(p.locations["enter_" + e.name + "_loc_" + child[len(child)-1].name],
                            p.locations[s.name + "_active"], 
                            sync="enter_" + child[len(child)-1].name + "_via_" + entry.name + "_in_" + s.name + "!")
            p.addTransition(tr)
    c = Channel("exit_" + s.name, "h", False)
    ta.addChannel(c)
    tr = Transition(p.locations[s.name + "_active"],
                    p.locations[s.name + "_idle"], 
                    sync="exit_" + s.name + "?")
    p.addTransition(tr)
    

def process_xor(sm, ta, s, p):
    ''' Translates a composite state to UPPAAL'''
    for b in s.getChildren():
        if b.isXor() or b.isAnd() or b.isBasic():
            l = Location(b.name + "_active_in_" + s.name, commit=False)
            l.oldname = s.name + "." + b.name
            if b.invariant:
                l.addInvariant(b.invariant)
            p.addLocation(l)
            if b.initial:
                t = Transition(p.locations[s.name + "_idle"], p.locations[b.name + "_active_in_" + s.name], sync="init_" + s.name + "?")
                p.addTransition(t)
            if b.isXor() or b.isAnd():
                for e in b.getChildren():
                    if e.isEntry():
                        c = Channel("enter_" + b.name + "_via_" + e.name + "_in_" + s.name, "h", False)
                        ta.addChannel(c)
                        l = Location(s.name + "_aux_" + b.name + "_" + e.name, commit=True, invariant="true")
                        p.addLocation(l)
                        t = Transition(p.locations[s.name + "_aux_" + b.name + "_" + e.name],
                                       p.locations[b.name + "_active_in_" + s.name],
                                       sync = "enter_" + b.name + "_via_" + e.name + "_in_" + s.name + "!")
                        p.addTransition(t)
                        
    # Add Basic -> Basic transitions
    basictr = []
    for b in [s1 for s1 in s.getChildren() if s1.isBasic()]:
        for t in sm.findTransitions(src=b, dst=None):
            if t.dst in s.getChildren() and t.dst.isBasic():
                basictr.append(t)
    for t in basictr:
        newt = add_sync_transition(p, p.locations[t.src.name + "_active_in_" + s.name], 
                            p.locations[t.dst.name + "_active_in_" + s.name], 
                            t.guard, t.trigger)
        add_assign(ta, newt, t.effect)
    
    # Add Basic -> Entry transitions
    basicentrytr = []
    for b in [s1 for s1 in s.getChildren() if s1.isBasic()]:
        for t in sm.findTransitions(src=b, dst=None):
            if t.dst.parent in s.getChildren() and t.dst.isEntry():
                basicentrytr.append(t)
    for t in basicentrytr:
        newt = add_sync_transition(p, p.locations[t.src.name + "_active_in_" + s.name], 
                            p.locations[s.name + "_aux_" + t.dst.parent.name + "_" + t.dst.name], 
                            t.guard, t.trigger)
        add_assign(ta, newt, t.effect)

    # Add Entry -> Basic transitions
    entrybasictr = []
    for b in [s1 for s1 in s.getChildren() if s1.isEntry()]:
        for t in sm.findTransitions(src=b, dst=None):
            if t.dst in s.getChildren() and t.dst.isBasic():
                entrybasictr.append(t)
    for t in entrybasictr:
        c = Channel("enter_" + s.name + "_via_" + t.src.name + "_in_" + s.parent.name, "h", False)
        ta.addChannel(c)
        newt = Transition(p.locations[s.name + "_idle"], 
                            p.locations[t.dst.name + "_active_in_" + s.name], 
                            sync = "enter_" + s.name + "_via_" + t.src.name + "_in_" + s.parent.name + "?")
        add_assign(ta, newt, t.effect)
        p.addTransition(newt)
        
    # Add Entry -> Entry transitions
    entrytr = []
    for b in [s1 for s1 in s.getChildren() if s1.isEntry()]:
        for t in sm.findTransitions(src=b, dst=None):
            if t.dst.parent in s.getChildren() and t.dst.isEntry():
                entrytr.append(t)
    for t in entrytr:
        c = Channel("enter_" + s.name + "_via_" + t.src.name + "_in_" + s.parent.name, "h", False)
        ta.addChannel(c)
        newt = Transition(p.locations[s.name + "_idle"], 
                            p.locations[s.name + "_aux_" + t.dst.parent.name + "_" + t.dst.name], 
                            sync = "enter_" + s.name + "_via_" + t.src.name + "_in_" + s.parent.name + "?")
        add_assign(ta, newt, t.effect)
        p.addTransition(newt)
        
    # Add Basic -> Exit transitions
    exittr = []
    for b in [s1 for s1 in s.getChildren() if s1.isBasic()]:
        for t in sm.findTransitions(src=b, dst=None):
            if t.dst in s.getChildren() and t.dst.isExit():
                exittr.append(t)
    for t in exittr:
        c = Channel("exit_" + s.name, "h", False)
        ta.addChannel(c)
        newt = Transition(p.locations[t.src.name + "_active_in_" + s.name], 
                            p.locations[s.name + "_idle"], 
                            guard = t.guard,
                            sync = "exit_" + s.name + "?")
        p.addTransition(newt)
        
    exitexittr = []
    child = s.getChildren()
    twoChild = []
    for c in child:
        twoChild.extend(c.getChildren())
    for b in [s1 for s1 in twoChild if s1.isExit()]:
        for t in sm.findTransitions(src=b, dst=None):
            if t.dst in s.getChildren() and t.dst.isExit():
                exitexittr.append(t)
    for t in exitexittr:
        c = Channel("exit_" + s.name, "h", False)
        ta.addChannel(c)
        newt = Transition(p.locations[t.src.parent.name + "_active_in_" + s.name], 
                            p.locations[s.name + "_idle"], 
                            guard = t.guard,
                            sync = "exit_" + s.name + "?")
        p.addTransition(newt)        
        
    add_exit_cascades(sm, ta, s, p)
    add_exit_guards(sm, ta, s, p)
    
def add_global_kickoff(sm, ta, root):
    ''' Initializes UML->UPPAAL translation'''
    allstates = sm.getAllChildren()
    kickoff = Process("Global_Kickoff")
    locations = []
    channels = []
    for s in allstates:
        if s.isComposite() and s.initial:
            l = Location(s.name + "_vertex", commit=True, invariant="true")
            locations.append(l)
            c = Channel("init_" + s.name, "h", False)
            ta.addChannel(c)
            channels.append(c)
    last_vertex = Location("end")
    last_vertex.oldname = "Main.Main"
    locations.append(last_vertex)
    locations[0].isinit = True
    for l in locations:
        kickoff.addLocation(l)
    for i in range(len(locations)-1):
        tr = Transition(locations[i], locations[i+1], sync=channels[i].name + "!")
        kickoff.addTransition(tr)
    ta.addProcess(kickoff)
     
# TODO: store triggers somewhere        
def main_block(stateMachine, triggers):
    ''' Converts a stateMachine to a TimedAutomaton '''
    sm = stateMachine
    # There can be several unrelated diagrams on the top level, all of them are converted to UPPAAL
    root = sm.getChildren()
 
    ta = TimedAutomaton()   
    
    '''for t in triggers:
        if t.type == 'signal':
            c = Channel(t.name, "b", False)
            ta.addChannel(c)'''
            #c2 = Channel(t.name + "_urg", "b", True)
            #ta.addChannel(c2)

    for t in stateMachine.transitions:
        if t.trigger:
            if t.trigger.type == 'timeout':
                if str(t.trigger.expression).find("self.c") != -1:
                    ta.addClock(t.src.name + "_timeout")                                    
        
    for v in sm.variables.values():
        if v.type == 'intvar':
            var = Variable('int', v.name, v.init_val, v.range[0], v.range[1])
            ta.addVariable(var)
        if v.type == 'boolvar':
            var = Variable('bool', v.name, v.init_val, 0, 1)
            ta.addVariable(var)
        if v.type == 'clockvar':
            ta.addClock(v.name)
        if v.type == 'signalvar':
            c = Channel(v.name, "b", False)
            ta.addChannel(c)
        
    add_global_kickoff(sm, ta, root)
    
    # Add Hurry if necessary
    
    toProcess = []
    toProcess += root
    while toProcess != []:
        s = toProcess[0]
        toProcess = toProcess[1:]
        print "Converting to UPPAAL automaton " + s.name + "..."
        toProcess += [p for p in s.getChildren() if p.isComposite()]
        p = Process(s.name + "_process")
        idle = Location(s.name + "_idle", commit=False, invariant="true")
        idle.isinit = True
        p.addLocation(idle)
        if s.isXor():
            process_xor(sm, ta, s, p)
        elif s.isAnd():
            process_and(sm, ta, s, p)
        ta.addProcess(p)
        
    return ta