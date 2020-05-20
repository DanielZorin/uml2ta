
import sys
from antlr3 import *
from antlr3.compat import set, frozenset
                 
class BoolConst:
	def __init__(self, b):
		self.const = b
	def __str__(self):
		return str(self.const).lower()
	def Rename(self, v1, v2):
		pass
		
class IntConst:
	def __init__(self, b):
		self.const = b
	def __str__(self):
		return str(self.const)
	def Rename(self, v1, v2):
		pass
		
class VarName:
	def __init__(self, b):
		self.const = b
	def __str__(self):
		return str(self.const)
	def Rename(self, v1, v2):
		if self.const == v1:
			self.const = v2

class AssignStatement:
	type = 'assign'
	def __init__(self, var_name, expr):
		self.var_name = var_name
		self.expr = expr
	def __str__(self):
		return str(self.var_name) + '=' + str(self.expr) + ';'
	def Rename(self, v1, v2):
		if self.var_name == v1:
			self.var_name = v2
		#Workaround for the case of manually created expressions
		if hasattr(self.expr, "Rename"):
			self.expr.Rename(v1, v2)
		
class RandomAssignStatement:
	type = 'randomassign'
	def __init__(self, var_name):
		self.var_name = var_name
	def __str__(self):
		return str(self.var_name) + '= random();'
	def Rename(self, v1, v2):
		if self.var_name == v1:
			self.var_name = v2

class SendSignalStatement:
	type = 'signal'
	def __init__(self, signal_name):
		self.signal_name = signal_name
	def __str__(self):
		return '!!' + self.signal_name + ';'
	def Rename(self, v1, v2):
		if self.signal_name == v1:
			self.signal_name = v2

class PlusOp:
	def __init__(self, ops):
		self.ops = ops # for instance, it self.ops could be [('+', 'a'), ('-', 'b')]
	def __str__(self):
		r =  ''.join(i[0] + str(i[1]) for i in self.ops)
		if r[0] == '+':
			r = r[1:]
		return '(' + r + ')'
	def Rename(self, v1, v2):
		for o in self.ops:
			o[1].Rename(v1, v2)
		
class MultOp:
	def __init__(self, ops):
		self.ops = ops # for instance, it self.ops could be ['a', 'b']
	def __str__(self):
		return '(' + '*'.join(str(i) for i in self.ops) + ')'
	def Rename(self, v1, v2):
		for o in self.ops:
			o.Rename(v1, v2)
		
class CompOp:
	def __init__(self, ops, sign):
		self.ops = ops
		self.sign = sign
	def __str__(self):
		return '(' + str(self.ops[0]) + str(self.sign) + str(self.ops[1]) + ')'
	def Rename(self, v1, v2):
		for o in self.ops:
			o.Rename(v1, v2)
		
class AndOp:
	def __init__(self, ops):
		self.ops = ops
	def __str__(self):
		return '(' + '&&'.join(str(i) for i in self.ops) + ')'
	def Rename(self, v1, v2):
		for o in self.ops:
			o.Rename(v1, v2)

class OrOp:
	def __init__(self, ops):
		self.ops = ops
	def __str__(self):
		return '(' + '||'.join(str(i) for i in self.ops) + ')'
	def Rename(self, v1, v2):
		for o in self.ops:
			o.Rename(v1, v2)

class ConditionalOp:
	def __init__(self, op1, op2, op3):
		(self.op1, self.op2, self.op3) = (op1, op2, op3)
	def __str__(self):
		return '(' + str(self.op1) + '?' + str(self.op2) + ':' + str(self.op3) + ')'
	def Rename(self, v1, v2):
		self.op1.Rename(v1, v2)
		self.op2.Rename(v1, v2)
		self.op3.Rename(v1, v2)



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
T__26=26
T__25=25
T__24=24
T__23=23
T__22=22
T__21=21
T__20=20
BOOLCONST=6
INT=5
ID=4
EOF=-1
T__9=9
T__8=8
T__19=19
WS=7
T__16=16
T__15=15
T__18=18
T__17=17
T__12=12
T__11=11
T__14=14
T__13=13
T__10=10

# token names
tokenNames = [
    "<invalid>", "<EOR>", "<DOWN>", "<UP>", 
    "ID", "INT", "BOOLCONST", "WS", "';'", "'='", "'!!'", "'('", "')'", 
    "'random()'", "'?'", "':'", "'+'", "'-'", "'*'", "'>'", "'<'", "'=='", 
    "'!='", "'>='", "'<='", "'||'", "'&&'"
]



class action_scope(object):
    def __init__(self):
        self.statements = None
class add_expr_scope(object):
    def __init__(self):
        self.l = None
class mult_expr_scope(object):
    def __init__(self):
        self.l = None
class comp_expr_scope(object):
    def __init__(self):
        self.l = None
class or_expr_scope(object):
    def __init__(self):
        self.l = None
class and_expr_scope(object):
    def __init__(self):
        self.l = None


class ActionParser(Parser):
    grammarFileName = "grammars/Action.g"
    antlr_version = version_str_to_tuple("3.1.1")
    antlr_version_str = "3.1.1"
    tokenNames = tokenNames

    def __init__(self, input, state=None):
        if state is None:
            state = RecognizerSharedState()

        Parser.__init__(self, input, state)



	self.action_stack = []
	self.add_expr_stack = []
	self.mult_expr_stack = []
	self.comp_expr_stack = []
	self.or_expr_stack = []
	self.and_expr_stack = []





                


        



    # $ANTLR start "action"
    # grammars/Action.g:148:1: action returns [r] : assign_statement ( ';' assign_statement )* ( ';' )? EOF ;
    def action(self, ):
        self.action_stack.append(action_scope())
        r = None

        try:
            try:
                # grammars/Action.g:153:2: ( assign_statement ( ';' assign_statement )* ( ';' )? EOF )
                # grammars/Action.g:154:2: assign_statement ( ';' assign_statement )* ( ';' )? EOF
                pass 
                #action start
                  
                self.action_stack[-1].statements= []
                 
                #action end
                self._state.following.append(self.FOLLOW_assign_statement_in_action68)
                self.assign_statement()

                self._state.following.pop()
                # grammars/Action.g:157:19: ( ';' assign_statement )*
                while True: #loop1
                    alt1 = 2
                    LA1_0 = self.input.LA(1)

                    if (LA1_0 == 8) :
                        LA1_1 = self.input.LA(2)

                        if (LA1_1 == ID or LA1_1 == 10) :
                            alt1 = 1




                    if alt1 == 1:
                        # grammars/Action.g:157:20: ';' assign_statement
                        pass 
                        self.match(self.input, 8, self.FOLLOW_8_in_action71)
                        self._state.following.append(self.FOLLOW_assign_statement_in_action73)
                        self.assign_statement()

                        self._state.following.pop()


                    else:
                        break #loop1


                # grammars/Action.g:157:43: ( ';' )?
                alt2 = 2
                LA2_0 = self.input.LA(1)

                if (LA2_0 == 8) :
                    alt2 = 1
                if alt2 == 1:
                    # grammars/Action.g:157:43: ';'
                    pass 
                    self.match(self.input, 8, self.FOLLOW_8_in_action77)



                #action start
                                                                
                r = self.action_stack[-1].statements
                 
                #action end
                self.match(self.input, EOF, self.FOLLOW_EOF_in_action82)




                        
            except RecognitionException, e:
               raise
        finally:

            self.action_stack.pop()
            pass

        return r

    # $ANTLR end "action"


    # $ANTLR start "assign_statement"
    # grammars/Action.g:162:1: assign_statement : (var= ID '=' op= expr | ( ( '!!' i= ID ) | ( '!!' '(' i= ID ')' ) ) | var= ID '=' 'random()' );
    def assign_statement(self, ):

        var = None
        i = None
        op = None


        try:
            try:
                # grammars/Action.g:162:18: (var= ID '=' op= expr | ( ( '!!' i= ID ) | ( '!!' '(' i= ID ')' ) ) | var= ID '=' 'random()' )
                alt4 = 3
                LA4_0 = self.input.LA(1)

                if (LA4_0 == ID) :
                    LA4_1 = self.input.LA(2)

                    if (LA4_1 == 9) :
                        LA4_3 = self.input.LA(3)

                        if (LA4_3 == 13) :
                            alt4 = 3
                        elif ((ID <= LA4_3 <= BOOLCONST) or LA4_3 == 11 or (16 <= LA4_3 <= 17)) :
                            alt4 = 1
                        else:
                            nvae = NoViableAltException("", 4, 3, self.input)

                            raise nvae

                    else:
                        nvae = NoViableAltException("", 4, 1, self.input)

                        raise nvae

                elif (LA4_0 == 10) :
                    alt4 = 2
                else:
                    nvae = NoViableAltException("", 4, 0, self.input)

                    raise nvae

                if alt4 == 1:
                    # grammars/Action.g:163:2: var= ID '=' op= expr
                    pass 
                    var=self.match(self.input, ID, self.FOLLOW_ID_in_assign_statement95)
                    self.match(self.input, 9, self.FOLLOW_9_in_assign_statement97)
                    self._state.following.append(self.FOLLOW_expr_in_assign_statement101)
                    op = self.expr()

                    self._state.following.pop()
                    #action start
                    self.action_stack[-1].statements.append(AssignStatement(var.text, op))
                    #action end


                elif alt4 == 2:
                    # grammars/Action.g:164:2: ( ( '!!' i= ID ) | ( '!!' '(' i= ID ')' ) )
                    pass 
                    # grammars/Action.g:164:2: ( ( '!!' i= ID ) | ( '!!' '(' i= ID ')' ) )
                    alt3 = 2
                    LA3_0 = self.input.LA(1)

                    if (LA3_0 == 10) :
                        LA3_1 = self.input.LA(2)

                        if (LA3_1 == ID) :
                            alt3 = 1
                        elif (LA3_1 == 11) :
                            alt3 = 2
                        else:
                            nvae = NoViableAltException("", 3, 1, self.input)

                            raise nvae

                    else:
                        nvae = NoViableAltException("", 3, 0, self.input)

                        raise nvae

                    if alt3 == 1:
                        # grammars/Action.g:164:3: ( '!!' i= ID )
                        pass 
                        # grammars/Action.g:164:3: ( '!!' i= ID )
                        # grammars/Action.g:164:4: '!!' i= ID
                        pass 
                        self.match(self.input, 10, self.FOLLOW_10_in_assign_statement110)
                        i=self.match(self.input, ID, self.FOLLOW_ID_in_assign_statement114)





                    elif alt3 == 2:
                        # grammars/Action.g:164:15: ( '!!' '(' i= ID ')' )
                        pass 
                        # grammars/Action.g:164:15: ( '!!' '(' i= ID ')' )
                        # grammars/Action.g:164:16: '!!' '(' i= ID ')'
                        pass 
                        self.match(self.input, 10, self.FOLLOW_10_in_assign_statement118)
                        self.match(self.input, 11, self.FOLLOW_11_in_assign_statement120)
                        i=self.match(self.input, ID, self.FOLLOW_ID_in_assign_statement124)
                        self.match(self.input, 12, self.FOLLOW_12_in_assign_statement126)






                    #action start
                    self.action_stack[-1].statements.append(SendSignalStatement(i.text))
                    #action end


                elif alt4 == 3:
                    # grammars/Action.g:165:2: var= ID '=' 'random()'
                    pass 
                    var=self.match(self.input, ID, self.FOLLOW_ID_in_assign_statement137)
                    self.match(self.input, 9, self.FOLLOW_9_in_assign_statement139)
                    self.match(self.input, 13, self.FOLLOW_13_in_assign_statement141)
                    #action start
                    self.action_stack[-1].statements.append(RandomAssignStatement(var.text))
                    #action end



                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return 

    # $ANTLR end "assign_statement"


    # $ANTLR start "expr"
    # grammars/Action.g:167:1: expr returns [a] : op1= add_expr ( '?' op2= add_expr ':' op3= add_expr )? ;
    def expr(self, ):

        a = None

        op1 = None

        op2 = None

        op3 = None


        try:
            try:
                # grammars/Action.g:167:18: (op1= add_expr ( '?' op2= add_expr ':' op3= add_expr )? )
                # grammars/Action.g:168:2: op1= add_expr ( '?' op2= add_expr ':' op3= add_expr )?
                pass 
                self._state.following.append(self.FOLLOW_add_expr_in_expr159)
                op1 = self.add_expr()

                self._state.following.pop()
                # grammars/Action.g:168:16: ( '?' op2= add_expr ':' op3= add_expr )?
                alt5 = 2
                LA5_0 = self.input.LA(1)

                if (LA5_0 == 14) :
                    alt5 = 1
                if alt5 == 1:
                    # grammars/Action.g:168:17: '?' op2= add_expr ':' op3= add_expr
                    pass 
                    self.match(self.input, 14, self.FOLLOW_14_in_expr163)
                    self._state.following.append(self.FOLLOW_add_expr_in_expr167)
                    op2 = self.add_expr()

                    self._state.following.pop()
                    self.match(self.input, 15, self.FOLLOW_15_in_expr169)
                    self._state.following.append(self.FOLLOW_add_expr_in_expr173)
                    op3 = self.add_expr()

                    self._state.following.pop()
                    #action start
                    a = ConditionalOp(op1, op2, op3)
                    #action end



                #action start
                a = {False: ConditionalOp(op1, op2, op3),  True: op1}[op2==None]
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "expr"


    # $ANTLR start "add_expr"
    # grammars/Action.g:170:1: add_expr returns [a] : (o= ( '+' | '-' ) )? e= mult_expr (o= ( '+' | '-' ) e= mult_expr )* ;
    def add_expr(self, ):
        self.add_expr_stack.append(add_expr_scope())
        a = None

        o = None
        e = None


        try:
            try:
                # grammars/Action.g:170:31: ( (o= ( '+' | '-' ) )? e= mult_expr (o= ( '+' | '-' ) e= mult_expr )* )
                # grammars/Action.g:171:2: (o= ( '+' | '-' ) )? e= mult_expr (o= ( '+' | '-' ) e= mult_expr )*
                pass 
                # grammars/Action.g:171:3: (o= ( '+' | '-' ) )?
                alt6 = 2
                LA6_0 = self.input.LA(1)

                if ((16 <= LA6_0 <= 17)) :
                    alt6 = 1
                if alt6 == 1:
                    # grammars/Action.g:171:3: o= ( '+' | '-' )
                    pass 
                    o = self.input.LT(1)
                    if (16 <= self.input.LA(1) <= 17):
                        self.input.consume()
                        self._state.errorRecovery = False

                    else:
                        mse = MismatchedSetException(None, self.input)
                        raise mse





                self._state.following.append(self.FOLLOW_mult_expr_in_add_expr207)
                e = self.mult_expr()

                self._state.following.pop()
                #action start
                self.add_expr_stack[-1].l = [({True: (lambda x:'+'), False: (lambda i:i.text)}[o==None](o), e)]
                #action end
                # grammars/Action.g:171:112: (o= ( '+' | '-' ) e= mult_expr )*
                while True: #loop7
                    alt7 = 2
                    LA7_0 = self.input.LA(1)

                    if ((16 <= LA7_0 <= 17)) :
                        alt7 = 1


                    if alt7 == 1:
                        # grammars/Action.g:171:113: o= ( '+' | '-' ) e= mult_expr
                        pass 
                        o = self.input.LT(1)
                        if (16 <= self.input.LA(1) <= 17):
                            self.input.consume()
                            self._state.errorRecovery = False

                        else:
                            mse = MismatchedSetException(None, self.input)
                            raise mse


                        self._state.following.append(self.FOLLOW_mult_expr_in_add_expr222)
                        e = self.mult_expr()

                        self._state.following.pop()
                        #action start
                        self.add_expr_stack[-1].l.append((o.text, e))
                        #action end


                    else:
                        break #loop7


                #action start
                a = {True: PlusOp(self.add_expr_stack[-1].l), False: self.add_expr_stack[-1].l[0][1]}[len(self.add_expr_stack[-1].l)>1]
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.add_expr_stack.pop()
            pass

        return a

    # $ANTLR end "add_expr"


    # $ANTLR start "mult_expr"
    # grammars/Action.g:173:1: mult_expr returns [a] : o= comp_expr ( '*' o= comp_expr )* ;
    def mult_expr(self, ):
        self.mult_expr_stack.append(mult_expr_scope())
        a = None

        o = None


        try:
            try:
                # grammars/Action.g:173:32: (o= comp_expr ( '*' o= comp_expr )* )
                # grammars/Action.g:174:2: o= comp_expr ( '*' o= comp_expr )*
                pass 
                self._state.following.append(self.FOLLOW_comp_expr_in_mult_expr246)
                o = self.comp_expr()

                self._state.following.pop()
                #action start
                self.mult_expr_stack[-1].l=[o]
                #action end
                # grammars/Action.g:174:34: ( '*' o= comp_expr )*
                while True: #loop8
                    alt8 = 2
                    LA8_0 = self.input.LA(1)

                    if (LA8_0 == 18) :
                        alt8 = 1


                    if alt8 == 1:
                        # grammars/Action.g:174:35: '*' o= comp_expr
                        pass 
                        self.match(self.input, 18, self.FOLLOW_18_in_mult_expr251)
                        self._state.following.append(self.FOLLOW_comp_expr_in_mult_expr255)
                        o = self.comp_expr()

                        self._state.following.pop()
                        #action start
                        self.mult_expr_stack[-1].l.append(o)
                        #action end


                    else:
                        break #loop8


                #action start
                a = {True: MultOp(self.mult_expr_stack[-1].l), False: self.mult_expr_stack[-1].l[0]}[len(self.mult_expr_stack[-1].l)>1]
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.mult_expr_stack.pop()
            pass

        return a

    # $ANTLR end "mult_expr"


    # $ANTLR start "comp_expr"
    # grammars/Action.g:176:1: comp_expr returns [a] : o= or_expr (sign= ( '>' | '<' | '==' | '!=' | '>=' | '<=' ) o= or_expr )? ;
    def comp_expr(self, ):
        self.comp_expr_stack.append(comp_expr_scope())
        a = None

        sign = None
        o = None


        try:
            try:
                # grammars/Action.g:176:32: (o= or_expr (sign= ( '>' | '<' | '==' | '!=' | '>=' | '<=' ) o= or_expr )? )
                # grammars/Action.g:177:2: o= or_expr (sign= ( '>' | '<' | '==' | '!=' | '>=' | '<=' ) o= or_expr )?
                pass 
                self._state.following.append(self.FOLLOW_or_expr_in_comp_expr279)
                o = self.or_expr()

                self._state.following.pop()
                #action start
                self.comp_expr_stack[-1].l=[o]
                #action end
                # grammars/Action.g:177:32: (sign= ( '>' | '<' | '==' | '!=' | '>=' | '<=' ) o= or_expr )?
                alt9 = 2
                LA9_0 = self.input.LA(1)

                if ((19 <= LA9_0 <= 24)) :
                    alt9 = 1
                if alt9 == 1:
                    # grammars/Action.g:177:33: sign= ( '>' | '<' | '==' | '!=' | '>=' | '<=' ) o= or_expr
                    pass 
                    sign = self.input.LT(1)
                    if (19 <= self.input.LA(1) <= 24):
                        self.input.consume()
                        self._state.errorRecovery = False

                    else:
                        mse = MismatchedSetException(None, self.input)
                        raise mse


                    self._state.following.append(self.FOLLOW_or_expr_in_comp_expr302)
                    o = self.or_expr()

                    self._state.following.pop()
                    #action start
                    self.comp_expr_stack[-1].l.append(o)
                    #action end



                #action start
                a = {True: CompOp(self.comp_expr_stack[-1].l, sign.text if sign else None), False: self.comp_expr_stack[-1].l[0]}[len(self.comp_expr_stack[-1].l)>1]
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.comp_expr_stack.pop()
            pass

        return a

    # $ANTLR end "comp_expr"


    # $ANTLR start "or_expr"
    # grammars/Action.g:180:1: or_expr returns [a] : o= and_expr ( '||' o= and_expr )* ;
    def or_expr(self, ):
        self.or_expr_stack.append(or_expr_scope())
        a = None

        o = None


        try:
            try:
                # grammars/Action.g:180:30: (o= and_expr ( '||' o= and_expr )* )
                # grammars/Action.g:181:2: o= and_expr ( '||' o= and_expr )*
                pass 
                self._state.following.append(self.FOLLOW_and_expr_in_or_expr328)
                o = self.and_expr()

                self._state.following.pop()
                #action start
                self.or_expr_stack[-1].l=[o]
                #action end
                # grammars/Action.g:181:31: ( '||' o= and_expr )*
                while True: #loop10
                    alt10 = 2
                    LA10_0 = self.input.LA(1)

                    if (LA10_0 == 25) :
                        alt10 = 1


                    if alt10 == 1:
                        # grammars/Action.g:181:32: '||' o= and_expr
                        pass 
                        self.match(self.input, 25, self.FOLLOW_25_in_or_expr333)
                        self._state.following.append(self.FOLLOW_and_expr_in_or_expr337)
                        o = self.and_expr()

                        self._state.following.pop()
                        #action start
                        self.or_expr_stack[-1].l.append(o)
                        #action end


                    else:
                        break #loop10


                #action start
                a = {True: OrOp(self.or_expr_stack[-1].l), False: self.or_expr_stack[-1].l[0]}[len(self.or_expr_stack[-1].l)>1]
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.or_expr_stack.pop()
            pass

        return a

    # $ANTLR end "or_expr"


    # $ANTLR start "and_expr"
    # grammars/Action.g:183:1: and_expr returns [a] : o= atom ( '&&' o= atom )* ;
    def and_expr(self, ):
        self.and_expr_stack.append(and_expr_scope())
        a = None

        o = None


        try:
            try:
                # grammars/Action.g:183:31: (o= atom ( '&&' o= atom )* )
                # grammars/Action.g:184:2: o= atom ( '&&' o= atom )*
                pass 
                self._state.following.append(self.FOLLOW_atom_in_and_expr362)
                o = self.atom()

                self._state.following.pop()
                #action start
                self.and_expr_stack[-1].l=[o]
                #action end
                # grammars/Action.g:184:28: ( '&&' o= atom )*
                while True: #loop11
                    alt11 = 2
                    LA11_0 = self.input.LA(1)

                    if (LA11_0 == 26) :
                        alt11 = 1


                    if alt11 == 1:
                        # grammars/Action.g:184:29: '&&' o= atom
                        pass 
                        self.match(self.input, 26, self.FOLLOW_26_in_and_expr367)
                        self._state.following.append(self.FOLLOW_atom_in_and_expr371)
                        o = self.atom()

                        self._state.following.pop()
                        #action start
                        self.and_expr_stack[-1].l.append(o)
                        #action end


                    else:
                        break #loop11


                #action start
                a = {True: AndOp(self.and_expr_stack[-1].l), False: self.and_expr_stack[-1].l[0]}[len(self.and_expr_stack[-1].l)>1]
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.and_expr_stack.pop()
            pass

        return a

    # $ANTLR end "and_expr"


    # $ANTLR start "atom"
    # grammars/Action.g:186:1: atom returns [a] : ( (o1= ID ) | (o2= INT ) | (o3= BOOLCONST ) | ( '(' o4= expr ')' ) );
    def atom(self, ):

        a = None

        o1 = None
        o2 = None
        o3 = None
        o4 = None


        try:
            try:
                # grammars/Action.g:186:17: ( (o1= ID ) | (o2= INT ) | (o3= BOOLCONST ) | ( '(' o4= expr ')' ) )
                alt12 = 4
                LA12 = self.input.LA(1)
                if LA12 == ID:
                    alt12 = 1
                elif LA12 == INT:
                    alt12 = 2
                elif LA12 == BOOLCONST:
                    alt12 = 3
                elif LA12 == 11:
                    alt12 = 4
                else:
                    nvae = NoViableAltException("", 12, 0, self.input)

                    raise nvae

                if alt12 == 1:
                    # grammars/Action.g:187:2: (o1= ID )
                    pass 
                    # grammars/Action.g:187:2: (o1= ID )
                    # grammars/Action.g:187:3: o1= ID
                    pass 
                    o1=self.match(self.input, ID, self.FOLLOW_ID_in_atom392)
                    #action start
                    a=VarName(o1.text)
                    #action end





                elif alt12 == 2:
                    # grammars/Action.g:187:33: (o2= INT )
                    pass 
                    # grammars/Action.g:187:33: (o2= INT )
                    # grammars/Action.g:187:34: o2= INT
                    pass 
                    o2=self.match(self.input, INT, self.FOLLOW_INT_in_atom402)
                    #action start
                    a=IntConst(o2.text)
                    #action end





                elif alt12 == 3:
                    # grammars/Action.g:187:66: (o3= BOOLCONST )
                    pass 
                    # grammars/Action.g:187:66: (o3= BOOLCONST )
                    # grammars/Action.g:187:67: o3= BOOLCONST
                    pass 
                    o3=self.match(self.input, BOOLCONST, self.FOLLOW_BOOLCONST_in_atom412)
                    #action start
                    a=BoolConst(o3.text == "true")
                    #action end





                elif alt12 == 4:
                    # grammars/Action.g:187:116: ( '(' o4= expr ')' )
                    pass 
                    # grammars/Action.g:187:116: ( '(' o4= expr ')' )
                    # grammars/Action.g:187:117: '(' o4= expr ')'
                    pass 
                    self.match(self.input, 11, self.FOLLOW_11_in_atom420)
                    self._state.following.append(self.FOLLOW_expr_in_atom424)
                    o4 = self.expr()

                    self._state.following.pop()
                    self.match(self.input, 12, self.FOLLOW_12_in_atom426)
                    #action start
                    a=o4
                    #action end






                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "atom"


    # $ANTLR start "send_signal_statement"
    # grammars/Action.g:189:1: send_signal_statement : ( ( '!!' i= ID ) | ( '!!' '(' i= ID ')' ) );
    def send_signal_statement(self, ):

        i = None

        try:
            try:
                # grammars/Action.g:189:23: ( ( '!!' i= ID ) | ( '!!' '(' i= ID ')' ) )
                alt13 = 2
                LA13_0 = self.input.LA(1)

                if (LA13_0 == 10) :
                    LA13_1 = self.input.LA(2)

                    if (LA13_1 == ID) :
                        alt13 = 1
                    elif (LA13_1 == 11) :
                        alt13 = 2
                    else:
                        nvae = NoViableAltException("", 13, 1, self.input)

                        raise nvae

                else:
                    nvae = NoViableAltException("", 13, 0, self.input)

                    raise nvae

                if alt13 == 1:
                    # grammars/Action.g:190:2: ( '!!' i= ID )
                    pass 
                    # grammars/Action.g:190:2: ( '!!' i= ID )
                    # grammars/Action.g:190:3: '!!' i= ID
                    pass 
                    self.match(self.input, 10, self.FOLLOW_10_in_send_signal_statement439)
                    i=self.match(self.input, ID, self.FOLLOW_ID_in_send_signal_statement443)





                elif alt13 == 2:
                    # grammars/Action.g:190:14: ( '!!' '(' i= ID ')' )
                    pass 
                    # grammars/Action.g:190:14: ( '!!' '(' i= ID ')' )
                    # grammars/Action.g:190:15: '!!' '(' i= ID ')'
                    pass 
                    self.match(self.input, 10, self.FOLLOW_10_in_send_signal_statement447)
                    self.match(self.input, 11, self.FOLLOW_11_in_send_signal_statement449)
                    i=self.match(self.input, ID, self.FOLLOW_ID_in_send_signal_statement453)
                    self.match(self.input, 12, self.FOLLOW_12_in_send_signal_statement455)



                    #action start
                    self.action_stack[-1].statements.append(SendSignalStatement(i.text))
                    #action end



                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return 

    # $ANTLR end "send_signal_statement"


    # Delegated rules


 

    FOLLOW_assign_statement_in_action68 = frozenset([8])
    FOLLOW_8_in_action71 = frozenset([4, 10])
    FOLLOW_assign_statement_in_action73 = frozenset([8])
    FOLLOW_8_in_action77 = frozenset([])
    FOLLOW_EOF_in_action82 = frozenset([1])
    FOLLOW_ID_in_assign_statement95 = frozenset([9])
    FOLLOW_9_in_assign_statement97 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_expr_in_assign_statement101 = frozenset([1])
    FOLLOW_10_in_assign_statement110 = frozenset([4])
    FOLLOW_ID_in_assign_statement114 = frozenset([1])
    FOLLOW_10_in_assign_statement118 = frozenset([11])
    FOLLOW_11_in_assign_statement120 = frozenset([4])
    FOLLOW_ID_in_assign_statement124 = frozenset([12])
    FOLLOW_12_in_assign_statement126 = frozenset([1])
    FOLLOW_ID_in_assign_statement137 = frozenset([9])
    FOLLOW_9_in_assign_statement139 = frozenset([13])
    FOLLOW_13_in_assign_statement141 = frozenset([1])
    FOLLOW_add_expr_in_expr159 = frozenset([1, 14])
    FOLLOW_14_in_expr163 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_add_expr_in_expr167 = frozenset([15])
    FOLLOW_15_in_expr169 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_add_expr_in_expr173 = frozenset([1])
    FOLLOW_set_in_add_expr198 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_mult_expr_in_add_expr207 = frozenset([1, 16, 17])
    FOLLOW_set_in_add_expr214 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_mult_expr_in_add_expr222 = frozenset([1, 16, 17])
    FOLLOW_comp_expr_in_mult_expr246 = frozenset([1, 18])
    FOLLOW_18_in_mult_expr251 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_comp_expr_in_mult_expr255 = frozenset([1, 18])
    FOLLOW_or_expr_in_comp_expr279 = frozenset([1, 19, 20, 21, 22, 23, 24])
    FOLLOW_set_in_comp_expr286 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_or_expr_in_comp_expr302 = frozenset([1])
    FOLLOW_and_expr_in_or_expr328 = frozenset([1, 25])
    FOLLOW_25_in_or_expr333 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_and_expr_in_or_expr337 = frozenset([1, 25])
    FOLLOW_atom_in_and_expr362 = frozenset([1, 26])
    FOLLOW_26_in_and_expr367 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_atom_in_and_expr371 = frozenset([1, 26])
    FOLLOW_ID_in_atom392 = frozenset([1])
    FOLLOW_INT_in_atom402 = frozenset([1])
    FOLLOW_BOOLCONST_in_atom412 = frozenset([1])
    FOLLOW_11_in_atom420 = frozenset([4, 5, 6, 11, 16, 17])
    FOLLOW_expr_in_atom424 = frozenset([12])
    FOLLOW_12_in_atom426 = frozenset([1])
    FOLLOW_10_in_send_signal_statement439 = frozenset([4])
    FOLLOW_ID_in_send_signal_statement443 = frozenset([1])
    FOLLOW_10_in_send_signal_statement447 = frozenset([11])
    FOLLOW_11_in_send_signal_statement449 = frozenset([4])
    FOLLOW_ID_in_send_signal_statement453 = frozenset([12])
    FOLLOW_12_in_send_signal_statement455 = frozenset([1])



       
def main(argv, otherArg=None):
	from ActionLexer import ActionLexer
	char_stream = ANTLRFileStream(sys.argv[1])
	lexer = ActionLexer(char_stream)
	tokens = CommonTokenStream(lexer)
	parser = ActionParser(tokens);
	print parser.action()


if __name__ == '__main__':
    main(sys.argv)
