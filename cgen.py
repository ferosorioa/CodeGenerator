# cgen.py

from globalTypes import *  # Para tipos y enums definidos previamente

class CodeEmitter:
    def __init__(self, file):
        self.file = file
        self.label_count = 0

    def emit(self, code):
        self.file.write(code + '\n')

    def emit_comment(self, comment):
        self.emit(f"# {comment}")

    def new_label(self, prefix="L"):
        label = f"{prefix}{self.label_count}"
        self.label_count += 1
        return label

#variables globales
symbol_table={}
offset_counter=0
register_counter = 0

def codeGen(tree, filename):
    with open(filename, 'w') as f:
        emitter = CodeEmitter(f)

        emitter.emit(".data")
        emitter.emit("newline: .asciiz \"\\n\"")
        emitter.emit(".text")
        emitter.emit(".globl main")

        generate_code(tree, emitter)

def generate_code(node, emitter):

    if node is None:
        return

    if node.kind == 'program':
        for child in node.children:
            generate_code(child, emitter)

    elif node.kind == 'fun_decl':
        gen_function(node, emitter)
    
    elif node.kind =='compound_stmt':
        gen_compound_stmt(node,emitter)
    
    elif node.kind=='var_decl':
        gen_var_decl(node,emitter)

    elif node.kind == 'expression_stmt':
        gen_expression_stmt(node, emitter)

    # Agregaremos más tipos aquí como compound_stmt, assign, call, etc.


#Convierte a las funciones en las instrucciones MIPS para funciones. Guarda las variables de estas funciones en un stack local.
#Un stack personal por función
def gen_function(node, emitter):
    global symbol_table, offset_counter
    symbol_table = {}          # Reset tabla de símbolos
    offset_counter = 0         # Reset offset local
    name = node.children[1].lexeme  # e.g., 'main' o 'bigTest'
    emitter.emit(f"{name}:")
    emitter.emit_comment("Prolog")
    emitter.emit("sw $ra, 0($sp)")
    emitter.emit("sw $fp, -4($sp)")
    emitter.emit("move $fp, $sp")
    emitter.emit("addi $sp, $sp, -8")  # Reservar espacio mínimo

    for child in node.children:
        generate_code(child, emitter)

    emitter.emit_comment("Epilog")
    emitter.emit("move $sp, $fp")
    emitter.emit("lw $fp, -4($sp)")
    emitter.emit("lw $ra, 0($sp)")
    emitter.emit("jr $ra")

#Analiza los compound statements "{ }". MArca su inicio y su fin y se supone que llama a todo lo que esta dentro de forma recursiva.
def gen_compound_stmt(node, emitter):
    emitter.emit_comment("Inicio de compound_stmt")
    local_decls = node.children[0]
    stmt_list = node.children[1]

    # Procesar declaraciones locales
    for decl in local_decls.children:
        generate_code(decl, emitter)

    # Procesar lista de sentencias
    for stmt in stmt_list.children:
        generate_code(stmt, emitter)

    emitter.emit_comment("Fin de compound_stmt")

def gen_var_decl(node, emitter):
    global offset_counter
    name = node.children[1].lexeme

    # Ver si es un arreglo
    size = 1
    if len(node.children) == 3 and node.children[2].kind == 'NUM':
        size = int(node.children[2].lexeme)

    emitter.emit_comment(f"Declaración de variable: {name} (size = {size})")
    total_size = size * 4
    offset_counter -= total_size
    symbol_table[name] = offset_counter
    emitter.emit(f"addi $sp, $sp, -{total_size}  # Reservar espacio para {name}")

#Vale la pena revisar.
def gen_expression_stmt(node, emitter):
    emitter.emit_comment("Inicio de expression_stmt")
    if node.children:
        gen_expression(node.children[0], emitter)
    emitter.emit_comment("Fin de expression_stmt")

def gen_expression(node, emitter):
    global register_counter
    emitter.emit_comment("Inicio de expression")
    if node.kind == 'NUM':
        reg = f"$t{register_counter % 10}"
        register_counter += 1
        emitter.emit(f"li {reg}, {node.lexeme}")
        return reg

    elif node.kind == 'var':
        name = node.lexeme
        offset = symbol_table.get(name)
        reg = f"$t{register_counter % 10}"
        register_counter += 1
        if offset is not None:
            emitter.emit(f"lw {reg}, {offset}($fp)")
        else:
            emitter.emit_comment(f"[Error] Variable no encontrada: {name}")
        return reg

    elif node.kind == 'addop':
        left = gen_expression(node.children[0], emitter)
        right = gen_expression(node.children[1], emitter)
        reg = f"$t{register_counter % 10}"
        register_counter += 1
        op = 'add' if node.lexeme == '+' else 'sub'
        emitter.emit(f"{op} {reg}, {left}, {right}")
        return reg

    elif node.kind == 'mulop':
        left = gen_expression(node.children[0], emitter)
        right = gen_expression(node.children[1], emitter)
        reg = f"$t{register_counter % 10}"
        register_counter += 1
        op = 'mul' if node.lexeme == '*' else 'div'
        emitter.emit(f"{op} {reg}, {left}, {right}")
        return reg

    elif node.kind == 'assign':
        name = node.lexeme
        offset = symbol_table.get(name)
        result = gen_expression(node.children[0], emitter)
        if offset is not None:
            emitter.emit(f"sw {result}, {offset}($fp)")
        else:
            emitter.emit_comment(f"[Error] Variable no encontrada para asignación: {name}")
        return result



# === Funciones necesarias para traducir el AST a MIPS ===

# gen_compound_stmt(node, emitter)
# Traduce un bloque de código `{ ... }`.
# - Llama a gen_var_decl para reservar espacio en stack
# - Luego traduce cada statement del bloque con generate_code

# gen_var_decl(node, emitter)
# Traduce declaraciones de variables locales.
# - Reserva espacio en el stack
# - Actualiza la tabla de símbolos con el offset de cada variable

# gen_expression_stmt(node, emitter)
# Traduce una expresión como statement. Ej: `x = a + b;`
# - Solo llama a gen_expression y descarta el resultado (salvo si es asignación)

# gen_assign(node, emitter)
# Traduce una asignación `x = expr`.
# - Evalúa el lado derecho (gen_expression)
# - Busca el offset de `x` y guarda el resultado con sw

# gen_expression(node, emitter)
# Traduce una expresión general: puede ser NUM, var, addop, mulop, call, etc.
# - Retorna el registro donde queda el resultado
# - Puede llamar recursivamente a gen_addop, gen_mulop, etc.

# gen_var(node, emitter)
# Traduce una variable:
# - Si es simple (`x`), la carga desde stack (lw)
# - Si es un arreglo indexado (`data[i]`), calcula offset dinámico y hace lw

# gen_num(node, emitter)
# Traduce un número constante `NUM: 5` → `li $tX, 5`
# - Retorna el registro donde quedó el número

# gen_addop(node, emitter)
# Traduce una suma o resta: `a + b`, `x - y`
# - Evalúa ambos operandos y aplica `add` o `sub`

# gen_mulop(node, emitter)
# Traduce una multiplicación o división: `a * b`, `x / y`
# - Evalúa ambos lados y aplica `mul` o `div`

# gen_relop(node, emitter)
# Traduce una comparación relacional: `<`, `>`, `!=`, etc.
# - Usa instrucciones como `slt`, `beq`, `bne`, `bge`, etc.
# - Retorna un registro con 1 o 0

# gen_selection_stmt(node, emitter)
# Traduce una sentencia `if (...) { ... } else { ... }`
# - Evalúa condición
# - Genera etiquetas para true, false, y final
# - Usa saltos `beq`, `bne`, `j`

# gen_iteration_stmt(node, emitter)
# Traduce `while (...) { ... }`
# - Genera etiquetas de entrada y fin
# - Evalúa la condición al inicio de cada vuelta
# - Salta fuera del bucle si la condición falla

# gen_return_stmt(node, emitter)
# Traduce `return expr;` o `return;`
# - Evalúa la expresión si existe
# - Guarda el resultado en `$v0`
# - Salta a la instrucción de retorno

# gen_call(node, emitter)
# Traduce una llamada a función
# - Evalúa cada argumento y los pone en $a0-$a3
# - Usa `jal` para saltar
# - El resultado está en `$v0`
