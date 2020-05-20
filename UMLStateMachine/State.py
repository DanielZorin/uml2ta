import copy
        
class State:
    ''' UML state
    
    :param name: state name'''
    initial = False
    states = []
    code = None
    
    def __init__(self, name):
        self.name = name
        self.initial = False
        self.parent = None
        self.states = []
        self.invariant = None
        
    def setParent(self, parent):
        ''' Sets parent state'''
        self.parent = parent
        
    def setInitial(self):
        ''' Make this state and all its parents initial'''
        self.initial = True
        p = self.parent
        while isinstance(p, State):
            p.initial = True
            p = p.parent
            
    def setInvariant(self, inv):
        ''' Sets an invariant'''
        self.invariant = inv

    def setCode(self, code):
        ''' Sets the executable code, also used for submachine parameters'''
        self.code = code
            
    def getChildren(self):
        ''' Returns all immediate children of this state'''
        return self.states
    
    def getAllChildren(self):
        ''' Returns all children, including indirect'''
        res = [s for s in self.states]
        for s in self.states:
            res += s.getAllChildren()
        return res
        
    def __str__(self):
        if self.name:
            name = self.name
        else:
            name = '[Unnamed]'
        return self.__class__.__name__  + ' ' + name
    
    def isXor(self):
        ''' This function is reimplemented in the appropriate subclasses'''
        return False
    
    def isAnd(self):
        ''' This function is reimplemented in the appropriate subclasses'''
        return False
    
    def isBasic(self):
        ''' This function is reimplemented in the appropriate subclasses'''
        return False
    
    def isEntry(self):
        ''' This function is reimplemented in the appropriate subclasses'''
        return False
    
    def isExit(self):
        ''' This function is reimplemented in the appropriate subclasses'''
        return False
    
    def isComposite(self):
        ''' This function is reimplemented in the appropriate subclasses'''
        return False
    
    def getFullName(self):
        ''' Returns a full name including all parent states'''
        ret = []
        node = self
        while 1: 
            ret = [str(node)] + ret
            if isinstance(node, State):
                node = node.parent
            else:
                break 
        return '::'.join(['('+s+')' for s in ret])
    
    def getCopy(self):
        ''' Copies the state'''
        news = copy.copy(self)
        news.states = []
        comp = {}
        for s in self.states:
            tmp = s.getCopy()
            news.states.append(tmp[0])
            for k in tmp[1].keys():
                comp[k] = tmp[1][k]
        for s in news.getChildren():
            s.setParent(news)
        news.invariant = copy.deepcopy(self.invariant)
        comp[self] = news
        return (news, comp)
        

class SimpleState(State):
    ''' Basic UML state'''       
    def isBasic(self):
        return True

class AggregateState(State):
    ''' Container state'''
    def __init__(self, name):
        State.__init__(self, name)
        
    def addState(self, state):
        ''' Adds a child'''
        self.states.append(state)
    
    def isComposite(self):
        return True

class CompositeState(AggregateState):
    ''' XOR state'''
    def __init__(self, name):
        AggregateState.__init__(self, name)
        
    def isXor(self):
        return True

class ConcurrentCompositeState(AggregateState):
    ''' AND state'''
    def __init__(self, name):
        AggregateState.__init__(self, name)
    
    def isAnd(self):
        return True
             
        
class ConcurrentRegion(CompositeState):
    ''' Region of an AND state'''
    def __init__(self, name):
        CompositeState.__init__(self, name)

class JunctionState(SimpleState):
    ''' Junction, uninterpreted'''
    pass

class ChoiceState(SimpleState):
    ''' Choice, uninterpreted'''
    pass
    
class ForkState(SimpleState):
    ''' Fork, uninterpreted'''
    pass

class JoinState(SimpleState):
    ''' Join, uninterpreted'''
    pass

class InitialState(State):
    def isEntry(self):
        return True

class FinalState(State): 
    ''' Exit state'''   
    def isExit(self):
        return True
    
class ShallowHistoryState(State):
    pass

class DeepHistoryState(State):
    pass

class SubMachineState(AggregateState):
    ''' Reference to a submachine'''
    def __init__(self, name):
        AggregateState.__init__(self, name)
        
    def setReferenceStateMachine(self, statemachine):
        self.statemachine = statemachine

class StubState(State):
    ''' Reference to a state in the submachine'''
    def __init__(self, name):
        State.__init__(self, name)
        self.ref_state = None
        
    def setReferenceState(self, state):
        self.ref_state = state
        
    def getFullName(self):
        return State.getFullName(self) + '<' + str(self.ref_state) + '>'