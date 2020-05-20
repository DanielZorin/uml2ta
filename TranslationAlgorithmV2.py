from UPPAAL.Location import Location
from UPPAAL.Process import Process
from UPPAAL.Transition import Transition
from UPPAAL.Channel import Channel
from UPPAAL.Variable import Variable
from UPPAAL.TimedAutomaton import TimedAutomaton
     
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
        
    # Add Hurry if necessary
    
    add_processes(sm, ta)
    ta.ClearUp()
    return ta

def add_processes(sm, ta):
    ''' Initializes UML->UPPAAL translation'''
    procs = {}
    for s in sm.getAllChildren():
        if s.isXor():
            proc = Process(s.name)
            idle = Location("idle")
            proc.addLocation(idle)
            process_substates(s, proc, sm, ta)
            add_init(s, proc, sm, ta)
            ta.addProcess(proc)
            procs[s] = proc
            
    for s in procs.keys():
        add_act_blocks(s, procs[s], sm, ta)
        process_transitions(s, procs[s], sm, ta)
        add_assignments(s, procs[s], sm, ta)

def process_substates(s, proc, sm, ta):
    for child in s.getChildren():
        if child.isAnd() or child.isBasic():
            l = Location(child.name + "_active")
            l.oldname = child.name
            if child.invariant:
                l.addInvariant(child.invariant)
            proc.addLocation(l)

def add_init(s, proc, sm, ta):
    if s.initial:
        inits = [p for p in s.getChildren() if p.initial]
        for l in proc.locations.values():
            for p in inits:
                if l.name == p.name + "_active":
                    l.isinit = True
    else:
        for l in proc.locations.values():
            if l.name == "idle":
                l.isinit = True

def add_act_blocks(s, proc, sm, ta):
    for ss in s.getChildren():
        if ss.isAnd():
            for e in ss.getChildren():
                if e.isEntry():
                     for t in sm.transitions:
                         if t.dst == e  and not t.src.isEntry():
                             add_act_block(e, ss, proc, sm, ta)

def up(s):
    if s.isBasic():
        return s
    else:
        return s.parent

def add_act_block(e, s, proc, sm, ta):
    l = Location(e.name + "_act")
    l.iscommit = True
    proc.addLocation(l)
    c = Channel(e.name + "_bact", "b", False)
    ta.addChannel(c)
    tr = Transition(l, proc.locations[s.name + "_active"], sync = c.name + "!")
    proc.addTransition(tr)
    #TODO: add invariant to l

    procset = make_act_set(e, sm, ta)
    for pair in procset:
        p = (q for q in ta.processes if q.name == pair[1].parent.name).next()
        upstate = up(pair[1])
        tr = Transition(p.locations["idle"], p.locations[upstate.name + "_active"], sync = c.name + "?")
        p.addTransition(tr)

def make_act_set(e, sm, ta):
    tree = make_act_tree(e, sm, ta)
    res = []
    for pair in tree:
        # Second part is arbitrary
        if pair[1].parent.isXor() and not pair[0].parent.isAnd():
            res.append(pair)
    return res

def make_act_tree(e, sm, ta):
    verts = set([e])
    edges = []
    todo = [e]
    while len(todo) > 0:
        s = todo[0]
        todo = todo[1:] 
        if s.isEntry():
            for t in sm.findTransitions(src = s):
                verts.add(t.dst)
                edges.append([t.src, t.dst])
                todo.append(t.dst)
        todo = list(set(todo))
    return edges

def make_deact_set(e, sm, ta):
    tree = make_deact_tree(e, sm, ta)[1]
    res = []
    for pair in tree:
        if pair[0].parent.isXor() and not pair[1].parent.isAnd():
            res.append(pair)
    return res

def make_deact_tree(e, sm, ta):
    verts = set([e])
    edges = []
    todo = [e]
    while len(todo) > 0:
        s = todo[0]
        todo = todo[1:]
        if s.isExit():
            for t in sm.findTransitions(dst = s):
                verts.add(t.dst)
                edges.append([t.src, t.dst])
                todo.append(t.src)
    return [list(verts), edges]
                
def add_deact_block(t, inv, vert, proc, sm, ta):
    s = t.src.parent
    l = Location(t.src.name + "_" + t.dst.name + "_deact")
    l.iscommit = True
    proc.addLocation(l)
    tree = make_deact_tree(t.src, sm, ta)
    newt = add_tr(ta, proc, proc.locations[s.name + "_active"], 
                       proc.locations[t.src.name + "_" + t.dst.name + "_deact"], 
                       t.guard, t.trigger, None)
    newt.addGuard(trig(t.src, tree, sm))
    
    c = Channel(t.src.name + "_bdeact", "b", False)
    ta.addChannel(c)
    tr = Transition(proc.locations[t.src.name + "_" + t.dst.name + "_deact"], vert, sync = c.name + "!")
    add_assign(tr, t.effect, ta)
    proc.addTransition(tr)

    procset = make_deact_set(t.src, sm, ta)
    for pair in procset:
        p = (q for q in ta.processes if q.name == pair[0].parent.name).next()
        upstate = up(pair[0])
        if upstate.parent.isAnd():
            upstate = upstate.parent
            p = (q for q in ta.processes if q.name == upstate.parent.name).next()
        tr = Transition(p.locations[upstate.name + "_active"], p.locations["idle"], sync = c.name + "?")
        p.addTransition(tr)

def process_transitions(s, proc, sm, ta):
    for t in sm.transitions:
        if ((t.src.isBasic() and t.src.parent == s) or (t.src.isExit() and t.src.parent.isAnd() and t.src.parent.parent == s)) \
            and ((t.dst.isBasic() and t.dst.parent == s) or (t.dst.isEntry() and t.dst.parent.isAnd() and t.dst.parent.parent == s)):
            if t.src.isBasic() and t.dst.isBasic():
                add_tr(ta, proc, proc.locations[t.src.name + "_active"], 
                       proc.locations[t.dst.name + "_active"], t.guard, t.trigger, t.effect)
            if t.src.isBasic() and t.dst.isEntry():
                add_tr(ta, proc, proc.locations[t.src.name + "_active"], 
                       proc.locations[t.dst.name + "_act"], t.guard, t.trigger, t.effect)
            # TODO: invariants
            if t.src.isExit() and t.dst.isBasic():
                add_deact_block(t, "", proc.locations[t.dst.name + "_active"], proc, sm, ta)
            if t.src.isExit() and t.dst.isEntry():
                add_deact_block(t, "", proc.locations[t.dst.name + "_act"], proc, sm, ta)

def add_assignments(s, proc, sm, ta):
    for ex in s.getChildren():
        if ex.isExit():
            sb = [t.src for t in sm.findTransitions(dst=ex) if t.src.parent == s]
            ton = []
            for t in sm.transitions:
                for ss in sb: 
                    if t.dst.name == ss.name + "_active":
                        found = False
                        for ss2 in sb:
                            if t.src.name == ss2.name + "_active":
                                found = True
                        if not found:
                            ton.append(t)
                        break
                        
            toff = []
            for t in sm.transitions:
                for ss in sb: 
                    if t.src.name == ss.name + "_active":
                        found = False
                        for ss2 in sb:
                            if t.dst.name == ss2.name + "_active":
                                found = True
                        if not found:
                            toff.append(t)
                        break
                        
            var = Variable('bool', ex.name + "_flag", 0, 0, 1)
            ta.addVariable(var)
            for t in ton:
                t.addAssign(var.name + " = 1")
            for t in toff:
                t.addAssign(var.name + " = 0")
    
def trig(ex, tree, sm):
    verts = tree[0]
    edges = tree[1]
    upstate = up(ex)
    if upstate.isAnd():
        result = "true"
        for e in edges:
            if e[0] == ex:
                result = result + " && " + trig(e[1], tree, sm)
        return result
    else:
        for e in edges:
            if e[0] == ex and e[1].isBasic():
                result = ex.name + "_flag == 1"
            else:
                result = "false"
        for e in edges:
            if e[0] == ex:
                upstate = up(e[1])
                if upstate.isAnd():
                    result = result + " || " + trig(e[1], tree, sm)
        return result

def add_tr(ta, p, source, target, g, syn, r):
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
    add_assign(t, r, ta)
    return t

def add_assign(t, r, ta):
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