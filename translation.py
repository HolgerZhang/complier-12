# coding=utf-8
"""
assignment -> leftval ASSIGN expr  { leftval.value = expr.value; set_value(var_table, leftval.id, expr.value); }
assignment -> leftval ASSIGN array  { leftval.value = array.value; set_value(var_table, leftval.id, array.value); }
leftval -> leftval1 LLIST expr RLIST  { leftval.id = (leftval1.id, expr.value);
                                        leftval.value = get_value(var_table, leftval.id); }
leftval -> ID  { leftval.id = (ID.id, None); leftval.value = ID.value; }
expr -> expr1 '+' term  { expr.value = expr1.value + term.value; }
expr -> expr1 '-' term  { expr.value = expr1.value - term.value; }
expr -> term  { expr.value = term.value; }
term -> term1 '*' factor  { term.value = term1.value * factor.value; }
term -> term1 '/' factor  { term.value = term1.value / factor.value; }
term -> term1 '//' factor  { term.value = term1.value // factor.value; }
term -> factor { term.value = factor.value; }
factor -> leftval { leftval.value = get_value(var_table, leftval.id); factor.value = leftval.value; }
factor -> NUMBER  { factor.value = NUMBER.value; }
factor -> len  { factor.value = len.value; }
factor -> '(' expr ')'  { fact.value = expr.value; }
len -> LEN '(' expr ')'  { len.value = len(expr.value) }
exprs -> exprs1 ',' expr  { exprs.value = exprs1.value + <expr.value>; }
exprs -> expr  { exprs.value = <expr.value>; }
print -> PRINT '(' exprs ')'  { print(*exprs.value); }
print -> PRINT '(' ')'  { print(); }
array -> '[' exprs ']'  { array.value = exprs.value; }
array -> '[' ']' { array.value = <>; }
selfvar -> leftval '++'  { leftval.value = leftval.value + 1; set_value(var_table, leftval.id, leftval.value); }
selfvar -> leftval '--'  { leftval.value = leftval.value - 1; set_value(var_table, leftval.id, leftval.value); }
condition -> expr '<' expr1  { condition.value = exp.value < expr1.value; }
condition -> expr '<=' expr1  { condition.value = exp.value <= expr1.value; }
condition -> expr '>' expr1  { condition.value = exp.value > expr1.value; }
condition -> expr '>=' expr1  { condition.value = exp.value >= expr1.value; }
condition -> expr '==' expr1  { condition.value = exp.value == expr1.value; }
condition -> expr '!=' expr1  { condition.value = exp.value != expr1.value; }
condition -> expr  { condition.value = bool(exp.value); }
"""
from node import *


def get_value(tb, vid):
    name, sub = vid
    if not isinstance(name, tuple):
        if sub is None:
            return tb[name]
        return tb[name][sub]
    if sub is None:
        return get_value(tb, name)
    return get_value(tb, name)[sub]


def set_value(tb, vid, val):
    name, sub = vid
    if not isinstance(name, tuple):
        if sub is None:
            tb[name] = val
            return
        tb[name][sub] = val
        return
    if sub is None:
        set_value(tb, name, val)
        return
    get_value(tb, name)[sub] = val


var_table = {}  # variable table
loop_flag = False  # 循环内指示器
break_flag = False  # break指示器


def translate(tree):
    global loop_flag, break_flag
    if break_flag:
        return
    # 提前翻译 if for while
    if isinstance(tree, NonTerminal):
        # If
        if tree.type == 'If':
            """if : IF LPAREN condition RPAREN LBRACE statements RBRACE"""
            assert len(tree.children) in (7, 11, 18), 'Syntax error'
            assert isinstance(tree.child(0), Terminal) and tree.child(0).text == 'if' and \
                   isinstance(tree.child(1), Terminal) and tree.child(1).text == '(' and \
                   isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Condition' and \
                   isinstance(tree.child(3), Terminal) and tree.child(3).text == ')' and \
                   isinstance(tree.child(4), Terminal) and tree.child(4).text == '{' and \
                   isinstance(tree.child(5), NonTerminal) and tree.child(5).type == 'Statements' and \
                   isinstance(tree.child(6), Terminal) and tree.child(6).text == '}', 'Syntax error'
            translate(tree.child(2))  # Condition
            condition = tree.child(2).value
            if condition:
                translate(tree.child(5))  # Statements
            if len(tree.children) == 11:
                assert isinstance(tree.child(7), Terminal) and tree.child(7).text == 'else' and \
                       isinstance(tree.child(8), Terminal) and tree.child(8).text == '{' and \
                       isinstance(tree.child(9), NonTerminal) and tree.child(9).type == 'Statements' and \
                       isinstance(tree.child(10), Terminal) and tree.child(10).text == '}', 'Syntax error'
                if not condition:
                    translate(tree.child(9))  # Statements2
            elif len(tree.children) == 18:
                assert isinstance(tree.child(7), Terminal) and tree.child(7).text == 'elif' and \
                       isinstance(tree.child(8), Terminal) and tree.child(8).text == '(' and \
                       isinstance(tree.child(9), NonTerminal) and tree.child(9).type == 'Condition' and \
                       isinstance(tree.child(10), Terminal) and tree.child(10).text == ')' and \
                       isinstance(tree.child(11), Terminal) and tree.child(11).text == '{' and \
                       isinstance(tree.child(12), NonTerminal) and tree.child(12).type == 'Statements' and \
                       isinstance(tree.child(13), Terminal) and tree.child(13).text == '}' and \
                       isinstance(tree.child(14), Terminal) and tree.child(14).text == 'else' and \
                       isinstance(tree.child(15), Terminal) and tree.child(15).text == '{' and \
                       isinstance(tree.child(16), NonTerminal) and tree.child(16).type == 'Statements' and \
                       isinstance(tree.child(17), Terminal) and tree.child(17).text == '}', 'Syntax error'
                translate(tree.child(9))  # Condition
                elif_condition = tree.child(9).value
                if (not condition) and elif_condition:
                    translate(tree.child(12))  # Statements2
                else:
                    translate(tree.child(16))  # Statements3
            return
        # While
        elif tree.type == 'While':
            """while : WHILE LPAREN condition RPAREN LBRACE statements RBRACE"""
            assert len(tree.children) == 7 and \
                   isinstance(tree.child(0), Terminal) and tree.child(0).text == 'while' and \
                   isinstance(tree.child(1), Terminal) and tree.child(1).text == '(' and \
                   isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Condition' and \
                   isinstance(tree.child(3), Terminal) and tree.child(3).text == ')' and \
                   isinstance(tree.child(4), Terminal) and tree.child(4).text == '{' and \
                   isinstance(tree.child(5), NonTerminal) and tree.child(5).type == 'Statements' and \
                   isinstance(tree.child(6), Terminal) and tree.child(6).text == '}', 'Syntax error'
            while True:
                translate(tree.child(2))  # Condition
                condition = tree.child(2).value
                if not condition:
                    loop_flag = False
                    break
                loop_flag = True
                translate(tree.child(5))  # Statements
                if break_flag:
                    break_flag = False
                    loop_flag = False
                    break
            return
        # For
        elif tree.type == 'For':
            """for : FOR LPAREN assignment SEMICOLON condition SEMICOLON selfvar RPAREN LBRACE statements RBRACE"""
            assert len(tree.children) == 11 and \
                   isinstance(tree.child(0), Terminal) and tree.child(0).text == 'for' and \
                   isinstance(tree.child(1), Terminal) and tree.child(1).text == '(' and \
                   isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Assignment' and \
                   isinstance(tree.child(3), Terminal) and tree.child(3).text == ';' and \
                   isinstance(tree.child(4), NonTerminal) and tree.child(4).type == 'Condition' and \
                   isinstance(tree.child(5), Terminal) and tree.child(5).text == ';' and \
                   isinstance(tree.child(6), NonTerminal) and tree.child(6).type == 'SelfVar' and \
                   isinstance(tree.child(7), Terminal) and tree.child(7).text == ')' and \
                   isinstance(tree.child(8), Terminal) and tree.child(8).text == '{' and \
                   isinstance(tree.child(9), NonTerminal) and tree.child(9).type == 'Statements' and \
                   isinstance(tree.child(10), Terminal) and tree.child(10).text == '}', 'Syntax error'
            translate(tree.child(2))  # Assignment
            while True:
                translate(tree.child(4))  # Condition
                condition = tree.child(4).value
                if not condition:
                    loop_flag = False
                    break
                loop_flag = True
                translate(tree.child(9))  # Statements
                if break_flag:
                    break_flag = False
                    loop_flag = False
                    break
                translate(tree.child(6))  # SelfVar
            return
        # Break
        elif tree.type == 'Break':
            assert len(tree.children) == 1 and \
                   isinstance(tree.child(0), Terminal) and tree.child(0).text == 'break', 'Syntax error'
            assert loop_flag, 'Syntax error: use "break" in non-loop statements'
            break_flag = True
            return

    # 深度优先遍历语法树
    for child in tree.children:
        translate(child)

    # Translation
    if isinstance(tree, NonTerminal):
        # Assignment
        if tree.type == 'Assignment':
            '''assignment -> leftval ASSIGN expr'''
            assert len(tree.children) == 3, 'Syntax error'
            assert isinstance(tree.child(0), LeftValue) and \
                   isinstance(tree.child(1), Terminal) and tree.child(1).text == '=' and \
                   isinstance(tree.child(2), NonTerminal) and tree.child(2).type in ('Expr', 'Array'), 'Syntax error'
            value = tree.child(2).value
            tree.child(0).value = value
            set_value(var_table, tree.child(0).id, value)  # update var_table
        # LeftVal
        elif tree.type == 'LeftVal':
            """leftval -> leftval1 LLIST expr RLIST | ID"""
            assert len(tree.children) == 1 or len(tree.children) == 4, 'Syntax error'
            if len(tree.children) == 1:
                assert isinstance(tree.child(0), ID), 'Syntax error'
                # { leftval.id = (ID.id, None); leftval.value = ID.value; }
                tree.id = (tree.child(0).id, None)
                tree.value = tree.child(0).value
            elif len(tree.children) == 4:
                assert isinstance(tree.child(0), LeftValue) and \
                       isinstance(tree.child(1), Terminal) and tree.child(1).text == '[' and \
                       isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Expr' and \
                       isinstance(tree.child(3), Terminal) and tree.child(3).text == ']', 'Syntax error'
                # { leftval.id = (leftval1.id, expr.value); leftval.value = get_value(var_table, leftval.id); }
                tree.id = (tree.child(0).id, tree.child(2).value)
                tree.value = get_value(var_table, tree.id)
        # Expr
        elif tree.type == 'Expr':
            '''expr : expr '+' term | expr '-' term | term'''
            assert len(tree.children) == 1 or len(tree.children) == 3, 'Syntax error'
            if len(tree.children) == 1:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Term', 'Syntax error'
                tree.value = tree.child(0).value
            elif len(tree.children) == 3:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Expr' and \
                       isinstance(tree.child(1), Terminal) and (tree.child(1).text in ('+', '-')) and \
                       isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Term', 'Syntax error'
                op = tree.child(1).text
                if op == '+':
                    value = tree.child(0).value + tree.child(2).value
                else:
                    value = tree.child(0).value - tree.child(2).value
                tree.value = value
        # Term
        elif tree.type == 'Term':
            '''term : term '*' factor | term '/' factor | factor'''
            assert len(tree.children) == 1 or len(tree.children) == 3, 'Syntax error'
            if len(tree.children) == 1:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Factor', 'Syntax error'
                tree.value = tree.child(0).value
            elif len(tree.children) == 3:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Term' and \
                       isinstance(tree.child(1), Terminal) and (tree.child(1).text in ('*', '/', '//')) and \
                       isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Factor', 'Syntax error'
                op = tree.child(1).text
                if op == '*':
                    value = tree.child(0).value * tree.child(2).value
                else:
                    assert tree.child(2).value != 0, '除数不能为0'
                    if op == '//':
                        value = tree.child(0).value // tree.child(2).value
                    else:
                        value = tree.child(0).value / tree.child(2).value
                tree.value = value
        # Factor
        elif tree.type == 'Factor':
            """factor : leftval | NUMBER | len | '(' expr ')'"""
            assert len(tree.children) == 1 or len(tree.children) == 3, 'Syntax error'
            if len(tree.children) == 1:
                assert isinstance(tree.child(0), LeftValue) or \
                       (isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Len') or \
                       isinstance(tree.child(0), Number), 'Syntax error'
                if isinstance(tree.child(0), LeftValue):
                    # { leftval.value = get_value(var_table, leftval.id); factor.value = leftval.value; }
                    value = get_value(var_table, tree.child(0).id)  # search for var_table
                    assert value is not None, f'符号 "{tree.child(0).id}" 未定义'
                    tree.child(0).value = value
                    tree.value = value
                if isinstance(tree.child(0), NonTerminal):
                    # { factor.value = len.value; }
                    tree.value = tree.child(0).value
                else:
                    tree.value = tree.child(0).value
            elif len(tree.children) == 3:
                assert isinstance(tree.child(0), Terminal) and tree.child(0).text == '(' and \
                       isinstance(tree.child(1), NonTerminal) and tree.child(1).type == 'Expr' and \
                       isinstance(tree.child(2), Terminal) and tree.child(2).text == ')', 'Syntax error'
                tree.value = tree.child(1).value
        # Exprs
        elif tree.type == 'Exprs':
            """exprs : exprs ',' expr | expr"""
            assert len(tree.children) == 1 or len(tree.children) == 3, 'Syntax error'
            if len(tree.children) == 1:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Expr', 'Syntax error'
                tree.value = [tree.child(0).value]
            elif len(tree.children) == 3:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Exprs' and \
                       isinstance(tree.child(1), Terminal) and tree.child(1).text == ',' and \
                       isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Expr', 'Syntax error'
                tree.value = tree.child(0).value + [tree.child(2).value]
        # Print
        elif tree.type == 'Print':
            ''' print : PRINT '(' exprs ')' | PRINT '(' ')' '''
            assert (len(tree.children) == 4 and
                    isinstance(tree.child(0), Terminal) and tree.child(0).text == 'print' and
                    isinstance(tree.child(1), Terminal) and tree.child(1).text == '(' and
                    isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Exprs' and
                    isinstance(tree.child(3), Terminal) and tree.child(3).text == ')') or \
                   (len(tree.children) == 3 and
                    isinstance(tree.child(0), Terminal) and tree.child(0).text == 'print' and
                    isinstance(tree.child(1), Terminal) and tree.child(1).text == '(' and
                    isinstance(tree.child(2), Terminal) and tree.child(2).text == ')'), 'Syntax error'
            if len(tree.children) == 4:
                print(*tree.child(2).value)
            else:
                print()
        # Len
        elif tree.type == 'Len':
            """len -> LEN '(' expr ')'  { len.value = len(expr.value) }"""
            assert len(tree.children) == 4 and \
                   isinstance(tree.child(0), Terminal) and tree.child(0).text == 'len' and \
                   isinstance(tree.child(1), Terminal) and tree.child(1).text == '(' and \
                   isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Expr' and \
                   isinstance(tree.child(3), Terminal) and tree.child(3).text == ')', 'Syntax error'
            tree.value = len(tree.child(2).value)
        # Array
        elif tree.type == 'Array':
            ''' array : '[' exprs ']' | '[' ']' '''
            assert (len(tree.children) == 3 and
                    isinstance(tree.child(0), Terminal) and tree.child(0).text == '[' and
                    isinstance(tree.child(1), NonTerminal) and tree.child(1).type == 'Exprs' and
                    isinstance(tree.child(2), Terminal) and tree.child(2).text == ']') or \
                   (len(tree.children) == 2 and
                    isinstance(tree.child(0), Terminal) and tree.child(0).text == '[' and
                    isinstance(tree.child(1), Terminal) and tree.child(1).text == ']'), 'Syntax error'
            if len(tree.children) == 3:
                tree.value = list(tree.child(1).value)
            else:
                tree.value = []
        # SelfVar
        elif tree.type == 'SelfVar':
            """{ leftval.value = leftval.value + 1; set_value(var_table, leftval.id, leftval.value); }
               { leftval.value = leftval.value - 1; set_value(var_table, leftval.id, leftval.value); }"""
            assert len(tree.children) == 2 and \
                   isinstance(tree.child(0), LeftValue) and \
                   isinstance(tree.child(1), Terminal) and tree.child(1).text in ('++', '--'), 'Syntax error'
            if tree.child(1).text == '++':
                tree.child(0).value = tree.child(0).value + 1
            elif tree.child(1).text == '--':
                tree.child(0).value = tree.child(0).value - 1
            set_value(var_table, tree.child(0).id, tree.child(0).value)
        # Condition
        elif tree.type == 'Condition':
            assert len(tree.children) == 3 or len(tree.children) == 1, 'Syntax error'
            if len(tree.children) == 3:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Expr' and \
                       isinstance(tree.child(1), Terminal) and \
                       tree.child(1).text in ('<', '<=', '>', '>=', '==', '!=') and \
                       isinstance(tree.child(2), NonTerminal) and tree.child(2).type == 'Expr', 'Syntax error'
                if tree.child(1).text == '<':
                    tree.value = tree.child(0).value < tree.child(2).value
                elif tree.child(1).text == '<=':
                    tree.value = tree.child(0).value <= tree.child(2).value
                elif tree.child(1).text == '>':
                    tree.value = tree.child(0).value > tree.child(2).value
                elif tree.child(1).text == '>=':
                    tree.value = tree.child(0).value >= tree.child(2).value
                elif tree.child(1).text == '==':
                    tree.value = tree.child(0).value == tree.child(2).value
                elif tree.child(1).text == '!=':
                    tree.value = tree.child(0).value != tree.child(2).value
            elif len(tree.children) == 1:
                assert isinstance(tree.child(0), NonTerminal) and tree.child(0).type == 'Expr', 'Syntax error'
                tree.value = bool(tree.child(0).value)
