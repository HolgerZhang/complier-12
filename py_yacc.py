"""
语法：
program : statements
statements : statements statement | statement
statement : assignment | expr | print | if | while | for
assignment : leftval ASSIGN expr | leftval ASSIGN array
leftval : leftval LLIST expr RLIST | ID  # 左值，可以被赋值、读取值的符号
# 右值，只能读取值的符号
expr : expr PLUS term | expr MINUS term | term
term : term TIMES factor | term DIVIDE factor | term EDIVIDE factor | factor
factor : leftval | NUMBER | len | LPAREN expr RPAREN
exprs : exprs COMMA expr | expr
len : LEN LPAREN expr RPAREN
print : PRINT LPAREN exprs RPAREN | PRINT LPAREN RPAREN
array : LLIST exprs RLIST | LLIST RLIST
selfvar : leftval DPLUS | leftval DMINUS
condition : expr LT expr | expr LE expr | expr GT expr | expr GE expr | expr EQ expr | expr NE expr | expr
if : IF LPAREN condition RPAREN LBRACE statements RBRACE
   | IF LPAREN condition RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE
   | IF LPAREN condition RPAREN LBRACE statements RBRACE ELIF LPAREN condition RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE
while : WHILE LPAREN condition RPAREN LBRACE statements RBRACE
for : FOR LPAREN assignment SEMICOLON condition SEMICOLON selfvar RPAREN LBRACE statements RBRACE
"""

# coding=utf-8
from ply import yacc
# noinspection PyUnresolvedReferences
from py_lex import *
from node import *


# YACC for parsing Python


def p_program(t):
    """program : statements"""
    if len(t) == 2:
        t[0] = NonTerminal('Program')
        t[0].add(t[1])


def p_statements(t):
    """statements : statements statement
                  | statement"""
    if len(t) == 3:
        t[0] = NonTerminal('Statements')
        t[0].add(t[1])
        t[0].add(t[2])
    elif len(t) == 2:
        t[0] = NonTerminal('Statements')
        t[0].add(t[1])


def p_statement(t):
    """ statement : assignment
                  | expr
                  | print
                  | if
                  | while
                  | for"""
    if len(t) == 2:
        t[0] = NonTerminal('Statement')
        t[0].add(t[1])


def p_assignment(t):
    """assignment : leftval ASSIGN expr
                  | leftval ASSIGN array"""
    if len(t) == 4:
        t[0] = NonTerminal('Assignment')
        t[0].add(t[1])
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])


def p_leftval(t):
    """leftval : leftval LLIST expr RLIST
               | ID"""
    if len(t) == 2:
        t[0] = LeftValue('LeftVal')
        t[0].add(ID(t[1]))
    elif len(t) == 5:
        t[0] = LeftValue('LeftVal')
        t[0].add(t[1])
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
        t[0].add(Terminal(t[4]))


def p_expr(t):
    """expr : expr PLUS term
            | expr MINUS term
            | term"""
    if len(t) == 4:
        t[0] = NonTerminal('Expr')
        t[0].add(t[1])
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
    elif len(t) == 2:
        t[0] = NonTerminal('Expr')
        t[0].add(t[1])


def p_term(t):
    """term : term TIMES factor
            | term DIVIDE factor
            | term EDIVIDE factor
            | factor"""
    if len(t) == 4:
        t[0] = NonTerminal('Term')
        t[0].add(t[1])
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
    elif len(t) == 2:
        t[0] = NonTerminal('Term')
        t[0].add(t[1])


def p_factor(t):
    """factor : leftval
              | NUMBER
              | len
              | LPAREN expr RPAREN """
    if len(t) == 4:
        t[0] = NonTerminal('Factor')
        t[0].add(Terminal(t[1]))
        t[0].add(t[2])
        t[0].add(Terminal(t[3]))
    elif len(t) == 2:
        t[0] = NonTerminal('Factor')
        if isinstance(t[1], int) or str(t[1]).isdigit():
            t[0].add(Number(t[1]))
        else:
            t[0].add(t[1])


def p_exprs(t):
    """exprs : exprs COMMA expr
             | expr"""
    if len(t) == 4:
        t[0] = NonTerminal('Exprs')
        t[0].add(t[1])
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
    elif len(t) == 2:
        t[0] = NonTerminal('Exprs')
        t[0].add(t[1])


def p_len(t):
    """len : LEN LPAREN expr RPAREN"""
    if len(t) == 5:
        t[0] = NonTerminal('Len')
        t[0].add(Terminal(t[1]))
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
        t[0].add(Terminal(t[4]))


def p_print(t):
    """print : PRINT LPAREN exprs RPAREN
             | PRINT LPAREN RPAREN"""
    if len(t) == 5:
        t[0] = NonTerminal('Print')
        t[0].add(Terminal(t[1]))
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
        t[0].add(Terminal(t[4]))
    elif len(t) == 3:
        t[0] = NonTerminal('Print')
        t[0].add(Terminal(t[1]))
        t[0].add(Terminal(t[2]))
        t[0].add(Terminal(t[3]))


def p_array(t):
    """array : LLIST exprs RLIST
             | LLIST RLIST"""
    if len(t) == 4:
        t[0] = NonTerminal('Array')
        t[0].add(Terminal(t[1]))
        t[0].add(t[2])
        t[0].add(Terminal(t[3]))
    elif len(t) == 3:
        t[0] = NonTerminal('Array')
        t[0].add(Terminal(t[1]))
        t[0].add(Terminal(t[2]))


def p_selfvar(t):
    """selfvar : leftval DPLUS
               | leftval DMINUS"""
    if len(t) == 3:
        t[0] = NonTerminal('SelfVar')
        t[0].add(t[1])
        t[0].add(Terminal(t[2]))


def p_condition(t):
    """condition : expr LT expr
                 | expr LE expr
                 | expr GT expr
                 | expr GE expr
                 | expr EQ expr
                 | expr NE expr
                 | expr"""
    if len(t) == 4:
        t[0] = NonTerminal('Condition')
        t[0].add(t[1])
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
    elif len(t) == 2:
        t[0] = NonTerminal('Condition')
        t[0].add(t[1])


def p_if(t):
    """if : IF LPAREN condition RPAREN LBRACE statements RBRACE
          | IF LPAREN condition RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE
          | IF LPAREN condition RPAREN LBRACE statements RBRACE ELIF LPAREN condition RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE"""
    if len(t) == 8:
        t[0] = NonTerminal('If')
        t[0].add(Terminal(t[1]))
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
        t[0].add(Terminal(t[4]))
        t[0].add(Terminal(t[5]))
        t[0].add(t[6])
        t[0].add(Terminal(t[7]))


def p_while(t):
    """while : WHILE LPAREN condition RPAREN LBRACE statements RBRACE"""
    if len(t) == 8:
        t[0] = NonTerminal('While')
        t[0].add(Terminal(t[1]))
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
        t[0].add(Terminal(t[4]))
        t[0].add(Terminal(t[5]))
        t[0].add(t[6])
        t[0].add(Terminal(t[7]))


def p_for(t):
    """for : FOR LPAREN assignment SEMICOLON condition SEMICOLON selfvar RPAREN LBRACE statements RBRACE"""
    if len(t) == 12:
        t[0] = NonTerminal('For')
        t[0].add(Terminal(t[1]))
        t[0].add(Terminal(t[2]))
        t[0].add(t[3])
        t[0].add(Terminal(t[4]))
        t[0].add(t[5])
        t[0].add(Terminal(t[6]))
        t[0].add(t[7])
        t[0].add(Terminal(t[8]))
        t[0].add(Terminal(t[9]))
        t[0].add(t[10])
        t[0].add(Terminal(t[11]))


def p_error(t):
    if t is None:
        raise SyntaxError("Syntax error")
    raise SyntaxError("Syntax error '%s' at line %d" % (t.value[0], t.lexer.lineno))


yacc.yacc()
