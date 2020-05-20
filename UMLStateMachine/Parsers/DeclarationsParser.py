
import sys
from antlr3 import *
from antlr3.compat import set, frozenset
                 
import logging 
import_logger = logging.getLogger('Import from XMI')

class IntVar:
	type = 'intvar'
	def __init__(self, name, range_l, init_val):
		if not init_val in range(range_l[0], range_l[1]+1):
			import_logger.error("Variable \""+name+"\" default value "+str(init_val)+" is outside its values range "+str(range_l[0])+".."+str(range_l[1]) +", setting it to "+str(range_l[0]))
			init_val = range_l[0]
		self.name = name
		self.range = range_l
		self.init_val = init_val
	def __str__(self):
		return self.name
		
class ClockVar:
	type = 'clockvar'
	def __init__(self, name):
		self.name = name
	def __str__(self):
		return self.name

class SignalVar:
	type = 'signalvar'
	def __init__(self, name):
		self.name = name
	def __str__(self):
		return self.name
		
class Macro:
	type = 'macro'
	def __init__(self, src, to):
		self.name = src
		self.src = src
		self.to = to

class BoolVar:
	type = 'boolvar'
	def __init__(self, name, init_val):
		assert(type(init_val) == bool)
		self.name = name
		self.init_val = init_val
	def __str__(self):
		return self.name



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
WS=7
T__16=16
T__15=15
T__12=12
T__11=11
T__14=14
T__13=13
T__10=10
BOOL=6
INT=4
ID=5
EOF=-1
T__9=9
T__8=8

# token names
tokenNames = [
    "<invalid>", "<EOR>", "<DOWN>", "<UP>", 
    "INT", "ID", "BOOL", "WS", "'int'", "'['", "'..'", "']'", "'='", "';'", 
    "'clock'", "'signal'", "'bool'"
]



class declarations_scope(object):
    def __init__(self):
        self.decls = None


class DeclarationsParser(Parser):
    grammarFileName = "grammars/Declarations.g"
    antlr_version = version_str_to_tuple("3.1.1")
    antlr_version_str = "3.1.1"
    tokenNames = tokenNames

    def __init__(self, input, state=None):
        if state is None:
            state = RecognizerSharedState()

        Parser.__init__(self, input, state)



	self.declarations_stack = []





                


        



    # $ANTLR start "declarations"
    # grammars/Declarations.g:73:1: declarations returns [r] : ( declaration )+ ;
    def declarations(self, ):
        self.declarations_stack.append(declarations_scope())
        r = None

        try:
            try:
                # grammars/Declarations.g:78:2: ( ( declaration )+ )
                # grammars/Declarations.g:79:2: ( declaration )+
                pass 
                #action start
                  
                self.declarations_stack[-1].decls = []
                 
                #action end
                # grammars/Declarations.g:82:2: ( declaration )+
                cnt1 = 0
                while True: #loop1
                    alt1 = 2
                    LA1_0 = self.input.LA(1)

                    if (LA1_0 == 8 or (14 <= LA1_0 <= 16)) :
                        alt1 = 1


                    if alt1 == 1:
                        # grammars/Declarations.g:82:3: declaration
                        pass 
                        self._state.following.append(self.FOLLOW_declaration_in_declarations68)
                        self.declaration()

                        self._state.following.pop()


                    else:
                        if cnt1 >= 1:
                            break #loop1

                        eee = EarlyExitException(1, self.input)
                        raise eee

                    cnt1 += 1


                #action start
                                 
                r = self.declarations_stack[-1].decls
                 
                #action end




                        
            except RecognitionException, e:
               raise
        finally:

            self.declarations_stack.pop()
            pass

        return r

    # $ANTLR end "declarations"


    # $ANTLR start "declaration"
    # grammars/Declarations.g:87:1: declaration : ( 'int' ( '[' low= INT '..' high= INT ']' ) i= ID '=' inn= INT ';' | 'clock' i= ID ';' | 'signal' i= ID ';' | 'bool' i= ID '=' inn= BOOL ';' );
    def declaration(self, ):

        low = None
        high = None
        i = None
        inn = None

        try:
            try:
                # grammars/Declarations.g:87:13: ( 'int' ( '[' low= INT '..' high= INT ']' ) i= ID '=' inn= INT ';' | 'clock' i= ID ';' | 'signal' i= ID ';' | 'bool' i= ID '=' inn= BOOL ';' )
                alt2 = 4
                LA2 = self.input.LA(1)
                if LA2 == 8:
                    alt2 = 1
                elif LA2 == 14:
                    alt2 = 2
                elif LA2 == 15:
                    alt2 = 3
                elif LA2 == 16:
                    alt2 = 4
                else:
                    nvae = NoViableAltException("", 2, 0, self.input)

                    raise nvae

                if alt2 == 1:
                    # grammars/Declarations.g:88:3: 'int' ( '[' low= INT '..' high= INT ']' ) i= ID '=' inn= INT ';'
                    pass 
                    self.match(self.input, 8, self.FOLLOW_8_in_declaration83)
                    # grammars/Declarations.g:88:10: ( '[' low= INT '..' high= INT ']' )
                    # grammars/Declarations.g:88:11: '[' low= INT '..' high= INT ']'
                    pass 
                    self.match(self.input, 9, self.FOLLOW_9_in_declaration87)
                    low=self.match(self.input, INT, self.FOLLOW_INT_in_declaration92)
                    self.match(self.input, 10, self.FOLLOW_10_in_declaration95)
                    high=self.match(self.input, INT, self.FOLLOW_INT_in_declaration100)
                    self.match(self.input, 11, self.FOLLOW_11_in_declaration103)



                    i=self.match(self.input, ID, self.FOLLOW_ID_in_declaration108)
                    self.match(self.input, 12, self.FOLLOW_12_in_declaration111)
                    inn=self.match(self.input, INT, self.FOLLOW_INT_in_declaration116)
                    self.match(self.input, 13, self.FOLLOW_13_in_declaration119)
                    #action start
                    self.declarations_stack[-1].decls.append(IntVar(i.text, (int(low.text), int(high.text)), int(inn.text)))
                    #action end


                elif alt2 == 2:
                    # grammars/Declarations.g:90:3: 'clock' i= ID ';'
                    pass 
                    self.match(self.input, 14, self.FOLLOW_14_in_declaration129)
                    i=self.match(self.input, ID, self.FOLLOW_ID_in_declaration134)
                    self.match(self.input, 13, self.FOLLOW_13_in_declaration137)
                    #action start
                    self.declarations_stack[-1].decls.append(ClockVar(i.text))
                    #action end


                elif alt2 == 3:
                    # grammars/Declarations.g:92:3: 'signal' i= ID ';'
                    pass 
                    self.match(self.input, 15, self.FOLLOW_15_in_declaration147)
                    i=self.match(self.input, ID, self.FOLLOW_ID_in_declaration152)
                    self.match(self.input, 13, self.FOLLOW_13_in_declaration155)
                    #action start
                    self.declarations_stack[-1].decls.append(SignalVar(i.text))
                    #action end


                elif alt2 == 4:
                    # grammars/Declarations.g:94:3: 'bool' i= ID '=' inn= BOOL ';'
                    pass 
                    self.match(self.input, 16, self.FOLLOW_16_in_declaration165)
                    i=self.match(self.input, ID, self.FOLLOW_ID_in_declaration170)
                    self.match(self.input, 12, self.FOLLOW_12_in_declaration172)
                    inn=self.match(self.input, BOOL, self.FOLLOW_BOOL_in_declaration177)
                    self.match(self.input, 13, self.FOLLOW_13_in_declaration180)
                    #action start
                    self.declarations_stack[-1].decls.append(BoolVar(i.text, {'true':True, 'false':False}[inn.text]))
                    #action end



                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return 

    # $ANTLR end "declaration"


    # $ANTLR start "empty"
    # grammars/Declarations.g:97:1: empty : ( WS | );
    def empty(self, ):

        try:
            try:
                # grammars/Declarations.g:97:7: ( WS | )
                alt3 = 2
                LA3_0 = self.input.LA(1)

                if (LA3_0 == WS) :
                    alt3 = 1
                elif (LA3_0 == EOF) :
                    alt3 = 2
                else:
                    nvae = NoViableAltException("", 3, 0, self.input)

                    raise nvae

                if alt3 == 1:
                    # grammars/Declarations.g:98:2: WS
                    pass 
                    self.match(self.input, WS, self.FOLLOW_WS_in_empty193)


                elif alt3 == 2:
                    # grammars/Declarations.g:98:6: 
                    pass 


                        
            except RecognitionException, e:
               raise
        finally:

            pass

        return 

    # $ANTLR end "empty"


    # Delegated rules


 

    FOLLOW_declaration_in_declarations68 = frozenset([1, 8, 14, 15, 16])
    FOLLOW_8_in_declaration83 = frozenset([9])
    FOLLOW_9_in_declaration87 = frozenset([4])
    FOLLOW_INT_in_declaration92 = frozenset([10])
    FOLLOW_10_in_declaration95 = frozenset([4])
    FOLLOW_INT_in_declaration100 = frozenset([11])
    FOLLOW_11_in_declaration103 = frozenset([5])
    FOLLOW_ID_in_declaration108 = frozenset([12])
    FOLLOW_12_in_declaration111 = frozenset([4])
    FOLLOW_INT_in_declaration116 = frozenset([13])
    FOLLOW_13_in_declaration119 = frozenset([1])
    FOLLOW_14_in_declaration129 = frozenset([5])
    FOLLOW_ID_in_declaration134 = frozenset([13])
    FOLLOW_13_in_declaration137 = frozenset([1])
    FOLLOW_15_in_declaration147 = frozenset([5])
    FOLLOW_ID_in_declaration152 = frozenset([13])
    FOLLOW_13_in_declaration155 = frozenset([1])
    FOLLOW_16_in_declaration165 = frozenset([5])
    FOLLOW_ID_in_declaration170 = frozenset([12])
    FOLLOW_12_in_declaration172 = frozenset([6])
    FOLLOW_BOOL_in_declaration177 = frozenset([13])
    FOLLOW_13_in_declaration180 = frozenset([1])
    FOLLOW_WS_in_empty193 = frozenset([1])



       
def main(argv, otherArg=None):
	from DeclarationsLexer import DeclarationsLexer
	char_stream = ANTLRFileStream(sys.argv[1])
	lexer = DeclarationsLexer(char_stream)
	tokens = CommonTokenStream(lexer)
	parser = DeclarationsParser(tokens);
	print parser.declarations()


if __name__ == '__main__':
    main(sys.argv)
