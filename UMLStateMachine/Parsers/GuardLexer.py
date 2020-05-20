
import sys
from antlr3 import *
from antlr3.compat import set, frozenset


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


class GuardLexer(Lexer):

    grammarFileName = "grammars/Guard.g"
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

            # grammars/Guard.g:11:6: ( '||' )
            # grammars/Guard.g:11:8: '||'
            pass 
            self.match("||")



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

            # grammars/Guard.g:12:6: ( '&&' )
            # grammars/Guard.g:12:8: '&&'
            pass 
            self.match("&&")



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

            # grammars/Guard.g:13:7: ( '(' )
            # grammars/Guard.g:13:9: '('
            pass 
            self.match(40)



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

            # grammars/Guard.g:14:7: ( ')' )
            # grammars/Guard.g:14:9: ')'
            pass 
            self.match(41)



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

            # grammars/Guard.g:15:7: ( '==' )
            # grammars/Guard.g:15:9: '=='
            pass 
            self.match("==")



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

            # grammars/Guard.g:16:7: ( '!=' )
            # grammars/Guard.g:16:9: '!='
            pass 
            self.match("!=")



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

            # grammars/Guard.g:17:7: ( '<' )
            # grammars/Guard.g:17:9: '<'
            pass 
            self.match(60)



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

            # grammars/Guard.g:18:7: ( '>' )
            # grammars/Guard.g:18:9: '>'
            pass 
            self.match(62)



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

            # grammars/Guard.g:19:7: ( '<=' )
            # grammars/Guard.g:19:9: '<='
            pass 
            self.match("<=")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__16"



    # $ANTLR start "T__17"
    def mT__17(self, ):

        try:
            _type = T__17
            _channel = DEFAULT_CHANNEL

            # grammars/Guard.g:20:7: ( '>=' )
            # grammars/Guard.g:20:9: '>='
            pass 
            self.match(">=")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__17"



    # $ANTLR start "T__18"
    def mT__18(self, ):

        try:
            _type = T__18
            _channel = DEFAULT_CHANNEL

            # grammars/Guard.g:21:7: ( '+' )
            # grammars/Guard.g:21:9: '+'
            pass 
            self.match(43)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__18"



    # $ANTLR start "T__19"
    def mT__19(self, ):

        try:
            _type = T__19
            _channel = DEFAULT_CHANNEL

            # grammars/Guard.g:22:7: ( 'in' )
            # grammars/Guard.g:22:9: 'in'
            pass 
            self.match("in")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__19"



    # $ANTLR start "T__20"
    def mT__20(self, ):

        try:
            _type = T__20
            _channel = DEFAULT_CHANNEL

            # grammars/Guard.g:23:7: ( '.' )
            # grammars/Guard.g:23:9: '.'
            pass 
            self.match(46)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__20"



    # $ANTLR start "T__21"
    def mT__21(self, ):

        try:
            _type = T__21
            _channel = DEFAULT_CHANNEL

            # grammars/Guard.g:24:7: ( '!' )
            # grammars/Guard.g:24:9: '!'
            pass 
            self.match(33)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__21"



    # $ANTLR start "BOOLCONST"
    def mBOOLCONST(self, ):

        try:
            _type = BOOLCONST
            _channel = DEFAULT_CHANNEL

            # grammars/Guard.g:136:12: ( 'true' | 'false' )
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
                # grammars/Guard.g:136:14: 'true'
                pass 
                self.match("true")


            elif alt1 == 2:
                # grammars/Guard.g:136:23: 'false'
                pass 
                self.match("false")


            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "BOOLCONST"



    # $ANTLR start "ID"
    def mID(self, ):

        try:
            _type = ID
            _channel = DEFAULT_CHANNEL

            # grammars/Guard.g:139:5: ( ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' | '.' )* )
            # grammars/Guard.g:139:7: ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' | '.' )*
            pass 
            if (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122):
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse

            # grammars/Guard.g:139:31: ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' | '.' )*
            while True: #loop2
                alt2 = 2
                LA2_0 = self.input.LA(1)

                if (LA2_0 == 46 or (48 <= LA2_0 <= 57) or (65 <= LA2_0 <= 90) or LA2_0 == 95 or (97 <= LA2_0 <= 122)) :
                    alt2 = 1


                if alt2 == 1:
                    # grammars/Guard.g:
                    pass 
                    if self.input.LA(1) == 46 or (48 <= self.input.LA(1) <= 57) or (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122):
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

            # grammars/Guard.g:142:5: ( ( '0' .. '9' )+ )
            # grammars/Guard.g:142:7: ( '0' .. '9' )+
            pass 
            # grammars/Guard.g:142:7: ( '0' .. '9' )+
            cnt3 = 0
            while True: #loop3
                alt3 = 2
                LA3_0 = self.input.LA(1)

                if ((48 <= LA3_0 <= 57)) :
                    alt3 = 1


                if alt3 == 1:
                    # grammars/Guard.g:142:7: '0' .. '9'
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

            # grammars/Guard.g:145:5: ( ( ' ' | '\\t' | '\\r' | '\\n' ) )
            # grammars/Guard.g:145:9: ( ' ' | '\\t' | '\\r' | '\\n' )
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
        # grammars/Guard.g:1:8: ( T__8 | T__9 | T__10 | T__11 | T__12 | T__13 | T__14 | T__15 | T__16 | T__17 | T__18 | T__19 | T__20 | T__21 | BOOLCONST | ID | INT | WS )
        alt4 = 18
        alt4 = self.dfa4.predict(self.input)
        if alt4 == 1:
            # grammars/Guard.g:1:10: T__8
            pass 
            self.mT__8()


        elif alt4 == 2:
            # grammars/Guard.g:1:15: T__9
            pass 
            self.mT__9()


        elif alt4 == 3:
            # grammars/Guard.g:1:20: T__10
            pass 
            self.mT__10()


        elif alt4 == 4:
            # grammars/Guard.g:1:26: T__11
            pass 
            self.mT__11()


        elif alt4 == 5:
            # grammars/Guard.g:1:32: T__12
            pass 
            self.mT__12()


        elif alt4 == 6:
            # grammars/Guard.g:1:38: T__13
            pass 
            self.mT__13()


        elif alt4 == 7:
            # grammars/Guard.g:1:44: T__14
            pass 
            self.mT__14()


        elif alt4 == 8:
            # grammars/Guard.g:1:50: T__15
            pass 
            self.mT__15()


        elif alt4 == 9:
            # grammars/Guard.g:1:56: T__16
            pass 
            self.mT__16()


        elif alt4 == 10:
            # grammars/Guard.g:1:62: T__17
            pass 
            self.mT__17()


        elif alt4 == 11:
            # grammars/Guard.g:1:68: T__18
            pass 
            self.mT__18()


        elif alt4 == 12:
            # grammars/Guard.g:1:74: T__19
            pass 
            self.mT__19()


        elif alt4 == 13:
            # grammars/Guard.g:1:80: T__20
            pass 
            self.mT__20()


        elif alt4 == 14:
            # grammars/Guard.g:1:86: T__21
            pass 
            self.mT__21()


        elif alt4 == 15:
            # grammars/Guard.g:1:92: BOOLCONST
            pass 
            self.mBOOLCONST()


        elif alt4 == 16:
            # grammars/Guard.g:1:102: ID
            pass 
            self.mID()


        elif alt4 == 17:
            # grammars/Guard.g:1:105: INT
            pass 
            self.mINT()


        elif alt4 == 18:
            # grammars/Guard.g:1:109: WS
            pass 
            self.mWS()







    # lookup tables for DFA #4

    DFA4_eot = DFA.unpack(
        u"\6\uffff\1\22\1\24\1\26\1\uffff\1\16\1\uffff\2\16\11\uffff\1\32"
        u"\2\16\1\uffff\2\16\1\37\1\16\1\uffff\1\37"
        )

    DFA4_eof = DFA.unpack(
        u"\41\uffff"
        )

    DFA4_min = DFA.unpack(
        u"\1\11\5\uffff\3\75\1\uffff\1\156\1\uffff\1\162\1\141\11\uffff"
        u"\1\56\1\165\1\154\1\uffff\1\145\1\163\1\56\1\145\1\uffff\1\56"
        )

    DFA4_max = DFA.unpack(
        u"\1\174\5\uffff\3\75\1\uffff\1\156\1\uffff\1\162\1\141\11\uffff"
        u"\1\172\1\165\1\154\1\uffff\1\145\1\163\1\172\1\145\1\uffff\1\172"
        )

    DFA4_accept = DFA.unpack(
        u"\1\uffff\1\1\1\2\1\3\1\4\1\5\3\uffff\1\13\1\uffff\1\15\2\uffff"
        u"\1\20\1\21\1\22\1\6\1\16\1\11\1\7\1\12\1\10\3\uffff\1\14\4\uffff"
        u"\1\17\1\uffff"
        )

    DFA4_special = DFA.unpack(
        u"\41\uffff"
        )

            
    DFA4_transition = [
        DFA.unpack(u"\2\20\2\uffff\1\20\22\uffff\1\20\1\6\4\uffff\1\2\1"
        u"\uffff\1\3\1\4\1\uffff\1\11\2\uffff\1\13\1\uffff\12\17\2\uffff"
        u"\1\7\1\5\1\10\2\uffff\32\16\4\uffff\1\16\1\uffff\5\16\1\15\2\16"
        u"\1\12\12\16\1\14\6\16\1\uffff\1\1"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\16\1\uffff\12\16\7\uffff\32\16\4\uffff\1\16\1\uffff"
        u"\32\16"),
        DFA.unpack(u"\1\33"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\36"),
        DFA.unpack(u"\1\16\1\uffff\12\16\7\uffff\32\16\4\uffff\1\16\1\uffff"
        u"\32\16"),
        DFA.unpack(u"\1\40"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\16\1\uffff\12\16\7\uffff\32\16\4\uffff\1\16\1\uffff"
        u"\32\16")
    ]

    # class definition for DFA #4

    DFA4 = DFA
 



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import LexerMain
    main = LexerMain(GuardLexer)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
