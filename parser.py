import lexer
from globalTypes import *
from lexer import getToken, globales as lexer_globales, TokenType


# Parser descendente recursivo para C-. Genera un AST enriquecido con números de línea.


class ASTNode:
    def __init__(self, kind, lexeme=None):
        self.kind = kind
        self.lexeme = lexeme
        self.children = []
        # Capturamos línea actual de lexer
        self.lineno = lexer.lineno

    def add(self, node):
        if node:
            if isinstance(node, list):
                for n in node:
                    self.children.append(n)
            else:
                self.children.append(node)

    def __repr__(self, lvl=0):
        pad = '  ' * lvl
        s = f"{pad}{self.kind}"
        if self.lexeme is not None:
            s += f": {self.lexeme}"
        s += "\n"
        for c in self.children:
            s += c.__repr__(lvl+1)
        return s

# Globals
programa = ''
lineas = []
token = None
lexeme = None
_error = False

def globales(prog, pos, lng):
    lexer_globales(prog, pos, lng)
    global programa, lineas
    programa = prog
    lineas = programa.splitlines()

# Error con contexto y caret

def error(msg):
    global _error
    _error = True
    ln = lexer.lineno
    texto = lineas[ln-1] if 0 <= ln-1 < len(lineas) else ''
    print(f"Línea {ln}: {msg}")
    if texto:
        print(texto)
        idx = texto.find(lexeme) if lexeme else -1
        if idx >= 0:
            print(' ' * idx + '^')

# Avanza token, ignorando comentarios

def advance():
    global token, lexeme
    token, lexeme = getToken(False)
    while token == TokenType.COMMENT or (token == TokenType.ERROR and isinstance(lexeme, str) and lexeme.startswith('/*')):
        token, lexeme = getToken(False)

# Recuperación pánico

def panic_recovery(sync):
    while token not in sync and token != TokenType.ENDFILE:
        advance()

# Match con recover

def match(expected):
    global token
    if token == expected:
        advance()
    else:
        error(f"Se esperaba {expected.name}, se encontró {token.name}")
        panic_recovery({TokenType.SEMI, TokenType.RBRACE})
        if token == expected:
            advance()

# Entry point

def parser(imprime=True):
    global _error, token
    advance()
    root = program()
    # Última debe ser main
    if root.children:
        last = root.children[-1]
        if not (isinstance(last, ASTNode) and last.kind=='fun_decl' and last.children[1].lexeme=='main'):
            error("La última declaración debe ser la función main")
    if token != TokenType.ENDFILE:
        error("Tokens sobrantes después de EOF")
    if imprime:
        print(root)
    return root

# 1. program → declaration-list

def program():
    node = ASTNode('program')
    while token in {TokenType.INT, TokenType.VOID}:
        node.add(declaration())
    return node

# 2. declaration → var-declaration | fun-declaration

def declaration():
    tipo = lexeme
    match(token)
    if token != TokenType.ID:
        error("se esperaba identificador en declaration")
        panic_recovery({TokenType.SEMI})
        return ASTNode('error_decl')
    name = lexeme
    match(TokenType.ID)
    # función
    if token == TokenType.LPAREN:
        fn = ASTNode('fun_decl')
        fn.add(ASTNode('type_specifier', tipo))
        fn.add(ASTNode('ID', name))
        match(TokenType.LPAREN)
        fn.add(params())
        match(TokenType.RPAREN)
        fn.add(compound_stmt())
        return fn
    # variable(s)
    decls = []
    def add_var(nm, arr_size=None):
        v = ASTNode('var_decl')
        v.add(ASTNode('type_specifier', tipo))
        v.add(ASTNode('ID', nm))
        if arr_size is not None:
            v.add(ASTNode('NUM', arr_size))
        decls.append(v)
    # arreglo
    if token == TokenType.LBRACKET:
        match(TokenType.LBRACKET)
        sz = lexeme
        match(TokenType.NUM)
        match(TokenType.RBRACKET)
        add_var(name, sz)
    else:
        add_var(name)
    while token == TokenType.COMMA:
        match(TokenType.COMMA)
        if token != TokenType.ID:
            error("Se esperaba ID después de coma en var_decl")
            break
        nm2 = lexeme
        match(TokenType.ID)
        if token == TokenType.LBRACKET:
            match(TokenType.LBRACKET)
            sz2 = lexeme
            match(TokenType.NUM)
            match(TokenType.RBRACKET)
            add_var(nm2, sz2)
        else:
            add_var(nm2)
    match(TokenType.SEMI)
    return decls[0] if len(decls)==1 else decls

# 3. params → param-list | void

def params():
    node = ASTNode('params')
    if token == TokenType.VOID:
        node.add(ASTNode('VOID', lexeme))
        match(TokenType.VOID)
    elif token != TokenType.RPAREN:
        node.add(param_list())
    return node

# 4. param-list

def param_list():
    node = ASTNode('param_list')
    node.add(param())
    while token == TokenType.COMMA:
        match(TokenType.COMMA)
        node.add(param())
    return node

# 5. param → type-specifier ID [ ]

def param():
    node = ASTNode('param')
    node.add(ASTNode('type_specifier', lexeme))
    match(token)
    if token == TokenType.ID:
        node.add(ASTNode('ID', lexeme))
        match(TokenType.ID)
    if token == TokenType.LBRACKET:
        match(TokenType.LBRACKET)
        match(TokenType.RBRACKET)
    return node

# 6. compound-stmt → { local-declarations statement-list }

def compound_stmt():
    node = ASTNode('compound_stmt')
    match(TokenType.LBRACE)
    node.add(local_declarations())
    node.add(statement_list())
    match(TokenType.RBRACE)
    return node

# 7. local-declarations

def local_declarations():
    node = ASTNode('local_declarations')
    while token in {TokenType.INT, TokenType.VOID}:
        decl = declaration()
        if isinstance(decl, list):
            # Handle multiple declarations
            for d in decl:
                node.add(d)
        else:
            node.add(decl)
    return node

# 8. statement-list

def statement_list():
    node = ASTNode('statement_list')
    while token not in {TokenType.RBRACE, TokenType.ENDFILE}:
        node.add(statement())
    return node

# 9. statement → expression-stmt | compound-stmt | selection-stmt | iteration-stmt | return-stmt

def statement():
    if token == TokenType.LBRACE:
        return compound_stmt()
    if token == TokenType.IF:
        return selection_stmt()
    if token == TokenType.WHILE:
        return iteration_stmt()
    if token == TokenType.RETURN:
        return return_stmt()
    return expression_stmt()

# 10. expression-stmt

def expression_stmt():
    node = ASTNode('expression_stmt')
    if token != TokenType.SEMI:
        node.add(expression())
    match(TokenType.SEMI)
    return node

# 11. selection-stmt

def selection_stmt():
    node = ASTNode('selection_stmt')
    match(TokenType.IF)
    match(TokenType.LPAREN)
    node.add(expression())
    match(TokenType.RPAREN)
    node.add(statement())
    if token == TokenType.ELSE:
        match(TokenType.ELSE)
        node.add(statement())
    return node

# 12. iteration-stmt

def iteration_stmt():
    node = ASTNode('iteration_stmt')
    match(TokenType.WHILE)
    match(TokenType.LPAREN)
    node.add(expression())
    match(TokenType.RPAREN)
    node.add(statement())
    return node

# 13. return-stmt

def return_stmt():
    node = ASTNode('return_stmt')
    match(TokenType.RETURN)
    if token != TokenType.SEMI:
        node.add(expression())
    match(TokenType.SEMI)
    return node

# 14. expression → var = expression | simple-expression

def expression():
    node = simple_expression()
    if token == TokenType.EQ:
        if not (isinstance(node, ASTNode) and node.kind=='var'):
            error("La parte izquierda de la asignación debe ser una variable")
        
        # Store the entire var node (including index if present)
        var_node = node
        match(TokenType.EQ)
        rhs = expression()
        
        # Create assignment node
        assign = ASTNode('assign', var_node.lexeme)
        
        # If the variable has an index (array assignment), add it first
        if var_node.children:  # Array assignment: var[index] = value
            assign.add(rhs)                   # Add value FIRST
            assign.add(var_node.children[0])  # Add index SECOND
        else:  # Simple assignment: var = value
            assign.add(rhs)
        
        return assign
    return node

# 15. simple-expression

def simple_expression():
    node = additive_expression()
    if token in {TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE, TokenType.EQEQ, TokenType.NE}:
        op = lexeme
        match(token)
        rel = ASTNode('relop', op)
        rel.add(node)
        rel.add(additive_expression())
        return rel
    return node

# 16. additive-expression

def additive_expression():
    node = term()
    while token in {TokenType.PLUS, TokenType.MINUS}:
        op = lexeme
        match(token)
        addn = ASTNode('addop', op)
        addn.add(node)
        addn.add(term())
        node = addn
    return node

# 17. term

def term():
    node = factor()
    while token in {TokenType.TIMES, TokenType.OVER}:
        op = lexeme
        match(token)
        mul = ASTNode('mulop', op)
        mul.add(node)
        mul.add(factor())
        node = mul
    return node

# 18. factor

def factor():
    if token == TokenType.LPAREN:
        match(TokenType.LPAREN)
        node = expression()
        match(TokenType.RPAREN)
        return node
    if token == TokenType.NUM:
        v = lexeme; match(TokenType.NUM)
        return ASTNode('NUM', v)
    if token == TokenType.ID:
        name = lexeme; match(TokenType.ID)
        # 1) var indexada
        if token == TokenType.LBRACKET:
            match(TokenType.LBRACKET)
            idx = expression()
            match(TokenType.RBRACKET)
            var_node = ASTNode('var', name)
            var_node.add(idx)
            return var_node
        # 2) llamada
        if token == TokenType.LPAREN:
            call = ASTNode('call', name)
            match(TokenType.LPAREN)
            call.add(args())
            match(TokenType.RPAREN)
            return call
        # 3) var simple
        return ASTNode('var', name)
    error("Error en factor")
    advance()
    return ASTNode('error_factor')


# 19. args → arg-list | empty

def args():
    node = ASTNode('args')
    if token != TokenType.RPAREN:
        node.add(arg_list())
    return node

# 20. arg-list

def arg_list():
    node = ASTNode('arg_list')
    node.add(expression())
    while token == TokenType.COMMA:
        match(TokenType.COMMA)
        node.add(expression())
    return node
