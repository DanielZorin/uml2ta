class Variable:
    ''' UPPAAL variable
    
    :param vartype: variable type: only int and bool variables are supported.
    :param name: variable name
    :param init: initial value
    :param start: lower bound
    :param end: upper bound
    '''
    def __init__(self, vartype, name, init=0, start=0, end=1):
        self.name = name
        self.start = start
        self.end = end
        self.init = init
        self.vartype = vartype
        
    def __str__(self):
        if self.vartype == 'int':
            s = "int [" + str(self.start) + "," + str(self.end) + "] " + self.name + " = " + str(self.init) + ";"
        elif self.vartype == 'bool':
            s = "bool " + self.name + " = " + ("true" if self.init == 1 else "false") + ";"
        return s