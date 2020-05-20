
import sys
from antlr3 import *
from antlr3.compat import set, frozenset
                 
import string

class BoolConst:
	def __init__(self, b):
		self.const = b
	def __str__(self):
		return str(self.const).lower()

class CompAtom:
	def __init__(self, arg1, op, arg2):
		self.args = [arg1, arg2]
		self.op = op
		
	def __str__(self):
		return str(self.args[0]) + self.op + str(self.args[1])
		
	def Rename(self, v1, v2):
		self.args[0].Rename(v1, v2)
		self.args[1].Rename(v1, v2)
		
class SumAtom:
	def __init__(self, a):
		self.args = a
		
	def __str__(self):
		return '+'.join([str(s) for s in self.args])
		
	def Rename(self, v1, v2):
		self.args = [s if s != v1 else v2 for s in self.args]

class OrAtom:
	def __init__(self, lst):
		self.disjunctions = lst
		
	def __str__(self):
		lst = []
		for s in self.disjunctions:
			lst.append(str(s))
		return '||'.join(lst)
	
	def Rename(self, v1, v2):
		for s in self.disjunctions:
			if hasattr(s, "Rename"):
				s.Rename(v1, v2)

class AndAtom:
	def __init__(self, lst):
		self.disjunctions = lst
		
	def __str__(self):
		lst = []
		for s in self.disjunctions:
			lst.append(str(s))
		return '&&'.join(['(' + str(v) + ')' for v in lst])
	
	def Rename(self, v1, v2):
		for s in self.disjunctions:
			if hasattr(s, "Rename"):
				s.Rename(v1, v2)
		
class Negation:
	def __init__(self, arg):
		self.arg = arg
		
	def __str__(self):
		return '!(' + str(self.arg) + ')'
		
	def Rename(self, v1, v2):
		self.arg.Rename(v1, v2)

class InAtom:
	def __init__(self, state_path):
		self.state_path = state_path
	def __str__(self):
		if  hasattr(self, 'state_path'):
			state_path = string.join(self.state_path, '.')
		else:
			state_path = '....' + self.state.name
		return 'in(' + state_path + ')'
	
	def Rename(self, v1, v2):
		pass



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
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
    "ID", "INT", "BOOLCONST", "WS", "'||'", "'&&'", "'('", "')'", "'=='", 
    "'!='", "'<'", "'>'", "'<='", "'>='", "'+'", "'in'", "'.'", "'!'"
]



class or_expr_scope(object):
    def __init__(self):
        self.l = None
class and_expr_scope(object):
    def __init__(self):
        self.l = None
class sum_scope(object):
    def __init__(self):
        self.l = None


class GuardParser(Parser):
    grammarFileName = "grammars/Guard.g"
    antlr_version = version_str_to_tuple("3.1.1")
    antlr_version_str = "3.1.1"
    tokenNames = tokenNames

    def __init__(self, input, state=None):
        if state is None:
            state = RecognizerSharedState()

        Parser.__init__(self, input, state)



	self.or_expr_stack = []
	self.and_expr_stack = []
	self.sum_stack = []





                


        



    # $ANTLR start "guard"
    # grammars/Guard.g:102:1: guard returns [r] : op= or_expr EOF ;
    def guard(self, ):

        r = None

        op = None


        try:
            try:
                # grammars/Guard.g:102:19: (op= or_expr EOF )
                # grammars/Guard.g:103:2: op= or_expr EOF
                pass 
                self._state.following.append(self.FOLLOW_or_expr_in_guard53)
                op = self.or_expr()

                self._state.following.pop()
                #action start
                r = op 
                #action end
                self.match(self.input, EOF, self.FOLLOW_EOF_in_guard57)




                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return r

    # $ANTLR end "guard"


    # $ANTLR start "or_expr"
    # grammars/Guard.g:105:1: or_expr returns [a] : op1= and_expr ( '||' op2= and_expr )* ;
    def or_expr(self, ):
        self.or_expr_stack.append(or_expr_scope())
        a = None

        op1 = None

        op2 = None


        try:
            try:
                # grammars/Guard.g:105:30: (op1= and_expr ( '||' op2= and_expr )* )
                # grammars/Guard.g:106:2: op1= and_expr ( '||' op2= and_expr )*
                pass 
                self._state.following.append(self.FOLLOW_and_expr_in_or_expr76)
                op1 = self.and_expr()

                self._state.following.pop()
                #action start
                self.or_expr_stack[-1].l = [op1]
                #action end
                # grammars/Guard.g:106:37: ( '||' op2= and_expr )*
                while True: #loop1
                    alt1 = 2
                    LA1_0 = self.input.LA(1)

                    if (LA1_0 == 8) :
                        alt1 = 1


                    if alt1 == 1:
                        # grammars/Guard.g:106:38: '||' op2= and_expr
                        pass 
                        self.match(self.input, 8, self.FOLLOW_8_in_or_expr81)
                        self._state.following.append(self.FOLLOW_and_expr_in_or_expr85)
                        op2 = self.and_expr()

                        self._state.following.pop()
                        #action start
                        self.or_expr_stack[-1].l.append(op2)
                        #action end


                    else:
                        break #loop1


                #action start
                a = OrAtom(self.or_expr_stack[-1].l) 
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.or_expr_stack.pop()
            pass

        return a

    # $ANTLR end "or_expr"


    # $ANTLR start "and_expr"
    # grammars/Guard.g:108:1: and_expr returns [a] : op1= disj ( '&&' op2= disj )* ;
    def and_expr(self, ):
        self.and_expr_stack.append(and_expr_scope())
        a = None

        op1 = None

        op2 = None


        try:
            try:
                # grammars/Guard.g:108:31: (op1= disj ( '&&' op2= disj )* )
                # grammars/Guard.g:109:2: op1= disj ( '&&' op2= disj )*
                pass 
                self._state.following.append(self.FOLLOW_disj_in_and_expr110)
                op1 = self.disj()

                self._state.following.pop()
                #action start
                self.and_expr_stack[-1].l = [op1]
                #action end
                # grammars/Guard.g:109:34: ( '&&' op2= disj )*
                while True: #loop2
                    alt2 = 2
                    LA2_0 = self.input.LA(1)

                    if (LA2_0 == 9) :
                        alt2 = 1


                    if alt2 == 1:
                        # grammars/Guard.g:109:35: '&&' op2= disj
                        pass 
                        self.match(self.input, 9, self.FOLLOW_9_in_and_expr115)
                        self._state.following.append(self.FOLLOW_disj_in_and_expr119)
                        op2 = self.disj()

                        self._state.following.pop()
                        #action start
                        self.and_expr_stack[-1].l.append(op2)
                        #action end


                    else:
                        break #loop2


                #action start
                a = AndAtom(self.and_expr_stack[-1].l) 
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.and_expr_stack.pop()
            pass

        return a

    # $ANTLR end "and_expr"


    # $ANTLR start "disj"
    # grammars/Guard.g:111:1: disj returns [a] : ( '(' op= or_expr ')' | op= in_atom | op= negative_expr | op= expr );
    def disj(self, ):

        a = None

        op = None


        try:
            try:
                # grammars/Guard.g:111:18: ( '(' op= or_expr ')' | op= in_atom | op= negative_expr | op= expr )
                alt3 = 4
                LA3 = self.input.LA(1)
                if LA3 == 10:
                    alt3 = 1
                elif LA3 == 19:
                    alt3 = 2
                elif LA3 == 21:
                    alt3 = 3
                elif LA3 == ID or LA3 == INT or LA3 == BOOLCONST:
                    alt3 = 4
                else:
                    nvae = NoViableAltException("", 3, 0, self.input)

                    raise nvae

                if alt3 == 1:
                    # grammars/Guard.g:112:2: '(' op= or_expr ')'
                    pass 
                    self.match(self.input, 10, self.FOLLOW_10_in_disj140)
                    self._state.following.append(self.FOLLOW_or_expr_in_disj144)
                    op = self.or_expr()

                    self._state.following.pop()
                    self.match(self.input, 11, self.FOLLOW_11_in_disj146)
                    #action start
                    a = op 
                    #action end


                elif alt3 == 2:
                    # grammars/Guard.g:113:2: op= in_atom
                    pass 
                    self._state.following.append(self.FOLLOW_in_atom_in_disj155)
                    op = self.in_atom()

                    self._state.following.pop()
                    #action start
                    a = op 
                    #action end


                elif alt3 == 3:
                    # grammars/Guard.g:114:2: op= negative_expr
                    pass 
                    self._state.following.append(self.FOLLOW_negative_expr_in_disj165)
                    op = self.negative_expr()

                    self._state.following.pop()
                    #action start
                    a = op 
                    #action end


                elif alt3 == 4:
                    # grammars/Guard.g:115:2: op= expr
                    pass 
                    self._state.following.append(self.FOLLOW_expr_in_disj175)
                    op = self.expr()

                    self._state.following.pop()
                    #action start
                    a = op 
                    #action end



                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "disj"


    # $ANTLR start "expr"
    # grammars/Guard.g:117:1: expr returns [a] : (op= comp_atom | op= positive_bool );
    def expr(self, ):

        a = None

        op = None


        try:
            try:
                # grammars/Guard.g:117:18: (op= comp_atom | op= positive_bool )
                alt4 = 2
                LA4_0 = self.input.LA(1)

                if (LA4_0 == ID) :
                    LA4_1 = self.input.LA(2)

                    if (LA4_1 == EOF or (8 <= LA4_1 <= 9) or LA4_1 == 11) :
                        alt4 = 2
                    elif ((12 <= LA4_1 <= 18)) :
                        alt4 = 1
                    else:
                        nvae = NoViableAltException("", 4, 1, self.input)

                        raise nvae

                elif ((INT <= LA4_0 <= BOOLCONST)) :
                    alt4 = 1
                else:
                    nvae = NoViableAltException("", 4, 0, self.input)

                    raise nvae

                if alt4 == 1:
                    # grammars/Guard.g:117:20: op= comp_atom
                    pass 
                    self._state.following.append(self.FOLLOW_comp_atom_in_expr193)
                    op = self.comp_atom()

                    self._state.following.pop()
                    #action start
                    a = op 
                    #action end


                elif alt4 == 2:
                    # grammars/Guard.g:118:2: op= positive_bool
                    pass 
                    self._state.following.append(self.FOLLOW_positive_bool_in_expr205)
                    op = self.positive_bool()

                    self._state.following.pop()
                    #action start
                    a = op 
                    #action end



                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "expr"


    # $ANTLR start "comp_atom"
    # grammars/Guard.g:120:1: comp_atom returns [a] : arg1= sum op= ( '==' | '!=' | '<' | '>' | '<=' | '>=' ) arg2= sum ;
    def comp_atom(self, ):

        a = None

        op = None
        arg1 = None

        arg2 = None


        try:
            try:
                # grammars/Guard.g:120:23: (arg1= sum op= ( '==' | '!=' | '<' | '>' | '<=' | '>=' ) arg2= sum )
                # grammars/Guard.g:120:25: arg1= sum op= ( '==' | '!=' | '<' | '>' | '<=' | '>=' ) arg2= sum
                pass 
                self._state.following.append(self.FOLLOW_sum_in_comp_atom221)
                arg1 = self.sum()

                self._state.following.pop()
                op = self.input.LT(1)
                if (12 <= self.input.LA(1) <= 17):
                    self.input.consume()
                    self._state.errorRecovery = False

                else:
                    mse = MismatchedSetException(None, self.input)
                    raise mse


                self._state.following.append(self.FOLLOW_sum_in_comp_atom241)
                arg2 = self.sum()

                self._state.following.pop()
                #action start
                a = CompAtom(arg1, op.text, arg2)
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "comp_atom"


    # $ANTLR start "sum"
    # grammars/Guard.g:122:1: sum returns [a] : o= var ( '+' o= var )* ;
    def sum(self, ):
        self.sum_stack.append(sum_scope())
        a = None

        o = None


        try:
            try:
                # grammars/Guard.g:122:26: (o= var ( '+' o= var )* )
                # grammars/Guard.g:123:2: o= var ( '+' o= var )*
                pass 
                self._state.following.append(self.FOLLOW_var_in_sum261)
                o = self.var()

                self._state.following.pop()
                #action start
                self.sum_stack[-1].l=[o]
                #action end
                # grammars/Guard.g:123:22: ( '+' o= var )*
                while True: #loop5
                    alt5 = 2
                    LA5_0 = self.input.LA(1)

                    if (LA5_0 == 18) :
                        alt5 = 1


                    if alt5 == 1:
                        # grammars/Guard.g:123:23: '+' o= var
                        pass 
                        self.match(self.input, 18, self.FOLLOW_18_in_sum266)
                        self._state.following.append(self.FOLLOW_var_in_sum270)
                        o = self.var()

                        self._state.following.pop()
                        #action start
                        self.sum_stack[-1].l.append(o)
                        #action end


                    else:
                        break #loop5


                #action start
                a = SumAtom(self.sum_stack[-1].l)
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.sum_stack.pop()
            pass

        return a

    # $ANTLR end "sum"


    # $ANTLR start "var"
    # grammars/Guard.g:125:1: var returns [a] : (arg= ID | arg= INT | arg= BOOLCONST );
    def var(self, ):

        a = None

        arg = None

        try:
            try:
                # grammars/Guard.g:125:17: (arg= ID | arg= INT | arg= BOOLCONST )
                alt6 = 3
                LA6 = self.input.LA(1)
                if LA6 == ID:
                    alt6 = 1
                elif LA6 == INT:
                    alt6 = 2
                elif LA6 == BOOLCONST:
                    alt6 = 3
                else:
                    nvae = NoViableAltException("", 6, 0, self.input)

                    raise nvae

                if alt6 == 1:
                    # grammars/Guard.g:125:19: arg= ID
                    pass 
                    arg=self.match(self.input, ID, self.FOLLOW_ID_in_var290)
                    #action start
                    a = arg.text
                    #action end


                elif alt6 == 2:
                    # grammars/Guard.g:125:43: arg= INT
                    pass 
                    arg=self.match(self.input, INT, self.FOLLOW_INT_in_var298)
                    #action start
                    a = int(arg.text)
                    #action end


                elif alt6 == 3:
                    # grammars/Guard.g:125:73: arg= BOOLCONST
                    pass 
                    arg=self.match(self.input, BOOLCONST, self.FOLLOW_BOOLCONST_in_var306)
                    #action start
                    a = BoolConst(arg.text=="true")
                    #action end



                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "var"


    # $ANTLR start "in_atom"
    # grammars/Guard.g:127:1: in_atom returns [a] : 'in' '(' s= state ( '.' s= state )* ')' ;
    def in_atom(self, ):

        a = None

        s = None


        try:
            try:
                # grammars/Guard.g:127:21: ( 'in' '(' s= state ( '.' s= state )* ')' )
                # grammars/Guard.g:127:23: 'in' '(' s= state ( '.' s= state )* ')'
                pass 
                self.match(self.input, 19, self.FOLLOW_19_in_in_atom320)
                self.match(self.input, 10, self.FOLLOW_10_in_in_atom322)
                #action start
                path = []
                #action end
                self._state.following.append(self.FOLLOW_state_in_in_atom328)
                s = self.state()

                self._state.following.pop()
                #action start
                path.append(s)
                #action end
                # grammars/Guard.g:127:69: ( '.' s= state )*
                while True: #loop7
                    alt7 = 2
                    LA7_0 = self.input.LA(1)

                    if (LA7_0 == 20) :
                        alt7 = 1


                    if alt7 == 1:
                        # grammars/Guard.g:127:70: '.' s= state
                        pass 
                        self.match(self.input, 20, self.FOLLOW_20_in_in_atom333)
                        self._state.following.append(self.FOLLOW_state_in_in_atom337)
                        s = self.state()

                        self._state.following.pop()
                        #action start
                        path.append(s)
                        #action end


                    else:
                        break #loop7


                self.match(self.input, 11, self.FOLLOW_11_in_in_atom343)
                #action start
                a = InAtom(path)
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "in_atom"


    # $ANTLR start "positive_bool"
    # grammars/Guard.g:129:1: positive_bool returns [a] : arg= ID ;
    def positive_bool(self, ):

        a = None

        arg = None

        try:
            try:
                # grammars/Guard.g:129:27: (arg= ID )
                # grammars/Guard.g:129:29: arg= ID
                pass 
                arg=self.match(self.input, ID, self.FOLLOW_ID_in_positive_bool359)
                #action start
                a = CompAtom(SumAtom([arg.text]), "==", SumAtom([BoolConst(True)]))
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "positive_bool"


    # $ANTLR start "negative_expr"
    # grammars/Guard.g:131:1: negative_expr returns [a] : '!' (arg1= positive_bool | '(' arg2= or_expr ')' ) ;
    def negative_expr(self, ):

        a = None

        arg1 = None

        arg2 = None


        try:
            try:
                # grammars/Guard.g:131:27: ( '!' (arg1= positive_bool | '(' arg2= or_expr ')' ) )
                # grammars/Guard.g:131:29: '!' (arg1= positive_bool | '(' arg2= or_expr ')' )
                pass 
                self.match(self.input, 21, self.FOLLOW_21_in_negative_expr373)
                # grammars/Guard.g:131:33: (arg1= positive_bool | '(' arg2= or_expr ')' )
                alt8 = 2
                LA8_0 = self.input.LA(1)

                if (LA8_0 == ID) :
                    alt8 = 1
                elif (LA8_0 == 10) :
                    alt8 = 2
                else:
                    nvae = NoViableAltException("", 8, 0, self.input)

                    raise nvae

                if alt8 == 1:
                    # grammars/Guard.g:131:34: arg1= positive_bool
                    pass 
                    self._state.following.append(self.FOLLOW_positive_bool_in_negative_expr378)
                    arg1 = self.positive_bool()

                    self._state.following.pop()
                    #action start
                    a = Negation(arg1)
                    #action end


                elif alt8 == 2:
                    # grammars/Guard.g:131:76: '(' arg2= or_expr ')'
                    pass 
                    self.match(self.input, 10, self.FOLLOW_10_in_negative_expr384)
                    self._state.following.append(self.FOLLOW_or_expr_in_negative_expr388)
                    arg2 = self.or_expr()

                    self._state.following.pop()
                    self.match(self.input, 11, self.FOLLOW_11_in_negative_expr390)
                    #action start
                    a = Negation(arg2)
                    #action end







                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return a

    # $ANTLR end "negative_expr"


    # $ANTLR start "state"
    # grammars/Guard.g:133:1: state returns [state_name] : (s= ID | s= INT ) ;
    def state(self, ):

        state_name = None

        s = None

        try:
            try:
                # grammars/Guard.g:133:28: ( (s= ID | s= INT ) )
                # grammars/Guard.g:133:30: (s= ID | s= INT )
                pass 
                # grammars/Guard.g:133:30: (s= ID | s= INT )
                alt9 = 2
                LA9_0 = self.input.LA(1)

                if (LA9_0 == ID) :
                    alt9 = 1
                elif (LA9_0 == INT) :
                    alt9 = 2
                else:
                    nvae = NoViableAltException("", 9, 0, self.input)

                    raise nvae

                if alt9 == 1:
                    # grammars/Guard.g:133:31: s= ID
                    pass 
                    s=self.match(self.input, ID, self.FOLLOW_ID_in_state408)


                elif alt9 == 2:
                    # grammars/Guard.g:133:38: s= INT
                    pass 
                    s=self.match(self.input, INT, self.FOLLOW_INT_in_state414)



                #action start
                state_name = s.text
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return state_name

    # $ANTLR end "state"


    # Delegated rules


 

    FOLLOW_or_expr_in_guard53 = frozenset([])
    FOLLOW_EOF_in_guard57 = frozenset([1])
    FOLLOW_and_expr_in_or_expr76 = frozenset([1, 8])
    FOLLOW_8_in_or_expr81 = frozenset([4, 5, 6, 10, 19, 21])
    FOLLOW_and_expr_in_or_expr85 = frozenset([1, 8])
    FOLLOW_disj_in_and_expr110 = frozenset([1, 9])
    FOLLOW_9_in_and_expr115 = frozenset([4, 5, 6, 10, 19, 21])
    FOLLOW_disj_in_and_expr119 = frozenset([1, 9])
    FOLLOW_10_in_disj140 = frozenset([4, 5, 6, 10, 19, 21])
    FOLLOW_or_expr_in_disj144 = frozenset([11])
    FOLLOW_11_in_disj146 = frozenset([1])
    FOLLOW_in_atom_in_disj155 = frozenset([1])
    FOLLOW_negative_expr_in_disj165 = frozenset([1])
    FOLLOW_expr_in_disj175 = frozenset([1])
    FOLLOW_comp_atom_in_expr193 = frozenset([1])
    FOLLOW_positive_bool_in_expr205 = frozenset([1])
    FOLLOW_sum_in_comp_atom221 = frozenset([12, 13, 14, 15, 16, 17])
    FOLLOW_set_in_comp_atom225 = frozenset([4, 5, 6])
    FOLLOW_sum_in_comp_atom241 = frozenset([1])
    FOLLOW_var_in_sum261 = frozenset([1, 18])
    FOLLOW_18_in_sum266 = frozenset([4, 5, 6])
    FOLLOW_var_in_sum270 = frozenset([1, 18])
    FOLLOW_ID_in_var290 = frozenset([1])
    FOLLOW_INT_in_var298 = frozenset([1])
    FOLLOW_BOOLCONST_in_var306 = frozenset([1])
    FOLLOW_19_in_in_atom320 = frozenset([10])
    FOLLOW_10_in_in_atom322 = frozenset([4, 5])
    FOLLOW_state_in_in_atom328 = frozenset([11, 20])
    FOLLOW_20_in_in_atom333 = frozenset([4, 5])
    FOLLOW_state_in_in_atom337 = frozenset([11, 20])
    FOLLOW_11_in_in_atom343 = frozenset([1])
    FOLLOW_ID_in_positive_bool359 = frozenset([1])
    FOLLOW_21_in_negative_expr373 = frozenset([4, 5, 6, 10, 19, 21])
    FOLLOW_positive_bool_in_negative_expr378 = frozenset([1])
    FOLLOW_10_in_negative_expr384 = frozenset([4, 5, 6, 10, 19, 21])
    FOLLOW_or_expr_in_negative_expr388 = frozenset([11])
    FOLLOW_11_in_negative_expr390 = frozenset([1])
    FOLLOW_ID_in_state408 = frozenset([1])
    FOLLOW_INT_in_state414 = frozenset([1])



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import ParserMain
    main = ParserMain("GuardLexer", GuardParser)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
