""" 
    Copyright (C) 2009
    Andreas Engelbredt Dalsgaard <andreas.dalsgaard@gmail.com>
    Martin Toft <mt@martintoft.dk>
    Mads Chr. Olesen <mchro@cs.aau.dk>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. """

from lexer import *
import expressionParser
from node import Node

# dictionary of names
identifiers = { }

class Parser:

    currentToken = None
    lexer = None
    expressionParser = None
    typedefDict = {}
    externList = []
    
    def __init__(self, data, lexer):
        self.lexer = lexer
        self.lexer.input(data)
        self.currentToken = self.lexer.token()
        children = []
        if self.currentToken != None:
            children = self.parseStatements()
        self.AST = Node('RootNode', children)
  
    def parseStatements(self):
        statements = []

        while 1:
            if self.currentToken:
                if self.currentToken.type in ('VOID'): #Function
                    type = self.parseFuncType()
                    identifier = self.parseIdentifier()
                    statements.append(self.parseFunction(type, identifier))
                elif self.currentToken.type in ('CONST', 'CLOCK', 'CHANNEL', 'URGENT', 'BROADCAST'): #Declaration
                    if self.currentToken.type == 'CONST':
                        self.accept('CONST')
                        type = self.parseStdType(True)
                    else:
                        type = self.parseDeclType()
                    identifier = self.parseIdentifierComplex()
                    statements.append(self.parseDeclaration(type, identifier))
                elif self.currentToken.type in ('INT', 'BOOL', 'IDENTIFIER'): #Function or declaration           
                    type = self.parseStdType(False)
                    identifier = self.parseIdentifierComplex()
                    
                    if self.currentToken.type == 'LPAREN':  #TODO check that it is not a complex identifier
                        statements.append(self.parseFunction(type, identifier))
                    else:
                        statements.append(self.parseDeclaration(type, identifier)) 
                elif self.currentToken.type == 'STRUCT':
                    structDecl = self.parseStruct()
                    structIden = self.parseIdentifier()
                    self.accept('SEMI')
                    statements.append(Node('Struct', structDecl, structIden))
                elif self.currentToken.type == 'TYPEDEF':
                    statements.append(self.parseTypedef())
                elif self.currentToken.type == 'EXTERN':
                    statements.append(self.parseExtern())
                else:
                    break 
            else:
                break

        if self.currentToken != None:
            self.error('at token "%s" on line %d: Did not expect any token, but found token of type %s' % (self.currentToken.value, self.currentToken.lineno, self.currentToken.type))

        return statements

    def parseStruct(self):
        structDecl = []
        self.accept('STRUCT')
        self.accept('LCURLYPAREN')
        while self.currentToken.type in ('INT', 'BOOL'): 
            type = self.parseDeclType()
            identifier = self.parseIdentifierComplex()
            structDecl.append(self.parseDeclaration(type, identifier))

        self.accept('RCURLYPAREN')
        return structDecl

    def parseDeclaration(self, type, identifier):
        varList = []
        
        #TODO scalars
        #TODO typedef
        varList.append(identifier)
        while self.currentToken.type in ('COMMA', 'EQUALS'):
            if self.currentToken.type == 'COMMA':
                self.accept('COMMA')
                identifier = self.parseIdentifierComplex()
                varList.append(identifier)
            elif self.currentToken.type == 'EQUALS':
                a = self.parseAssignment(identifier, shorthand=False)
                identifier.children.append(a)
            else:
                self.error('Did not expect token type' + self.currentToken.type)
                return
    
        if self.currentToken.type == 'SEMI':           
            self.accept('SEMI')

        return Node('VarDecl', varList, type)

    def parseTypedef(self):
        self.accept('TYPEDEF')
        if self.currentToken.type == 'STRUCT':
            structDecl = self.parseStruct()
            if self.currentToken.type == 'IDENTIFIER':
                typeName = self.currentToken.value
                self.accept('IDENTIFIER')
            else:
                typeName = 'ErrorName'
                self.error('Expected identifier')
            n = Node('NodeTypedef', structDecl, typeName)
            self.typedefDict[typeName] = n
            self.accept('SEMI')
            return n
        else:
            type = self.parseStdType(False)
            if self.currentToken.type == 'IDENTIFIER':
                typeName = self.currentToken.value
                self.accept('IDENTIFIER')
            else:
                typeName = 'ErrorName'
                self.error('Expected identifier')
            n = Node('NodeTypedef', [type], typeName)
            self.typedefDict[typeName] = n
            self.accept('SEMI')
            return n

    def parseExtern(self):
        self.accept('EXTERN')
        identnode = self.parseIdentifier()
        ident = identnode.leaf
        n = Node('NodeExtern', [], ident)

        self.typedefDict[ident] = n
        self.externList += [ident]

        self.accept('SEMI')
        return n

    def parseIndex(self):
        self.accept('LBRACKET')
        if self.currentToken.type == 'RBRACKET':
            self.error('invalid expression')
            e = None
        else:
            e = self.parseExpression()
        self.accept('RBRACKET')
        return Node('Index', [], e)

    def parseFunction(self, type, identifier):
        children = []
        self.accept('LPAREN')
        parameters = self.parseParameters()
        self.accept('RPAREN')
        self.accept('LCURLYPAREN')
        children.extend(self.parseBodyStatements())
        self.accept('RCURLYPAREN')

        return Node('Function', children, (type, identifier, parameters))
    
    def parseParameters(self):
        parameters = []
        while self.currentToken.type in ('INT', 'BOOL', 'CONST', 'IDENTIFIER'):
            isConst = False
            if self.currentToken.type == 'CONST':
                self.accept('CONST')
                isConst = True
            type = self.parseStdType(isConst) 
            identifier = self.parseIdentifierComplex()
            parameters.append( Node('Parameter', [], (type, identifier)) )
            if self.currentToken.type == 'COMMA':
                self.accept('COMMA')

        return parameters
   
    def parseBodyStatements(self):
        statements = []
        while self.currentToken.type != 'RCURLYPAREN':
            if self.currentToken.type in ('INT', 'BOOL', 'CONST'):
                if self.currentToken.type == 'CONST':
                    type = self.parseStdType(True)
                else:
                    type = self.parseStdType(False)
                identifier = self.parseIdentifierComplex()
                statements.append(self.parseDeclaration(type, identifier))
            elif self.currentToken.type == 'FOR':
                statements.append(self.parseForLoop())
            elif self.currentToken.type == 'WHILE':
                statements.append(self.parseWhileLoop())
            elif self.currentToken.type == 'DO':
                statements.append(self.parseDoWhileLoop())
            elif self.currentToken.type in ('IDENTIFIER', 'PLUSPLUS', 'MINUSMINUS'):
                if self.isType(self.currentToken.value):
                    statements.append(self.parseTypedefType())
                identifier = None
                if self.currentToken.type == 'IDENTIFIER':
                    identifier = self.parseIdentifierComplex()
                statements.append(self.parseAssignment(identifier))
                self.accept('SEMI')
            elif self.currentToken.type == 'RETURN':
                self.accept('RETURN')
                expression = self.parseExpression()
                n = Node('Return', [], expression)
                statements.append(n)
                self.accept('SEMI')
            else:
                self.error('parseBodyStatement unknown token: %s' % self.currentToken.type)
                break

        return statements 

    def parseVariableList(self):
        children = []
        while self.currentToken.type == 'COMMA':
            self.accept('COMMA')
            children.append(self.parseIdentifier())
         
        return children

    def parseExpression(self):
        exprParser = expressionParser.ExpressionParser(self.lexer, self)
        return Node('Expression', children=[exprParser.parse()])
       
    def parseNumber(self):
        n = Node('Number', [], self.currentToken.value)
        self.accept('NUMBER')
        return n

    #TODO add support for := *= %= += -= <<= >>= &= |=
    def parseAssignment(self, identifier, shorthand = True):
        if self.currentToken.type == 'EQUALS':
            self.accept('EQUALS')
            n = self.parseExpression()
            return Node('Assignment', [n], identifier) 
        elif shorthand:  #add -- support
            if self.currentToken.type == 'PLUSPLUS':
                self.accept('PLUSPLUS')
                if identifier == None:
                    identifier = self.parseIdentifierComplex()
                    ppnode = Node('PlusPlusPre', [identifier])
                else:
                    ppnode = Node('PlusPlusPost', [identifier])         
                return Node('Assignment', children=[Node('Expression', children=[ppnode])])
            elif self.currentToken.type == 'MINUSMINUS':
                self.accept('MINUSMINUS')
                if identifier == None:
                    identifier = self.parseIdentifierComplex()
                    mmnode = Node('MinusMinusPre', [identifier])
                else:
                    mmnode = Node('MinusMinusPost', [identifier])
                return Node('Assignment', children=[Node('Expression', children=[mmnode])])
        self.error('at assignment parsing, at token "%s" on line %d: Did not expect token type: "%s"' % (self.currentToken.value, self.currentToken.lineno, self.currentToken.type))

    def parseBooleanExpression(self):
        exprParser = expressionParser.ExpressionParser(self.lexer, self)
        return Node('BooleanExpression', children=[exprParser.parse()])

    def parseForLoop(self):
        leaf = []
        self.accept('FOR')
        self.accept('LPAREN')
        leaf.append(self.parseAssignment(self.parseIdentifierComplex()))
        self.accept('SEMI')
        leaf.append(self.parseBooleanExpression())
        self.accept('SEMI')
        leaf.append(self.parseAssignment(self.parseIdentifierComplex()))
        self.accept('RPAREN')
        self.accept('LCURLYPAREN')
        children = self.parseBodyStatements()
        self.accept('RCURLYPAREN')

        return Node('ForLoop', children, leaf)
           
    def parseWhileLoop(self):
        leaf = []
        self.accept('WHILE')
        self.accept('LPAREN')
        leaf.append(self.parseBooleanExpression())
        self.accept('RPAREN')
        self.accept('LCURLYPAREN')
        children = self.parseBodyStatements()
        self.accept('RCURLYPAREN')

        return Node('WhileLoop', children, leaf)

    def parseDoWhileLoop(self):
        leaf = []
        self.accept('DO')
        self.accept('LCURLYPAREN')
        children = self.parseBodyStatements()
        self.accept('RCURLYPAREN')
        self.accept('WHILE')
        self.accept('LPAREN')
        leaf.append(self.parseBooleanExpression())
        self.accept('RPAREN')
        self.accept('SEMI')

        return Node('DoWhileLoop', children, leaf)

    def parseIdentifier(self):
        n = Node('Identifier', [], self.currentToken.value)
        self.accept('IDENTIFIER')
        return n

    def parseIdentifierComplex(self):
        n = self.parseIdentifier()
        p = n

        while self.currentToken.type == 'DOT':	#TODO should be possible to intermix DOT's and BRACKET's
            self.accept('DOT')
            element = self.parseIdentifier()
            p.children = [element]
            p = element
        
        p.children = p.children or []
        while self.currentToken.type == 'LBRACKET':
            index = self.parseIndex()
            p.children += [index]
            
        
        return n

    def parseDeclType(self):
        if self.currentToken.type == 'URGENT':
            self.accept('URGENT')
            if self.currentToken.type == 'CHANNEL':
                self.accept('CHANNEL')
                return Node('TypeUrgentChannel')
            else:
                self.accept('BROADCAST')
                self.accept('CHANNEL')
                return Node('TypeUrgentBroadcastChannel')
        elif self.currentToken.type == 'CHANNEL':
            self.accept('CHANNEL')
            return Node('TypeChannel')
        elif self.currentToken.type == 'BROADCAST':
            self.accept('BROADCAST')
            self.accept('CHANNEL')
            return Node('TypeBroadcastChannel')
        elif self.currentToken.type == 'CLOCK':
            self.accept('CLOCK')
            return Node('TypeClock')
        else: 
            return self.parseStdType(False)
    
    def parseFuncType(self):
        if self.currentToken.type == 'VOID':
            self.accept('VOID')
            return Node('TypeVoid')

    def parseStdType(self, isConst):
        if self.currentToken.type == 'INT':
            self.accept('INT')
            if self.currentToken.type == 'BITAND' and not isConst:
                self.accept('BITAND')
                return Node('TypeIntPointer')
            elif self.currentToken.type == 'LBRACKET':
                self.accept('LBRACKET')
                #range-constrained int
                lower = self.parseExpression()
                self.accept('COMMA')
                upper = self.parseExpression()
                self.accept('RBRACKET')
                return Node('TypeInt', [lower, upper])
            elif isConst:
                return Node('TypeConstInt')
            else:
                return Node('TypeInt')
        elif self.currentToken.type == 'BOOL':
            self.accept('BOOL')
            if self.currentToken.type == 'BITAND' and not isConst:
                self.accept('BITAND')
                return Node('TypeBoolPointer')
            elif isConst:
                return Node('TypeConstBool')
            else:
                return Node('TypeBool')
        elif self.currentToken.type == 'IDENTIFIER' and not isConst:
            return self.parseTypedefType(self.currentToken.value)
        self.error('Not a type')

    def parseTypedefType(self, str):
        if self.isType(str):
            self.accept('IDENTIFIER')
            return self.getType(str)
        else:
            self.error('Not a typedef type:'+self.currentToken.value)


    def isType(self, str):
        if str in self.typedefDict:
            return True
        else:
            return False

    def getType(self, str):
        return self.typedefDict[str]
    
    def accept(self, expectedTokenType):
        if self.currentToken.type == expectedTokenType:
            self.currentToken = self.lexer.token()
        else:
            self.error('at token %s on line %d: Expected %s but was %s' % (self.currentToken.value, self.currentToken.lineno, expectedTokenType, self.currentToken.type))

    def error(self, msg):
            print 'Error: Parser error', msg
        
class DeclVisitor:
    def __init__(self, parser):
        #calculate variables, clocks and channels
        self.constants = {}
        #variables: list of (identifier, type, array-dimensions)
        self.variables = []
        self.clocks = []
        self.channels = []


        last_type = None
        last_type_node = None
        def visit_identifiers(node):
            global last_type, last_type_node
            if node.type == 'VarDecl':
                last_type = node.leaf.type
                last_type_node = node.leaf
            elif node.type == 'NodeTypedef':
                last_type = 'TypeTypedef'
            elif node.type == 'NodeExtern':
                last_type = 'TypeExtern'
            elif node.type == 'Identifier':
                ident = node.leaf
                #find array dimensions (if any)
                array_dimensions = []
                for child in [c for c in node.children if c.type == 'Index']:
                    array_dimensions += [child.leaf]

                if last_type == 'TypeInt':
                    #TODO ranges
                    self.variables += [(ident, 'int', array_dimensions)]
                elif last_type == 'TypeConstInt':
                    self.constants[ident] = node.children[0].children[0].children[0]
                elif last_type == 'TypeBool':
                    self.variables += [(ident, 'bool', array_dimensions)]
                elif last_type == 'TypeClock':
                    #TODO calculate max constant
                    self.clocks += [(node.leaf, 10)]
                elif last_type == 'TypeChannel':
                    self.channels += [(ident, array_dimensions)]
                elif last_type == 'NodeTypedef' or last_type == 'NodeExtern':
                    self.variables += [(ident, last_type_node.leaf, array_dimensions)]
                #else:
                #    print 'Unknown type: ' + last_type
                return False #don't recurse further
            return True
        parser.AST.visit(visit_identifiers)


# vim:ts=4:sw=4:expandtab
