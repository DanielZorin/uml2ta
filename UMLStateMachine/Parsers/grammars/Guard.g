grammar Guard;

options {
	language=Python;
}

@parser::header {
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
}


@rulecatch {
except RecognitionException, e:
   raise
}

@lexer::members {
def reportError(self, e): raise e
}

guard returns [r] :
	op=or_expr { r = op } EOF;

or_expr returns [a] scope {l}:	
	op1=and_expr {$or_expr::l = [op1]} ('||' op2=and_expr {$or_expr::l.append(op2)})* { a = OrAtom($or_expr::l) };

and_expr returns [a] scope {l}:	
	op1=disj {$and_expr::l = [op1]} ('&&' op2=disj {$and_expr::l.append(op2)})* { a = AndAtom($and_expr::l) };

disj returns [a] : 	
	'(' op=or_expr ')' { a = op }| 
	op=in_atom { a = op } | 
	op=negative_expr { a = op } | 
	op=expr { a = op };

expr returns [a] : op = comp_atom { a = op } | 
	op = positive_bool { a = op };

comp_atom returns [a] : arg1=sum op=('=='|'!='|'<'|'>'|'<='|'>=') arg2=sum {a = CompAtom(arg1, op.text, arg2)};

sum returns [a] scope {l}:
	o=var {$sum::l=[o]} ('+' o=var {$sum::l.append(o)})* {a = SumAtom($sum::l)};

var returns [a] : arg=ID {a = arg.text} | arg=INT {a = int(arg.text)} | arg=BOOLCONST {a = BoolConst(arg.text=="true")};

in_atom returns [a] : 'in' '(' {path = []} s=state {path.append(s)} ('.' s=state {path.append(s)})* ')' {a = InAtom(path)};

positive_bool returns [a] : arg=ID {a = CompAtom(SumAtom([arg.text]), "==", SumAtom([BoolConst(True)]))};

negative_expr returns [a] : '!' (arg1=positive_bool {a = Negation(arg1)} | '(' arg2=or_expr ')' {a = Negation(arg2)});

state returns [state_name] : (s=ID | s=INT) {state_name = s.text}
                ; 

BOOLCONST  : 'true' | 'false'
           ;

ID  :	('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'.')*
    ;

INT :	'0'..'9'+
    ;

WS  :   ( ' '
        | '\t'
        | '\r'
        | '\n'
        ) {$channel=HIDDEN;}
    ;
