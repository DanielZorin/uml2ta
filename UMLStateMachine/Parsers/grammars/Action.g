grammar Action;

options {
	language=Python;
}

@parser::header {
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
	from ActionLexer import ActionLexer
	char_stream = ANTLRFileStream(sys.argv[1])
	lexer = ActionLexer(char_stream)
	tokens = CommonTokenStream(lexer)
	parser = ActionParser(tokens);
	print parser.action()
}



action
returns [r] 
scope {
statements
} 
 :
 {
 $action::statements= []
 }
 assign_statement (';' assign_statement)* ';'? {
r = $action::statements
 } EOF
;

assign_statement : 
	var=ID '=' op=expr {$action::statements.append(AssignStatement(var.text, op))} |
	(('!!' i=ID)|('!!' '(' i=ID ')')) {$action::statements.append(SendSignalStatement(i.text))} |
	var=ID '=' 'random()' {$action::statements.append(RandomAssignStatement(var.text))} ;

expr returns [a] :
	op1=add_expr  ('?' op2=add_expr ':' op3=add_expr {a = ConditionalOp(op1, op2, op3)})? {a = {False: ConditionalOp(op1, op2, op3),  True: op1}[op2==None]};

add_expr returns [a] scope {l}: 
	o=('+'|'-')? e=mult_expr {$add_expr::l = [({True: (lambda x:'+'), False: (lambda i:i.text)}[o==None](o), e)]} (o=('+'|'-') e=mult_expr {$add_expr::l.append((o.text, e))})* {a = {True: PlusOp($add_expr::l), False: $add_expr::l[0][1]}[len($add_expr::l)>1]};

mult_expr returns [a] scope {l}:
	o=comp_expr {$mult_expr::l=[o]} ('*' o=comp_expr {$mult_expr::l.append(o)})* {a = {True: MultOp($mult_expr::l), False: $mult_expr::l[0]}[len($mult_expr::l)>1]};

comp_expr returns [a] scope {l}:
	o=or_expr {$comp_expr::l=[o]} (sign=('>'|'<'|'=='|'!='|'>='|'<=') o=or_expr {$comp_expr::l.append(o)})?
	 {a = {True: CompOp($comp_expr::l, sign.text if sign else None), False: $comp_expr::l[0]}[len($comp_expr::l)>1]};

or_expr returns [a] scope {l}:
	o=and_expr {$or_expr::l=[o]} ('||' o=and_expr {$or_expr::l.append(o)})* {a = {True: OrOp($or_expr::l), False: $or_expr::l[0]}[len($or_expr::l)>1]};
	
and_expr returns [a] scope {l}:
	o=atom {$and_expr::l=[o]} ('&&' o=atom {$and_expr::l.append(o)})* {a = {True: AndOp($and_expr::l), False: $and_expr::l[0]}[len($and_expr::l)>1]};

atom returns [a]:
	(o1=ID {a=VarName(o1.text)}) | (o2=INT {a=IntConst(o2.text)}) | (o3=BOOLCONST {a=BoolConst(o3.text == "true")}) | ('(' o4=expr ')' {a=o4});

send_signal_statement :
	('!!' i=ID)|('!!' '(' i=ID ')') {$action::statements.append(SendSignalStatement(i.text))} ;

BOOLCONST  : 'true' | 'false'
           ;
	
ID  :	('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
    ;

INT :	'0'..'9'+
    ;

WS  :   ( ' '
        | '\t'
        | '\r'
        | '\n'
        ) {$channel=HIDDEN;}
    ;
