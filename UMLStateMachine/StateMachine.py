import xml.dom.minidom
from UMLStateMachine.State import ConcurrentCompositeState, FinalState, InitialState

class HasVariables:
    ''' Intreface for an instance with variables'''
    def __init__(self):
        self.variables = {}
        self.globalScope = None
        
    def addVariable(self, var):
        self.variables[var.name] = var
        
    def removeVariable(self, name):
        del self.variables[name]
        
    def getVariable(self, name):
        if self.hasVariable(name):
            return self.variables[name]
        else:
            return None
        
    def hasVariable(self, name):
        return self.variables.has_key(name)

class StateMachine(HasVariables):
    ''' UML state machine
    
    :param name: state machine's name'''
    def __init__(self, name):
        HasVariables.__init__(self)
        self.name = name
        self.transitions = []
        self.states =  []
        self.parent = None
        
    def setParent(self, parent):
        ''' Sets the parent state'''
        self.parent = parent
        
    def addTransition(self, transition):
        ''' Add a :class:`UMLStateMachine.Transition.Transition`'''
        self.transitions.append(transition)
        
    def addState(self, state):
        ''' Add a :class:`UMLStateMachine.State.State`'''      
        self.states.append(state)
        
    def getChildren(self):
        # TODO: check if all statecharts in ArgoUML have 'top' states as their root
        return self.states[0].states
            
    def getAllChildren(self):
        res = [s for s in self.getChildren()]
        for s in self.getChildren():
            res += s.getAllChildren()
        return res
    
    def containsState(self, name):
        try:
            s = (st for st in self.getAllChildren() if st.name == name).next()
            return True
        except StopIteration:
            return False
    
    def findTransitions(self, src=None, dst=None):   
        return [t for t in self.transitions if (src == None or t.source == src) and (dst == None or t.target == dst)]
    
    def lookupVar(self, name):
        if self.hasVariable(name):
            return self.variables[name]
        else:
            if not self.parent is None and self.parent.hasVariable(name):
                return self.parent.variables[name]
            else:   
                if self.globalScope:
                    return self.globalScope.lookupVar(name)
                
    def getCopy(self):
        import copy
        newsm = StateMachine(self.name)
        newsm.variables = copy.deepcopy(self.variables)
        newsm.globalScope = self.globalScope
        newsm.parent = self.parent
        newsm.states = []
        newsm.transitions = []
        for t in self.transitions:
            tn = copy.copy(t)
            tn.trigger = copy.deepcopy(t.trigger)
            tn.guard = copy.deepcopy(t.guard)
            tn.effect = copy.deepcopy(t.effect)
            tn.urgency = copy.deepcopy(t.urgency)
            newsm.transitions.append(tn)
        comp = {}
        for s in self.states:
            tmp = s.getCopy()
            newsm.states.append(tmp[0])
            for k in tmp[1].keys():
                comp[k] = tmp[1][k]
        for s in newsm.getChildren():
            s.setParent(newsm)
        for t in newsm.transitions:
            t.setSrc(comp[t.src])
            t.setDst(comp[t.dst])
        return newsm
                
    def getAllMacros(self):
        res = [s for s in self.variables.values() if s.type == 'macro']
        if self.parent:
            res = res + [s for s in self.parent.variables.values() if s.type == 'macro']
        if self.globalScope:
            res = res + self.globalScope.getAllMacros()
        return res
        
    def getTransitionScxml(self, dom, t):
        node = dom.createElement("transition")
        if t.guard:
            node.setAttribute("cond", str(t.guard))
        if t.effect:
            node.setAttribute("event", ''.join([str(s) for s in t.effect]))
        if t.src != t.dst:
            node.setAttribute("target", t.dst.name)
        if t.trigger:
            signal = dom.createTextNode(str(t.trigger))
            node.appendChild(signal)
        return node
    
    def getStateScxml(self, dom, state):
        name = "state"
        if isinstance(state, ConcurrentCompositeState):
            name = "parallel"
        if isinstance(state, FinalState):
            name = "final"

        node = dom.createElement(name)
        node.setAttribute("id", state.name)
        if len(state.getChildren()) > 0:
            try:
                init = (s for s in state.getChildren() if isinstance(s, InitialState)).next()
                node.setAttribute("initial", init.name)
            except StopIteration:
                pass
        if state.invariant:
            onentry = dom.createElement("onentry")
            assume = dom.createTextNode("assume(" + str(state.invariant) + ")")
            onentry.appendChild(assume)
            node.appendChild(onentry)

        if state.code:
            node.setAttribute("code", state.code)
        tran = [t for t in self.transitions if t.src == state]
        for t in tran:
            node.appendChild(self.getTransitionScxml(dom, t))
        for c in state.getChildren():
            node.appendChild(self.getStateScxml(dom, c))
        if state.name.startswith("FED_"):
            for v in self.variables.values():
                par = dom.createElement("parametr")
                skip = False
                if v.type == 'intvar':                 
                    par.setAttribute("type", "int")
                    par.setAttribute("initval", str(v.init_val))
                elif v.type == 'boolvar':
                    par.setAttribute("type", "bool")
                    par.setAttribute("initval", str(int(v.init_val)))
                else:
                    skip = True
                par.setAttribute("name", v.name)
                if not skip:
		    pass
                    #node.appendChild(par)
        return node
             
    def exportToScxml(self):
        dom = xml.dom.minidom.Document()
        scxml = dom.createElement("scxml")
        dom.appendChild(scxml)
        vars = ""
        for v in self.variables.values():
            if v.type == 'intvar':
                vars += "int [%d..%d] %s = %d;\n" % (v.range[0], v.range[1], v.name, v.init_val)
            if v.type == 'boolvar':
                vars += "bool %s = %s;\n" % (v.name, str(v.init_val).lower())
            if v.type == 'clockvar':
                vars += "clock %s;\n" % (v.name)
        decl = dom.createComment(vars)
        scxml.appendChild(decl)
        for s in self.states:
            scxml.appendChild(self.getStateScxml(dom, s))
        return dom.toprettyxml()
