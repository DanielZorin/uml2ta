
import sys
from antlr3 import *
from antlr3.compat import set, frozenset


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


class DeclarationsLexer(Lexer):

    grammarFileName = "grammars/Declarations.g"
    antlr_version = version_str_to_tuple("3.1.1")
    antlr_version_str = "3.1.1"

    def __init__(self, input=None, state=None):
        if state is None:
            state = RecognizerSharedState()
        Lexer.__init__(self, input, state)

        self.dfa4 = self.DFA4(
            self, 4,
            eot = self.DFA4_eot,
            eof = self.DFA4_eof,
            min = self.DFA4_min,
            max = self.DFA4_max,
            accept = self.DFA4_accept,
            special = self.DFA4_special,
            transition = self.DFA4_transition
            )




                               
    def reportError(self, e): raise e



    # $ANTLR start "T__8"
    def mT__8(self, ):

        try:
            _type = T__8
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:11:6: ( 'int' )
            # grammars/Declarations.g:11:8: 'int'
            pass 
            self.match("int")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__8"



    # $ANTLR start "T__9"
    def mT__9(self, ):

        try:
            _type = T__9
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:12:6: ( '[' )
            # grammars/Declarations.g:12:8: '['
            pass 
            self.match(91)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__9"



    # $ANTLR start "T__10"
    def mT__10(self, ):

        try:
            _type = T__10
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:13:7: ( '..' )
            # grammars/Declarations.g:13:9: '..'
            pass 
            self.match("..")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__10"



    # $ANTLR start "T__11"
    def mT__11(self, ):

        try:
            _type = T__11
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:14:7: ( ']' )
            # grammars/Declarations.g:14:9: ']'
            pass 
            self.match(93)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__11"



    # $ANTLR start "T__12"
    def mT__12(self, ):

        try:
            _type = T__12
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:15:7: ( '=' )
            # grammars/Declarations.g:15:9: '='
            pass 
            self.match(61)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__12"



    # $ANTLR start "T__13"
    def mT__13(self, ):

        try:
            _type = T__13
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:16:7: ( ';' )
            # grammars/Declarations.g:16:9: ';'
            pass 
            self.match(59)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__13"



    # $ANTLR start "T__14"
    def mT__14(self, ):

        try:
            _type = T__14
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:17:7: ( 'clock' )
            # grammars/Declarations.g:17:9: 'clock'
            pass 
            self.match("clock")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__14"



    # $ANTLR start "T__15"
    def mT__15(self, ):

        try:
            _type = T__15
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:18:7: ( 'signal' )
            # grammars/Declarations.g:18:9: 'signal'
            pass 
            self.match("signal")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__15"



    # $ANTLR start "T__16"
    def mT__16(self, ):

        try:
            _type = T__16
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:19:7: ( 'bool' )
            # grammars/Declarations.g:19:9: 'bool'
            pass 
            self.match("bool")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__16"



    # $ANTLR start "BOOL"
    def mBOOL(self, ):

        try:
            _type = BOOL
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:100:6: ( 'true' | 'false' )
            alt1 = 2
            LA1_0 = self.input.LA(1)

            if (LA1_0 == 116) :
                alt1 = 1
            elif (LA1_0 == 102) :
                alt1 = 2
            else:
                nvae = NoViableAltException("", 1, 0, self.input)

                raise nvae

            if alt1 == 1:
                # grammars/Declarations.g:100:8: 'true'
                pass 
                self.match("true")


            elif alt1 == 2:
                # grammars/Declarations.g:100:15: 'false'
                pass 
                self.match("false")


            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "BOOL"



    # $ANTLR start "ID"
    def mID(self, ):

        try:
            _type = ID
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:103:5: ( ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )* )
            # grammars/Declarations.g:103:7: ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )*
            pass 
            if (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122):
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse

            # grammars/Declarations.g:103:31: ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )*
            while True: #loop2
                alt2 = 2
                LA2_0 = self.input.LA(1)

                if ((48 <= LA2_0 <= 57) or (65 <= LA2_0 <= 90) or LA2_0 == 95 or (97 <= LA2_0 <= 122)) :
                    alt2 = 1


                if alt2 == 1:
                    # grammars/Declarations.g:
                    pass 
                    if (48 <= self.input.LA(1) <= 57) or (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122):
                        self.input.consume()
                    else:
                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse



                else:
                    break #loop2





            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "ID"



    # $ANTLR start "INT"
    def mINT(self, ):

        try:
            _type = INT
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:106:5: ( ( '0' .. '9' )+ )
            # grammars/Declarations.g:106:7: ( '0' .. '9' )+
            pass 
            # grammars/Declarations.g:106:7: ( '0' .. '9' )+
            cnt3 = 0
            while True: #loop3
                alt3 = 2
                LA3_0 = self.input.LA(1)

                if ((48 <= LA3_0 <= 57)) :
                    alt3 = 1


                if alt3 == 1:
                    # grammars/Declarations.g:106:7: '0' .. '9'
                    pass 
                    self.matchRange(48, 57)


                else:
                    if cnt3 >= 1:
                        break #loop3

                    eee = EarlyExitException(3, self.input)
                    raise eee

                cnt3 += 1





            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "INT"



    # $ANTLR start "WS"
    def mWS(self, ):

        try:
            _type = WS
            _channel = DEFAULT_CHANNEL

            # grammars/Declarations.g:109:5: ( ( ' ' | '\\t' | '\\r' | '\\n' ) )
            # grammars/Declarations.g:109:9: ( ' ' | '\\t' | '\\r' | '\\n' )
            pass 
            if (9 <= self.input.LA(1) <= 10) or self.input.LA(1) == 13 or self.input.LA(1) == 32:
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse

            #action start
            _channel=HIDDEN;
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "WS"



    def mTokens(self):
        # grammars/Declarations.g:1:8: ( T__8 | T__9 | T__10 | T__11 | T__12 | T__13 | T__14 | T__15 | T__16 | BOOL | ID | INT | WS )
        alt4 = 13
        alt4 = self.dfa4.predict(self.input)
        if alt4 == 1:
            # grammars/Declarations.g:1:10: T__8
            pass 
            self.mT__8()


        elif alt4 == 2:
            # grammars/Declarations.g:1:15: T__9
            pass 
            self.mT__9()


        elif alt4 == 3:
            # grammars/Declarations.g:1:20: T__10
            pass 
            self.mT__10()


        elif alt4 == 4:
            # grammars/Declarations.g:1:26: T__11
            pass 
            self.mT__11()


        elif alt4 == 5:
            # grammars/Declarations.g:1:32: T__12
            pass 
            self.mT__12()


        elif alt4 == 6:
            # grammars/Declarations.g:1:38: T__13
            pass 
            self.mT__13()


        elif alt4 == 7:
            # grammars/Declarations.g:1:44: T__14
            pass 
            self.mT__14()


        elif alt4 == 8:
            # grammars/Declarations.g:1:50: T__15
            pass 
            self.mT__15()


        elif alt4 == 9:
            # grammars/Declarations.g:1:56: T__16
            pass 
            self.mT__16()


        elif alt4 == 10:
            # grammars/Declarations.g:1:62: BOOL
            pass 
            self.mBOOL()


        elif alt4 == 11:
            # grammars/Declarations.g:1:67: ID
            pass 
            self.mID()


        elif alt4 == 12:
            # grammars/Declarations.g:1:70: INT
            pass 
            self.mINT()


        elif alt4 == 13:
            # grammars/Declarations.g:1:74: WS
            pass 
            self.mWS()







    # lookup tables for DFA #4

    DFA4_eot = DFA.unpack(
        u"\1\uffff\1\14\5\uffff\5\14\3\uffff\6\14\1\33\5\14\1\uffff\2\14"
        u"\1\43\1\44\1\14\1\46\1\14\2\uffff\1\44\1\uffff\1\50\1\uffff"
        )

    DFA4_eof = DFA.unpack(
        u"\51\uffff"
        )

    DFA4_min = DFA.unpack(
        u"\1\11\1\156\5\uffff\1\154\1\151\1\157\1\162\1\141\3\uffff\1\164"
        u"\1\157\1\147\1\157\1\165\1\154\1\60\1\143\1\156\1\154\1\145\1\163"
        u"\1\uffff\1\153\1\141\2\60\1\145\1\60\1\154\2\uffff\1\60\1\uffff"
        u"\1\60\1\uffff"
        )

    DFA4_max = DFA.unpack(
        u"\1\172\1\156\5\uffff\1\154\1\151\1\157\1\162\1\141\3\uffff\1\164"
        u"\1\157\1\147\1\157\1\165\1\154\1\172\1\143\1\156\1\154\1\145\1"
        u"\163\1\uffff\1\153\1\141\2\172\1\145\1\172\1\154\2\uffff\1\172"
        u"\1\uffff\1\172\1\uffff"
        )

    DFA4_accept = DFA.unpack(
        u"\2\uffff\1\2\1\3\1\4\1\5\1\6\5\uffff\1\13\1\14\1\15\14\uffff\1"
        u"\1\7\uffff\1\11\1\12\1\uffff\1\7\1\uffff\1\10"
        )

    DFA4_special = DFA.unpack(
        u"\51\uffff"
        )

            
    DFA4_transition = [
        DFA.unpack(u"\2\16\2\uffff\1\16\22\uffff\1\16\15\uffff\1\3\1\uffff"
        u"\12\15\1\uffff\1\6\1\uffff\1\5\3\uffff\32\14\1\2\1\uffff\1\4\1"
        u"\uffff\1\14\1\uffff\1\14\1\11\1\7\2\14\1\13\2\14\1\1\11\14\1\10"
        u"\1\12\6\14"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\12\14\7\uffff\32\14\4\uffff\1\14\1\uffff\32\14"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\36"),
        DFA.unpack(u"\1\37"),
        DFA.unpack(u"\1\40"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\41"),
        DFA.unpack(u"\1\42"),
        DFA.unpack(u"\12\14\7\uffff\32\14\4\uffff\1\14\1\uffff\32\14"),
        DFA.unpack(u"\12\14\7\uffff\32\14\4\uffff\1\14\1\uffff\32\14"),
        DFA.unpack(u"\1\45"),
        DFA.unpack(u"\12\14\7\uffff\32\14\4\uffff\1\14\1\uffff\32\14"),
        DFA.unpack(u"\1\47"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\12\14\7\uffff\32\14\4\uffff\1\14\1\uffff\32\14"),
        DFA.unpack(u""),
        DFA.unpack(u"\12\14\7\uffff\32\14\4\uffff\1\14\1\uffff\32\14"),
        DFA.unpack(u"")
    ]

    # class definition for DFA #4

    DFA4 = DFA
 



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import LexerMain
    main = LexerMain(DeclarationsLexer)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
