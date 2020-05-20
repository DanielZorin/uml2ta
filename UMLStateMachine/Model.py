# -*- coding: utf-8 -*-
#
# IR representation of UML state machines plus a parser.
#
# This module requires OrderedDict introduced in python 2.7, the backport
# to the versions 2.4-27 are located there:
#
# http://pypi.python.org/pypi/ordereddict/
#
# Peter Bulychev, 2011

import logging
import sys
import pdb
import re
import string
import antlr3
import xml.dom.minidom

from UMLStateMachine.Parsers import GuardParser, DeclarationsParser, ActionParser
from UMLStateMachine.xmiparser import xmiparser
from UMLStateMachine.Parsers.GuardParser import CompAtom, SumAtom, InAtom, OrAtom, AndAtom, Negation, BoolConst
from UMLStateMachine.Parsers.DeclarationsParser import IntVar, BoolVar, ClockVar, Macro
from UMLStateMachine.Parsers.ActionParser import AssignStatement, RandomAssignStatement, SendSignalStatement, PlusOp, MultOp, CompOp, AndOp, OrOp, ConditionalOp, BoolConst as ActionBoolConst, VarName, IntConst
from UMLStateMachine.errors import ZeroMatchingStatesException, SeveralMathcingStatesException, IncorrectStatesPathException

logging.basicConfig(level=logging.WARNING)
import_logger = logging.getLogger('Import from XMI') # TODO move to Model

from UMLStateMachine.State import *
from UMLStateMachine.Transition import *
from UMLStateMachine.StateMachine import *

class Model(HasVariables):
    ''' XMI model containing several :class:`~UMLStateMachine.StateMachine.StateMachine` instances'''
    def __init__(self):
        HasVariables.__init__(self)
        self.state_machines = {}
        
    def importFromXMI(self, fn):
        ''' Loads the model from XMI file'''
        self.xmimodel = xmiparser.parse(fn)    
        self.name = self.xmimodel.name
        self._buildStates()    
        self._referenceSubMachines()       
        self._referenceStubStates()    
        self._checkStateMachines()
        self._storeTriggers()
        self._readDeclarations()
        self._buildTransitions()
        self._buildInvariants()   
        self._checkSignals()
        self._checkStates()        
        self._checkTransitions()
        self._replaceIn()
        del self.xmimodel
            
    def _getStateClass(self, xmistate):
        return {  
                  xmiparser.XMICompositeState:              CompositeState,
                  xmiparser.XMIConcurrentCompositeState:    ConcurrentCompositeState,
                  xmiparser.XMIConcurrentRegion:            ConcurrentRegion,
                  xmiparser.XMISimpleState:                 SimpleState,
                  xmiparser.XMIForkState:                   ForkState,
                  xmiparser.XMIJoinState:                   JoinState,
                  xmiparser.XMIInitialState:                InitialState,
                  xmiparser.XMIFinalState:                  FinalState,
                  xmiparser.XMIStubState:                   StubState,
                  xmiparser.XMISubMachineState:             SubMachineState,
                  xmiparser.XMIJunctionState:               JunctionState,
                  xmiparser.XMIChoiceState:                 ChoiceState,
                  xmiparser.XMIShallowHistoryState:         ShallowHistoryState,
                  xmiparser.XMIDeepHistoryState:            DeepHistoryState
               }[type(xmistate)]
    
    # building states
    def _buildStates(self):
        self.xmi_id_map = {}
        self.xmi_id_map[self.xmimodel.id] = self
        self.sub_machines_to_update = []
        self.stub_states_to_update = []
        self.unnamed_state_machine_counter = 1
        self.unnamed_states_counter = 1
        for xmism in self.xmimodel.statemachines:
            name = xmism.name
            if not name:
                name = "UNNAMED_STATE_MACHINE_%d"%(self.unnamed_state_machine_counter)
                self.unnamed_state_machine_counter += 1
                import_logger.error("Unnamed state machine, renaming it to " + name)
            #TODO: parse identifier more precisely
            elif not name[0].isalpha() or name.find(' ') != -1:
                import_logger.error("State machine name " + name + " must be a correct identifier")

            sm = StateMachine(name)
            sm.setParent(self)
            self.state_machines[name] = sm
            self.xmi_id_map[xmism.getId()] = sm
            
            states_to_update = []
            state_names = set([])
            for xmistate in xmism.states:
                               
                state_class = self._getStateClass(xmistate) 
                state_name = xmistate.name
                
                if (not state_name):
                    state_name = "UNNAMED%d"%(self.unnamed_states_counter)
                    self.unnamed_states_counter += 1
                    if state_class in [SimpleState, CompositeState, ConcurrentCompositeState, SubMachineState]:
                        import_logger.error("Unnamed state in state machine \""+ sm.name +"\", renaming it to " + state_name)
                
                # TODO: parse identifier more precisely
                if state_name and ((not state_name[0].isalpha() and not state_name[0] == '@') or state_name.find(' ') != -1) :
                    import_logger.error("State name " + state_name + " in state machine " + sm.name + " must be a correct identifier")
                    
                if xmistate.name_container_id + state_name in state_names:
                    new_state_name = "UNNAMED_STATE_%d"%(self.unnamed_states_counter)
                    self.unnamed_states_counter += 1
                    import_logger.error("There are several states with the same name \"%s\" in state machine \"%s\", renaming the last one to \"%s\""%(state_name, sm.name, new_state_name))
                    state_name = new_state_name
                    
                state_names.add(xmistate.name_container_id + state_name)                     
                state = state_class(state_name)
                
                state.setInvariant(xmistate.invariant)
                state.setCode(xmistate.code)

                self.xmi_id_map[xmistate.getId()] = state
                states_to_update.append((state, xmistate))
                
                if isinstance(state, SubMachineState):
                    try:
                        self.sub_machines_to_update.append((state, xmistate.reference_statemachine_id))
                    except AttributeError:
                        import_logger.error("Sub Machine state \"%s\" is not referenced with any sub machine"%(state_name))
                if isinstance(state, StubState):
                    try:
                        self.stub_states_to_update.append((state, xmistate.reference_state_name))
                    except AttributeError:
                        import_logger.error("Stub state \"%s\" is not referenced with any state on the sub machine"%(state_name))
            
            for (state, xmistate) in states_to_update:
                parent = self.xmi_id_map[xmistate.parent_state_id]
                state.setParent(parent)
                parent.addState(state)
            
            del(states_to_update)        
    
    #referencing sub machines    
    def _referenceSubMachines(self):
        for (sm, id) in self.sub_machines_to_update:
            sm.setReferenceStateMachine(self.xmi_id_map[id])
            
        for sm in self.state_machines.values():
            for subm in [s for s in sm.getAllChildren() if isinstance(s, SubMachineState)]:
                subm.statemachine.globalScope = sm
               
    #referencing and checking stub states
    def _referenceStubStates(self):
        for (state, name) in self.stub_states_to_update:
            def get_state_by_name(composite_state, name):
                st = [s for s in composite_state.getAllChildren() if s.name == name]
                if len(st) > 1:
                    raise SeveralMathcingStatesException
                elif len(st) == 0:
                    raise ZeroMatchingStatesException
                return st[0]
            reference_sm = state.parent.statemachine            
            try: 
                #TODO: here SECTION2::ex2 is cut to "ex2". this might be buggy    
                if name.find("::") != -1:
                    stubname = name[name.find("::") + 2:]
                else:
                    stubname = name
                reference_state = get_state_by_name(reference_sm, stubname)
                state.setReferenceState(reference_state)
            except SeveralMathcingStatesException:
                import_logger.error("Several matching states named \"%s\" found in state machine \"%s\" for stubstate \"%s\""%(name, reference_sm.name, state.getFullName()))
            except ZeroMatchingStatesException:
                import_logger.error("No matching state named \"%s\" found in state machine \"%s\" for stubstate \"%s\""%(name, reference_sm.name, state.getFullName()))
        
    #checking state_machines
    def _checkStateMachines(self):
        sm_names = set([])
        for sm in self.state_machines.values():
            if sm.name in sm_names:                
                new_name = "UNNAMED_STATE_MACHINE_%d"%(self.unnamed_state_machine_counter)
                self.unnamed_state_machine_counter += 1
                import_logger.error("There are several statemachines with the same name \"%s\", renaming the last one to \"%s\""%(sm.name, new_name))
                sm.name = new_name
            sm_names.add(sm.name)
        
    # storing triggers
    def _storeTriggers(self):
        self.triggers= []
        trigger_names = set()
        self.receive_signal_names = set([])
        for xmitrigger in self.xmimodel.triggers:
            if isinstance(xmitrigger, xmiparser.XMITimeTrigger):
                trigger = TimeTrigger(xmitrigger.name, xmitrigger.expression)
            elif isinstance(xmitrigger, xmiparser.XMISignalTrigger):
                name = xmitrigger.name
                if name in trigger_names:
                    import_logger.error("Several signals exist with name \"%s\""%(name))
                trigger_names.add(name)
                trigger = SignalTrigger(xmitrigger.name) 
                self.receive_signal_names.add(xmitrigger.name)
            else:
                assert(0)
            self.triggers.append(trigger)
            self.xmi_id_map[xmitrigger.id] = trigger
    
    def _getVariables(self, body):
        decls = body.split('\n')
        macro = re.compile("#define ([a-zA-z0-9]*) (.*)")
        macros = []
        otherdecls = ""
        i = 0
        while i < len(decls):
            d = decls[i]
            m = macro.match(d)
            if m:
                expr = m.group(2)
                if expr.endswith("\\"):
                    tmp = expr
                    expr = expr.replace("\\", "")
                    while tmp.endswith("\\"):
                        i += 1
                        expr += decls[i].replace("\\", "")
                        tmp = decls[i]                         
                macros.append(Macro(m.group(1), expr))
            else:
                otherdecls += d
            i += 1
        return self._parseDeclarations(otherdecls) + macros        
        
    # reading declarations (comments)
    def _readDeclarations(self):
        for comment in self.xmimodel.comments:
            id = comment.annotated_element_id
            body = comment.body
            body_exc = comment.body.replace('\n', '\\n')
            if not self.xmi_id_map.has_key(id):
                import_logger.error("Comment \"%s\" (xmi-id=\"%s\") assigned to unknown entity" % (body_exc, id))
            else:
                try:
                    decls = self._getVariables(body)
                    if isinstance(self.xmi_id_map[id], HasVariables):
                        element = self.xmi_id_map[id]
                    else:
                        tmp = self.xmi_id_map[id]
                        while not isinstance(tmp, HasVariables):
                            tmp = tmp.parent
                        element = tmp
                    for var in decls:
                        if element.lookupVar(var.name):
                            import_logger.error("Ignoring duplicate variable \"%s\" in declaration section %s (xmi-id=\"%s\")" % (var.name, body_exc, id))
                            continue
                        element.addVariable(var)
                except antlr3.exceptions.RecognitionException, e:
                    import_logger.error("Can't parse comment \"%s\", got \"%s\"  (xmi-id=\"%s\")" % (body_exc, str(e), id))
        
        for comment in self.xmimodel.comments:
            id = comment.annotated_element_id
            if self.xmi_id_map.has_key(id):
                if isinstance(self.xmi_id_map[id], HasVariables):
                    element = self.xmi_id_map[id]
                else:
                    tmp = self.xmi_id_map[id]
                    while not isinstance(tmp, HasVariables):
                        tmp = tmp.parent
                    element = tmp
                for var in element.variables.values():
                    if element.globalScope:
                        if element.globalScope.lookupVar(var.name):
                            import_logger.error("Ignoring duplicate variable \"%s\" in declaration section %s (xmi-id=\"%s\")" % (var.name, body_exc, id))
                            element.removeVariable(var.name)              
        
    def _applyMacros(self, sm, s):
        res = s
        for v in sm.getAllMacros():
            res = res.replace(v.src, v.to)
        return res
           
    # building transitions
    def _buildTransitions(self):
        self.send_signal_names = set([])
        for xmism in self.xmimodel.statemachines:
            state_machine = self.xmi_id_map[xmism.getId()]
            for xmitransition in xmism.transitions:
                source = self.xmi_id_map[xmitransition.source_state_id]
                target = self.xmi_id_map[xmitransition.target_state_id]
                #TODO: check this
                if self.xmi_id_map.has_key(xmitransition.trigger_id):
                    trigger = self.xmi_id_map[xmitransition.trigger_id]
                else:
                    trigger = None
                effect_str = xmitransition.effect.replace('\n', '\\n')                
                guard_str = xmitransition.guard.replace("\n", "\\n")
                transition_str = str(Transition(source, target, trigger, guard_str, effect_str))
                if xmitransition.trigger_id:                
                    trigger = self.xmi_id_map[xmitransition.trigger_id]
                    if isinstance(trigger, TimeTrigger):
                        if isinstance(trigger.expression, unicode) or isinstance(trigger.expression, str):
                            # Workaround to avoid trying to parse the same trigger twice (it causes crash)
                            try:
                                trigger.expression = self._applyMacros(state_machine, trigger.expression)
                                expr = self._parseGuard(state_machine, trigger.expression, source.parent)
                                trigger.expression = expr
                            except antlr3.exceptions.RecognitionException, e:
                                import_logger.error("Can't parse timeout \"%s\", for transition \"%s\"  (xmi-id=\"%s\"): \"%s\"" % (trigger.expression, transition_str, xmitransition.id, str(e)))
                                effect = None                               
                else:
                    trigger = None                
                if xmitransition.effect != "":
                    try:
                        xmitransition.effect = self._applyMacros(state_machine, xmitransition.effect)
                        #print xmitransition.effect
                        effect = self._parseAction(state_machine, self._applyMacros(state_machine, xmitransition.effect))
                        #print "paarsed!"
                    except antlr3.exceptions.RecognitionException, e:
                        import_logger.error("Can't parse effect \"%s\", for transition \"%s\"  (xmi-id=\"%s\"): \"%s\"" % (xmitransition.effect, transition_str, xmitransition.id, str(e)))
                        effect = None
                else:
                    effect = None                
                if xmitransition.guard != "":
                    try:
                        container = source.parent
                        xmitransition.guard = self._applyMacros(state_machine, xmitransition.guard)
                        guard = self._parseGuard(state_machine, xmitransition.guard, container)
                        clearguard = []
                    except antlr3.exceptions.RecognitionException, e:
                        import_logger.error("Can't parse guard \"%s\", for transition \"%s\"  (xmi-id=\"%s\"): \"%s\"" % (xmitransition.guard, transition_str, xmitransition.id, str(e)))
                        guard = None
                else:
                    guard = None
                t = Transition(source, target, trigger, guard, effect)
                state_machine.addTransition(t)
    
    #checking signals
    def _checkSignals(self):
        a = self.receive_signal_names.difference(self.send_signal_names)
        b = self.send_signal_names.difference(self.receive_signal_names)
        if a:
            import_logger.error("Signals {%s} received but never sent" % (', '.join(list(a))))
        if b:
            import_logger.error("Signals {%s} sent but never received" % (', '.join(list(b))))
    
    # checking states
    def _checkStates(self):
        def _checkNestedStates(states):
            for state in states:
                if isinstance(state, AggregateState):
                    if len([s for s in state.states if isinstance(s, InitialState)]) > 1:
                        import_logger.error("Several initial states exist for composite state \"%s\""%(state.getFullName(), ))
                    _checkNestedStates(state.states)    
        for state_machine in self.state_machines.values():
            _checkNestedStates(state_machine.states)
    
    # checking transitions
    def _checkTransitions(self):
        for state_machine in self.state_machines.values():
            for transition in state_machine.transitions:
                if isinstance(transition.source, StubState) and isinstance(transition.source.ref_state, InitialState):
                    import_logger.error("Transition \"%s\" starts in StubStates that refers to InitialState"%(transition,))
                #if isinstance(transition.target, InitialState ):
                #    import_logger.error("Transition \"%s\" ends in InitialState"%(transition,))
                if isinstance(transition.target, StubState) and isinstance(transition.target.ref_state, FinalState):
                    import_logger.error("Transition \"%s\" ends in StubStates that refers to FinalState"%(transition,))
                if isinstance(transition.source, StubState) and isinstance(transition.source.ref_state, InitialState):
                    import_logger.error("Transition \"%s\" starts in StubStates that refers to InitialState"%(transition,))

    def _parseAction(self, sm, s):
        from UMLStateMachine.Parsers.ActionLexer  import ActionLexer
        from UMLStateMachine.Parsers.ActionParser import ActionParser
        sStream = antlr3.StringStream(s)
        lexer = ActionLexer(sStream)
        tStream = antlr3.CommonTokenStream(lexer)
        parser = ActionParser(tStream)
        statements = parser.action()
        ret_statements = []
        for statement in statements:            
            def analyze_expr(expr, type):
                assert(type in (int, bool))   
                # TODO: put BoolConst class into a common file?      
                if isinstance(expr, ActionBoolConst):
                    return (type == bool)
                if isinstance(expr, IntConst):
                    return (type == int)
                if isinstance(expr, VarName):
                    var = sm.lookupVar(str(expr))                    
                    if var==None:
                        import_logger.error("Unknown variable \"%s\" in assignment %s"%(expr, statement))
                    if type == int:
                        return isinstance(var, IntVar) or isinstance(var, ClockVar)
                    else:
                        return isinstance(var, BoolVar)
                if isinstance(expr, PlusOp):
                    if type==bool:
                        return False
                    else:
                        return all([analyze_expr(e[1], int) for e in expr.ops])
                if isinstance(expr, MultOp):
                    if type==bool:
                        return False
                    else:
                        return all([analyze_expr(e, int) for e in expr.ops])
                if isinstance(expr, CompOp):
                    if type==int:
                        return False
                    else:
                        return all([analyze_expr(e, int) for e in expr.ops])
                if isinstance(expr, AndOp) or isinstance(expr, OrOp):
                    if type==int:
                        return False
                    else:
                        return all([analyze_expr(e, bool) for e in expr.ops])
                if isinstance(expr, ConditionalOp):
                    return analyze_expr(expr.op1, bool) and analyze_expr(expr.op2, type) and analyze_expr(expr.op3, type)

            if isinstance(statement, SendSignalStatement):
                self.send_signal_names.add(statement.signal_name)
            elif isinstance(statement, AssignStatement):
                var = sm.lookupVar(statement.var_name)
                if var==None:
                    import_logger.error("Assignment to unknown variable: " + str(statement))
                    return None
                if isinstance(var, IntVar):
                    res = analyze_expr(statement.expr, int)
                elif isinstance(var, BoolVar):
                    res = analyze_expr(statement.expr, bool)
                elif isinstance(var, ClockVar):
                    res = analyze_expr(statement.expr, int)
                else:
                    assert(0)
                if not res:
                    import_logger.error("Wrong expr type in assignment: " + str(statement))
                    continue
            elif isinstance(statement, RandomAssignStatement):
                var = sm.lookupVar(statement.var_name)
                if var==None:
                    import_logger.error("Assignment to unknown variable: " + str(statement))
                    return None
                if isinstance(var, IntVar) or isinstance(var, BoolVar):
                    res = True
                else:
                    import_logger.error("Trying to assign a random variable to a clock variable: " + str(statement))
                    continue
            ret_statements.append(statement)        
        return ret_statements

    def _parseGuard(self, sm, guard_s, container):
        from UMLStateMachine.Parsers.GuardLexer  import GuardLexer
        from UMLStateMachine.Parsers.GuardParser import GuardParser
        sStream = antlr3.StringStream(guard_s)
        lexer = GuardLexer(sStream)
        tStream = antlr3.CommonTokenStream(lexer)
        parser = GuardParser(tStream)
        _guard = parser.guard()
        def check(lst):
            hasBool = False
            hasInt = False
            for var in lst:
                if isinstance(var, BoolConst):
                    hasBool = True
                elif isinstance(var, int):
                    hasInt = True
                else:                        
                    v = sm.lookupVar(var)
                    if var != "self.c" and not v:
                        import_logger.error("Can't find var \"%s\" in state machine \"%s\"" %(var, sm.name))
                    else:
                        if isinstance(v, BoolVar):
                            hasBool = True
                        else:
                            hasInt = True
            if hasBool and hasInt:
                return False, False
            return True, hasBool  
        def analyze(guard):
            result = True
            for atom in guard.disjunctions:
                if isinstance(atom, CompAtom):                 
                    r1 = check(atom.args[0].args) 
                    r2 = check(atom.args[1].args)
                    if not r1[0] or not r2[0] or r1[1] != r2[1]:
                        result = False
                elif isinstance(atom, OrAtom) or isinstance(atom, AndAtom) :                                 
                    result &= analyze(atom)
                elif isinstance(atom, InAtom):
                    pass
                elif isinstance(atom, Negation):
                    if isinstance(atom.arg, OrAtom):
                        result = analyze(atom.arg)
                    else:
                        r1 = check(atom.arg.args[0].args) 
                        r2 = check(atom.arg.args[1].args)
                        if not r1[0] or not r2[0] or r1[1] != r2[1]:
                            result = False                 
                else:
                    print atom, conj, guard_s
                    print atom.__class__
                    assert(0)
            return result
        if not analyze(_guard):
            import_logger.error("Comparing vars of different types in guard atom \"%s\"" %(str(_guard)))
                        
        return _guard

    def _parseDeclarations(self, s):
        from UMLStateMachine.Parsers.DeclarationsLexer  import DeclarationsLexer
        from UMLStateMachine.Parsers.DeclarationsParser import DeclarationsParser
        sStream = antlr3.StringStream(s)
        lexer = DeclarationsLexer(sStream)
        tStream = antlr3.CommonTokenStream(lexer)
        parser = DeclarationsParser(tStream)
        return parser.declarations()

    def _buildInvariants(self):
        for state_machine in self.state_machines.values():
            for state in state_machine.getAllChildren():
                if state.invariant:
                    state.invariant = state.invariant.replace("\n", "").replace("\t", "").replace("\r", "")
                    inv = re.compile("assume( )*\((.*)\)")
                    m = inv.match(state.invariant)
                    if m:
                        inv = m.group(2)
                        inv = self._applyMacros(state_machine, inv)
                        state.setInvariant(self._parseGuard(state_machine, inv, None))
                    else:
                        import_logger.error("Incorrect invariant: " + state.invariant)
                        state.setInvariant(None)

    def _replaceIn(self):
        def process(guard):
            if isinstance(guard, Negation):
                process(guard.arg)
            elif isinstance(guard, OrAtom):
                for g in guard.disjunctions:
                    process(g)
            elif isinstance(guard, AndAtom):
                clearguard = []
                for g in guard.disjunctions:
                    if not isinstance(g, InAtom):
                        process(g)
                        clearguard.append(g)
                    else:
                        name = g.state_path[len(g.state_path) - 1]
                        try:
                            st, st_machine = ((s, sm) for sm in self.state_machines.values() 
                                    for s in sm.getAllChildren() 
                                    if (s.name == name) or (sm.name + "." + s.name == name)).next()
                            if not st_machine.hasVariable(name):
                                var = IntVar("in_" + name.replace(".", "_"), (0, 1), 0)
                                st_machine.addVariable(var)
                            for t in st_machine.findTransitions(src=st, dst=None):
                                assign = AssignStatement("in_" + name.replace(".", "_"), "0")
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
                    
                            for t in st_machine.findTransitions(src=None, dst=st):
                                assign = AssignStatement("in_" + name.replace(".", "_"), "1")
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
                            clearguard.append("in_" + name.replace(".", "_") + " == 1")
                        except StopIteration:
                            import_logger.error("Can't find state from IN statement: \"%s\"" % name)
                guard.disjunctions = clearguard                  
        for state_machine in self.state_machines.values():
            for transition in state_machine.transitions:
                if transition.guard:
                    process(transition.guard)
                    
    def lookupState(self, path, container):
        def _lookupInCompositeState(state, path):
            if len(path) == 0:
                raise IncorrectStatesPathException
            else:
                if not hasattr(state, 'getStates') or not state.getStates().has_key(path[0]):
                    raise IncorrectStatesPathException
                if len(path) == 1:
                    return state.getStates()[path[0]]
                else:
                    return _lookupInCompositeState(state.getStates()[path[0]], path[1:])
        def _lookupStateAbs(path):
            if not self.state_machines.has_key(path[0]):
                raise IncorrectStatesPathException
            sm = self.state_machines[path[0]]
            return _lookupInCompositeState(sm, path[1:])
        
        try:
            return _lookupInCompositeState(container, path)
        except IncorrectStatesPathException:
            return _lookupStateAbs(path)
    
    def parseTransition(self, tr, src):
        guard = tr.getAttribute("cond")
        assign = tr.getAttribute("event")
        sync = None
        if tr.childNodes != []:
            sync = str(tr.childNodes[0].data)
        dst = tr.getAttribute("target")
        if dst == '':
            dst = src
        return (src, dst, guard, assign, sync)
        
    def parseStateNode(self, node, parent, initial):
        init = unicode(node.getAttribute("initial"))
        id = unicode(node.getAttribute("id"))
        children = []
        invariant = None
        for s in node.childNodes:
            if isinstance(s, xml.dom.minidom.Comment):
                self.comments.append(s.data)
            elif isinstance(s, xml.dom.minidom.Text):
                pass
            elif s.tagName == "state" or s.tagName == "parallel" or s.tagName == "final":
                tmp = self.parseStateNode(s, node, init)
                children.append(tmp)
                self.states.append(tmp)
            elif s.tagName == "transition":
                self.transitions.append(self.parseTransition(s, id))
            elif s.tagName == "onentry":
                invariant = s.childNodes[0].data

        if node.tagName == "scxml":
            return children
        
        if node.tagName == "state" and children == []:
            if initial == id:
                s = InitialState(id)
            else:
                s = SimpleState(id)
        elif node.tagName == "state" and children != []:
            s = CompositeState(id)
        elif node.tagName == "parallel":
            s = ConcurrentCompositeState(id)
        elif node.tagName == "final":
            s = FinalState(id)
            
        if invariant:
            s.setInvariant(invariant)
                    
        for c in children:
            s.addState(c)
            c.setParent(s)
            
        return s            
        
    def importFromScxml(self, filename):
        ''' Load model from SCXML file'''
        f = open(filename, "r")
        dom = xml.dom.minidom.parse(f)
        self.states = []
        self.transitions = []
        self.comments = []
        self.triggers = []
        self.send_signal_names = set([])
        for node in dom.childNodes:
            if node.tagName == "scxml":
                res = self.parseStateNode(node, None, None)
             
        sm = StateMachine(filename)
        for s in res:
            sm.addState(s)
            s.setParent(sm)
        self.state_machines[filename] = sm
        
        for comment in self.comments:
            try:
                decls = self._getVariables(comment)
                for var in decls:
                    if sm.lookupVar(var.name):
                        import_logger.error("Ignoring duplicate variable \"%s\" in declaration section %s (xmi-id=\"%s\")" % (var.name, body_exc, id))
                        continue
                    sm.addVariable(var)
            except antlr3.exceptions.RecognitionException, e:
                pass
                #import_logger.error("Can't parse comment \"%s\", got \"%s\"  (xmi-id=\"%s\")" % (comment, str(e), id))
  
        for t in self.transitions:
            source = (s for s in self.states if s.name == t[0]).next()
            target = (s for s in self.states if s.name == t[1]).next()
            trigger = t[4]
            effect_str = t[3].replace('\n', '\\n')                
            guard_str = t[2].replace("\n", "\\n")
            transition_str = str(Transition(source, target, trigger, guard_str, effect_str))
            if not trigger is None:  
                trigger = trigger.replace("\n", "").replace("\t", "").replace("\r", "")
                if trigger.startswith("after"):
                    af = re.compile("after( )*\((.*)\)")
                    m = af.match(trigger)
                    expr = self._parseGuard(sm, m.group(2), source.parent)
                    trigger = TimeTrigger("timeout", expr)
                    self.triggers.append(trigger)
                else:
                    af = re.compile("[a-zA-Z]([a-zA-Z0-9]|_)*")
                    m = af.match(trigger)
                    if m:
                        trigger = SignalTrigger(trigger)
                        if len(filter(lambda t: t.name == trigger, self.triggers)) == 0:
                            self.triggers.append(trigger)    
                    else:
                        trigger = None     
            if effect_str != "":
                try:
                    effect = self._parseAction(sm, self._applyMacros(sm, effect_str))
                except antlr3.exceptions.RecognitionException, e:
                    import_logger.error("Can't parse effect \"%s\", for transition \"%s\"  \"%s\"" % (effect_str, transition_str, str(e)))
                    effect = None
            else:
                effect = None                
            if guard_str != "":
                try:
                    container = source.parent
                    guard = self._parseGuard(sm, self._applyMacros(sm, guard_str), container)
                    clearguard = []
                except antlr3.exceptions.RecognitionException, e:
                    import_logger.error("Can't parse guard \"%s\", for transition \"%s\"  \"%s\"" % (guard_str, transition_str, str(e)))
                    guard = None
            else:
                guard = None
            t = Transition(source, target, trigger, guard, effect)
            sm.addTransition(t)
        
        self._buildInvariants()
        self._checkStates()        
        self._checkTransitions()
        self._replaceIn()
