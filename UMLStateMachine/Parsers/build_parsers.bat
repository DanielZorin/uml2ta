java -cp ./antlr_java/antlr-3.1.1.jar org.antlr.Tool grammars/Action.g -fo .
del Action.tokens
java -cp ./antlr_java/antlr-3.1.1.jar org.antlr.Tool grammars/Guard.g -fo .
del Guard.tokens
java -cp ./antlr_java/antlr-3.1.1.jar org.antlr.Tool grammars/Declarations.g -fo .
del Declarations.tokens
python.exe clear.py