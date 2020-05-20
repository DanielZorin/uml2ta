grammar Declarations;

options {
	language=Python;
}

@parser::header {
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
}

@rulecatch {
except RecognitionException, e:
   raise
}

@lexer::members {
def reportError(self, e): raise e
}

@main {
def main(argv, otherArg=None):
	from DeclarationsLexer import DeclarationsLexer
	char_stream = ANTLRFileStream(sys.argv[1])
	lexer = DeclarationsLexer(char_stream)
	tokens = CommonTokenStream(lexer)
	parser = DeclarationsParser(tokens);
	print parser.declarations()
}

declarations 
returns [r] 
scope {
decls
} 
 :
 {
 $declarations::decls = []
 }
 (declaration)+ {
r = $declarations::decls
 }
;

declaration :
		'int'  ('['  low=INT  '..'  high=INT  ']') i=ID  '='  inn=INT  ';'
		{$declarations::decls.append(IntVar(i.text, (int(low.text), int(high.text)), int(inn.text)))} |
		'clock'  i=ID  ';'
		{$declarations::decls.append(ClockVar(i.text))} |
		'signal'  i=ID  ';'
		{$declarations::decls.append(SignalVar(i.text))} |
		'bool'  i=ID '='  inn=BOOL  ';'
		{$declarations::decls.append(BoolVar(i.text, {'true':True, 'false':False}[inn.text]))};

empty :
	WS |;
	
BOOL :	'true'|'false'
	;

ID  :	('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
    ;

INT :	'0'..'9'+
    ;

WS  :   ( ' ' | '\t' | '\r' | '\n') {$channel=HIDDEN;}
    ;