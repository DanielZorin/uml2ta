Guard = str
Effect = str

class Trigger:
    pass

class TimeTrigger(Trigger):
    ''' Timer trigger, e.g. after(self.c > 5)'''
    type = 'timeout'
    
    def __init__(self, name, expression):
        self.expression = expression
        self.name = name
        
    def __str__(self):
        return "after(" + str(self.expression) + ")"

class SignalTrigger(Trigger):
    ''' Signal'''
    type = 'signal'
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return self.name

class Transition:
    ''' UML transition
    
    :param source: source state
    :param target: target state
    :param trigger: trigger instance
    :param guard: guard expression
    :param effect: effect expression
    :param urgency: urgency'''
    def __init__(self, source, target, trigger, guard, effect, urgency=False):
        self.source= source 
        self.target = target 
        self.trigger = trigger
        self.guard = guard
        self.effect = effect
        self.urgency = urgency
        # Provided for convenience and compatibility with UPPAAL.Transition
        self.src = source
        self.dst = target
        
    def __str__(self):
        return self.source.getFullName() + '->' + self.target.getFullName()
    
    def setSrc(self, s):
        self.source = s
        self.src = s
        
    def setDst(self, s):
        self.target = s
        self.dst = s