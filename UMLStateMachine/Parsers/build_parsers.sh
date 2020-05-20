echo 'Building Action.g'
CLASSPATH=antlr_java/antlr-2.7.7.jar:antlr_java/antlr-3.1.1.jar:antlr_java/antlr-3.1.1-runtime.jar:antlr_java/stringtemplate-3.2.jar java org.antlr.Tool grammars/Action.g -fo `pwd`
sed '1d' ActionParser.py > /tmp/ActionParser.py
mv /tmp/ActionParser.py .
sed '1d' ActionLexer.py > /tmp/ActionLexer.py
mv /tmp/ActionLexer.py .
rm Action.tokens
echo 'Building Guard.g'
CLASSPATH=antlr_java/antlr-2.7.7.jar:antlr_java/antlr-3.1.1.jar:antlr_java/antlr-3.1.1-runtime.jar:antlr_java/stringtemplate-3.2.jar java org.antlr.Tool grammars/Guard.g  -fo `pwd`
sed '1d' GuardParser.py > /tmp/GuardParser.py
mv /tmp/GuardParser.py .
sed '1d' GuardLexer.py > /tmp/GuardLexer.py
mv /tmp/GuardLexer.py .
rm Guard.tokens
echo 'Building Declarations.g'
CLASSPATH=antlr_java/antlr-2.7.7.jar:antlr_java/antlr-3.1.1.jar:antlr_java/antlr-3.1.1-runtime.jar:antlr_java/stringtemplate-3.2.jargrammars/Declarations.g java org.antlr.Tool grammars/Declarations.g -fo `pwd`
sed '1d' DeclarationsParser.py > /tmp/DeclarationsParser.py
mv /tmp/DeclarationsParser.py .
sed '1d' DeclarationsLexer.py > /tmp/DeclarationsLexer.py
mv /tmp/DeclarationsLexer.py .
rm Declarations.tokens
