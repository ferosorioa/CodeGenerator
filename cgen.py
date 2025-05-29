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
current_function_name = ""  # Track current function for epilogue labels


def codeGen(tree, filename):
    with open(filename, 'w') as f:
        emitter = CodeEmitter(f)

        emitter.emit(".data")
        emitter.emit("newline: .asciiz \"\\n\"")
        emitter.emit("")
        emitter.emit(".text")
        
        # First pass: declare all functions as global
        for child in tree.children:
            if child.kind == 'fun_decl':
                func_name = child.children[1].lexeme
                emitter.emit(f".globl {func_name}")
        
        emitter.emit("")
        
        # Second pass: generate main first, then other functions
        # Find and generate main function first
        main_func = None
        other_funcs = []
        
        for child in tree.children:
            if child.kind == 'fun_decl':
                if child.children[1].lexeme == 'main':
                    main_func = child
                else:
                    other_funcs.append(child)
        
        # Generate main first
        if main_func:
            generate_code(main_func, emitter)
        
        # Then generate other functions
        for func in other_funcs:
            generate_code(func, emitter)

def generate_code(node, emitter):
    if node is None:
            return

    if node.kind == 'program':
        for child in node.children:
            generate_code(child, emitter)

    elif node.kind == 'fun_decl':
        gen_function(node, emitter)
    
    elif node.kind == 'compound_stmt':
        gen_compound_stmt(node, emitter)
    
    elif node.kind == 'var_decl':
        gen_var_decl(node, emitter)

    elif node.kind == 'expression_stmt':
        gen_expression_stmt(node, emitter)
    
    elif node.kind == 'selection_stmt':
        gen_selection_stmt(node, emitter)
    
    elif node.kind == 'iteration_stmt':
        gen_iteration_stmt(node, emitter)
    
    elif node.kind == 'return_stmt':
        gen_return_stmt(node, emitter)
    
    elif node.kind == 'local_declarations':
        # Procesar cada declaración local
        for child in node.children:
            generate_code(child, emitter)
    
    elif node.kind == 'statement_list':
        # Procesar cada statement
        for child in node.children:
            generate_code(child, emitter)
    
    # Don't process these nodes - they're handled by their parents
    elif node.kind in ['type_specifier', 'ID', 'params', 'VOID', 'param_list', 'param', 'args', 'arg_list']:
        pass
    
    # Expressions - normally not independent statements
    elif node.kind in ['assign', 'addop', 'mulop', 'relop', 'var', 'NUM', 'call']:
        gen_expression(node, emitter)
    
    else:
        emitter.emit_comment(f"[Warning] Tipo de nodo no manejado en generate_code: {node.kind}")



#Convierte a las funciones en las instrucciones MIPS para funciones. Guarda las variables de estas funciones en un stack local.
#Un stack personal por función

def gen_function(node, emitter):
    global symbol_table, offset_counter, current_function_name
    symbol_table = {}
    offset_counter = 0
    
    name = node.children[1].lexeme
    current_function_name = name  # Set the current function name
    
    emitter.emit(f"{name}:")
    emitter.emit_comment("Prolog")
    
    # For main function, we need to be more careful with initial stack
    if name == "main":
        # Don't save $ra for main since it's the entry point
        emitter.emit("move $fp, $sp")  # Set frame pointer
        emitter.emit("addi $sp, $sp, -4")  # Just reserve minimal space
    else:
        # For other functions, save return address and old frame pointer
        emitter.emit("addi $sp, $sp, -8")  # Make space first
        emitter.emit("sw $ra, 4($sp)")     # Save return address
        emitter.emit("sw $fp, 0($sp)")     # Save frame pointer
        emitter.emit("move $fp, $sp")      # Set new frame pointer
        emitter.emit("addi $fp, $fp, 8")   # Adjust fp to point to the original sp
    
    # Process parameters if any
    params_node = node.children[2]
    if params_node.children and params_node.children[0].kind != 'VOID':
        param_offset = 0  # Parameters are at positive offsets from $fp
        for i, param in enumerate(params_node.children[0].children):
            param_name = param.children[1].lexeme
            symbol_table[param_name] = param_offset
            param_offset += 4
            emitter.emit_comment(f"Parámetro {param_name} en offset {symbol_table[param_name]}")
    
    # Generate function body
    for child in node.children:
        if child.kind == 'compound_stmt':
            generate_code(child, emitter)
    
    # Unique epilogue label for this function
    emitter.emit(f"{name}_epilogue:")
    emitter.emit_comment("Epilog")
    
    if name == "main":
        # For main, just exit
        emitter.emit("li $v0, 10")
        emitter.emit("syscall")
    else:
        # Restore everything
        emitter.emit("addi $sp, $fp, -8")  # Restore sp to where we saved registers
        emitter.emit("lw $fp, 0($sp)")     # Restore frame pointer
        emitter.emit("lw $ra, 4($sp)")     # Restore return address
        emitter.emit("addi $sp, $sp, 8")   # Clean up stack
        emitter.emit("jr $ra")
    
    emitter.emit("")  # Empty line for readability

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

    # elif node.kind == 'var':
    #     name = node.lexeme
    #     offset = symbol_table.get(name)
    #     reg = f"$t{register_counter % 10}"
    #     register_counter += 1
    #     if offset is not None:
    #         emitter.emit(f"lw {reg}, {offset}($fp)")
    #     else:
    #         emitter.emit_comment(f"[Error] Variable no encontrada: {name}")
    #     return reg
    elif node.kind == 'var':
        name = node.lexeme
        offset = symbol_table.get(name)
        reg = f"$t{register_counter % 10}"
        register_counter += 1
        
        if len(node.children) > 0:  # Array access
            # Calculate array index
            index_reg = gen_expression(node.children[0], emitter)
            offset_reg = f"$t{register_counter % 10}"
            register_counter += 1
            
            # Calculate byte offset (index * 4)
            emitter.emit(f"sll {offset_reg}, {index_reg}, 2")
            
            # Calculate address
            if offset is not None:
                emitter.emit(f"addi {offset_reg}, {offset_reg}, {offset}")
                emitter.emit(f"add {offset_reg}, {offset_reg}, $fp")
                emitter.emit(f"lw {reg}, 0({offset_reg})")
            else:
                emitter.emit_comment(f"[Error] Array no encontrado: {name}")
        else:  # Simple variable
            if offset is not None:
                emitter.emit(f"lw {reg}, {offset}($fp)")
            else:
                emitter.emit_comment(f"[Error] Variable no encontrada: {name}")
        return reg
    
    # OTRA DEF de var, diferencia entre variable simple y arreglo
    # elif node.kind == 'var':
    #     name = node.lexeme
    #     offset = symbol_table.get(name)
    #     reg = f"$t{register_counter % 10}"
    #     register_counter += 1
        
    #     if len(node.children) > 0:  # Array access
    #         # Calculate array index
    #         index_reg = gen_expression(node.children[0], emitter)
    #         offset_reg = f"$t{register_counter % 10}"
    #         register_counter += 1
            
    #         # Calculate byte offset (index * 4)
    #         emitter.emit(f"sll {offset_reg}, {index_reg}, 2")
            
    #         # Calculate address
    #         if offset is not None:
    #             emitter.emit(f"addi {offset_reg}, {offset_reg}, {offset}")
    #             emitter.emit(f"add {offset_reg}, {offset_reg}, $fp")
    #             emitter.emit(f"lw {reg}, 0({offset_reg})")
    #         else:
    #             emitter.emit_comment(f"[Error] Array no encontrado: {name}")
    #     else:  # Simple variable
    #         if offset is not None:
    #             emitter.emit(f"lw {reg}, {offset}($fp)")
    #         else:
    #             emitter.emit_comment(f"[Error] Variable no encontrada: {name}")
    #     return reg

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
        if node.lexeme == '*':
            emitter.emit(f"mul {reg}, {left}, {right}")
        else:  # division
            emitter.emit(f"div {left}, {right}")
            emitter.emit(f"mflo {reg}")
        return reg

    elif node.kind == 'relop':
        return gen_relop(node, emitter)

    elif node.kind == 'assign':
        name = node.lexeme
        offset = symbol_table.get(name)
        result = gen_expression(node.children[0], emitter)
        
        if offset is not None:
            emitter.emit(f"sw {result}, {offset}($fp)")
        else:
            emitter.emit_comment(f"[Error] Variable no encontrada para asignación: {name}")
        return result
    
    elif node.kind == 'call':
        return gen_call(node, emitter)
    
    else:
        emitter.emit_comment(f"[Warning] Tipo de expresión no manejado: {node.kind}")
        return "$zero"



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
def gen_assign(node, emitter):
    """
    Traduce una asignación `x = expr`.
    - Evalúa el lado derecho (gen_expression)
    - Busca el offset de `x` y guarda el resultado con sw
    """
    name = node.lexeme
    offset = symbol_table.get(name)
    
    emitter.emit_comment(f"Asignación a variable: {name}")
    
    # Evaluar expresión del lado derecho
    result_reg = gen_expression(node.children[0], emitter)
    
    # Verificar si la variable es un arreglo con índice
    # En el AST, si es asignación a arreglo, necesitaríamos info adicional
    # Por ahora asumimos asignación a variable simple
    
    if offset is not None:
        emitter.emit(f"sw {result_reg}, {offset}($fp)  # {name} = expresión")
    else:
        emitter.emit_comment(f"[Error] Variable no encontrada para asignación: {name}")
    
    return result_reg

# gen_expression(node, emitter)
# Traduce una expresión general: puede ser NUM, var, addop, mulop, call, etc.
# - Retorna el registro donde queda el resultado
# - Puede llamar recursivamente a gen_addop, gen_mulop, etc.

# gen_var(node, emitter)
# Traduce una variable:
# - Si es simple (`x`), la carga desde stack (lw)
# - Si es un arreglo indexado (`data[i]`), calcula offset dinámico y hace lw
def gen_var(node, emitter):
    """
    Traduce una variable:
    - Si es simple (`x`), la carga desde stack (lw)
    - Si es un arreglo indexado (`data[i]`), calcula offset dinámico y hace lw
    """
    global register_counter
    name = node.lexeme
    offset = symbol_table.get(name)
    reg = f"$t{register_counter % 10}"
    register_counter += 1
    
    if len(node.children) > 0:  # Array access: data[i]
        emitter.emit_comment(f"Acceso a arreglo: {name}[index]")
        
        # Evaluar índice
        index_reg = gen_expression(node.children[0], emitter)
        offset_reg = f"$t{register_counter % 10}"
        register_counter += 1
        
        # Calcular offset en bytes (index * 4)
        emitter.emit(f"sll {offset_reg}, {index_reg}, 2  # index * 4")
        
        # Calcular dirección final
        if offset is not None:
            addr_reg = f"$t{register_counter % 10}"
            register_counter += 1
            # Dirección base del arreglo
            emitter.emit(f"addi {addr_reg}, $fp, {offset}")
            # Sumar el offset del índice
            emitter.emit(f"add {addr_reg}, {addr_reg}, {offset_reg}")
            # Cargar el valor
            emitter.emit(f"lw {reg}, 0({addr_reg})")
        else:
            emitter.emit_comment(f"[Error] Arreglo no encontrado: {name}")
            emitter.emit(f"li {reg}, 0  # Error: usar 0 como valor por defecto")
            
    else:  # Simple variable: x
        emitter.emit_comment(f"Cargar variable: {name}")
        if offset is not None:
            emitter.emit(f"lw {reg}, {offset}($fp)")
        else:
            emitter.emit_comment(f"[Error] Variable no encontrada: {name}")
            emitter.emit(f"li {reg}, 0  # Error: usar 0 como valor por defecto")
    
    return reg

# gen_num(node, emitter)
# Traduce un número constante `NUM: 5` → `li $tX, 5`
# - Retorna el registro donde quedó el número
def gen_num(node, emitter):
    """
    Traduce un número constante `NUM: 5` → `li $tX, 5`
    - Retorna el registro donde quedó el número
    """
    global register_counter
    reg = f"$t{register_counter % 10}"
    register_counter += 1
    emitter.emit(f"li {reg}, {node.lexeme}")
    return reg

# gen_addop(node, emitter)
# Traduce una suma o resta: `a + b`, `x - y`
# - Evalúa ambos operandos y aplica `add` o `sub`
def gen_addop(node, emitter):
    """
    Traduce una suma o resta: `a + b`, `x - y`
    - Evalúa ambos operandos y aplica `add` o `sub`
    """
    global register_counter
    
    emitter.emit_comment(f"Operación aritmética: {node.lexeme}")
    
    # Evaluar operandos
    left_reg = gen_expression(node.children[0], emitter)
    right_reg = gen_expression(node.children[1], emitter)
    
    # Resultado
    result_reg = f"$t{register_counter % 10}"
    register_counter += 1
    
    # Aplicar operación
    if node.lexeme == '+':
        emitter.emit(f"add {result_reg}, {left_reg}, {right_reg}")
    else:  # '-'
        emitter.emit(f"sub {result_reg}, {left_reg}, {right_reg}")
    
    return result_reg

# gen_mulop(node, emitter)
# Traduce una multiplicación o división: `a * b`, `x / y`
# - Evalúa ambos lados y aplica `mul` o `div`
def gen_mulop(node, emitter):
    """
    Traduce una multiplicación o división: `a * b`, `x / y`
    - Evalúa ambos lados y aplica `mul` o `div`
    """
    global register_counter
    
    emitter.emit_comment(f"Operación multiplicativa: {node.lexeme}")
    
    # Evaluar operandos
    left_reg = gen_expression(node.children[0], emitter)
    right_reg = gen_expression(node.children[1], emitter)
    
    # Resultado
    result_reg = f"$t{register_counter % 10}"
    register_counter += 1
    
    # Aplicar operación
    if node.lexeme == '*':
        emitter.emit(f"mul {result_reg}, {left_reg}, {right_reg}")
    else:  # '/'
        # División en MIPS usa registros especiales hi/lo
        emitter.emit(f"div {left_reg}, {right_reg}")
        emitter.emit(f"mflo {result_reg}  # Cociente de la división")
    
    return result_reg

# gen_relop(node, emitter)
# Traduce una comparación relacional: `<`, `>`, `!=`, etc.
# - Usa instrucciones como `slt`, `beq`, `bne`, `bge`, etc.
# - Retorna un registro con 1 o 0
def gen_relop(node, emitter):
    """
    Translates relational operators: <, >, <=, >=, ==, !=
    Returns a register containing 1 (true) or 0 (false)
    """
    global register_counter
    
    left = gen_expression(node.children[0], emitter)
    right = gen_expression(node.children[1], emitter)
    result_reg = f"$t{register_counter % 10}"
    register_counter += 1
    
    op = node.lexeme
    
    if op == '<':
        emitter.emit(f"slt {result_reg}, {left}, {right}")
    elif op == '>':
        emitter.emit(f"slt {result_reg}, {right}, {left}")
    elif op == '<=':
        # a <= b  is  !(a > b)  which is  !(b < a)
        emitter.emit(f"slt {result_reg}, {right}, {left}")
        emitter.emit(f"xori {result_reg}, {result_reg}, 1")
    elif op == '>=':
        # a >= b  is  !(a < b)
        emitter.emit(f"slt {result_reg}, {left}, {right}")
        emitter.emit(f"xori {result_reg}, {result_reg}, 1")
    elif op == '==':
        temp_reg = f"$t{register_counter % 10}"
        register_counter += 1
        emitter.emit(f"sub {temp_reg}, {left}, {right}")
        emitter.emit(f"seq {result_reg}, {temp_reg}, $zero")
    elif op == '!=':
        temp_reg = f"$t{register_counter % 10}"
        register_counter += 1
        emitter.emit(f"sub {temp_reg}, {left}, {right}")
        emitter.emit(f"sne {result_reg}, {temp_reg}, $zero")
    
    return result_reg

# gen_selection_stmt(node, emitter)
# Traduce una sentencia `if (...) { ... } else { ... }`
# - Evalúa condición
# - Genera etiquetas para true, false, y final
# - Usa saltos `beq`, `bne`, `j`
def gen_selection_stmt(node, emitter):
    """
    Translates if-else statements
    node.children[0] = condition
    node.children[1] = then statement
    node.children[2] = else statement (optional)
    """
    emitter.emit_comment("Inicio de if statement")
    
    # Evaluate condition
    cond_reg = gen_expression(node.children[0], emitter)
    
    # Generate labels
    else_label = emitter.new_label("else")
    end_label = emitter.new_label("endif")
    
    # Branch if condition is false (0)
    emitter.emit(f"beq {cond_reg}, $zero, {else_label}")
    
    # Generate then statement
    generate_code(node.children[1], emitter)
    
    # Jump to end after then block
    emitter.emit(f"j {end_label}")
    
    # Else label
    emitter.emit(f"{else_label}:")
    
    # Generate else statement if it exists
    if len(node.children) > 2:
        generate_code(node.children[2], emitter)
    
    # End label
    emitter.emit(f"{end_label}:")
    emitter.emit_comment("Fin de if statement")


# gen_iteration_stmt(node, emitter)
# Traduce `while (...) { ... }`
# - Genera etiquetas de entrada y fin
# - Evalúa la condición al inicio de cada vuelta
# - Salta fuera del bucle si la condición falla
def gen_iteration_stmt(node, emitter):
    """
    Translates while loops
    node.children[0] = condition
    node.children[1] = body statement
    """
    emitter.emit_comment("Inicio de while loop")
    
    # Generate labels
    loop_start = emitter.new_label("while")
    loop_end = emitter.new_label("endwhile")
    
    # Loop start label
    emitter.emit(f"{loop_start}:")
    
    # Evaluate condition
    cond_reg = gen_expression(node.children[0], emitter)
    
    # Exit loop if condition is false
    emitter.emit(f"beq {cond_reg}, $zero, {loop_end}")
    
    # Generate loop body
    generate_code(node.children[1], emitter)
    
    # Jump back to start
    emitter.emit(f"j {loop_start}")
    
    # End label
    emitter.emit(f"{loop_end}:")
    emitter.emit_comment("Fin de while loop")

# gen_return_stmt(node, emitter)
# Traduce `return expr;` o `return;`
# - Evalúa la expresión si existe
# - Guarda el resultado en `$v0`
# - Salta a la instrucción de retorno

def gen_return_stmt(node, emitter):
    """
    Translates return statements
    Places return value in $v0 and jumps to function epilogue
    """
    global current_function_name
    
    emitter.emit_comment("Return statement")
    
    # If there's a return value, evaluate it and put in $v0
    if node.children:
        result_reg = gen_expression(node.children[0], emitter)
        emitter.emit(f"move $v0, {result_reg}")
    
    # Jump to function-specific epilogue
    function_name = current_function_name if 'current_function_name' in globals() else "epilogue"
    emitter.emit(f"j {function_name}_epilogue")

# gen_call(node, emitter)
# Traduce una llamada a función
# - Evalúa cada argumento y los pone en $a0-$a3
# - Usa `jal` para saltar
# - El resultado está en `$v0`
def gen_call(node, emitter):
    """
    Translates function calls
    Handles built-in functions (input, output) and user-defined functions
    """
    global register_counter
    
    func_name = node.lexeme
    emitter.emit_comment(f"Llamada a función: {func_name}")
    
    # Handle built-in functions
    if func_name == "input":
        # input() reads an integer from user
        emitter.emit("li $v0, 5")  # syscall for read integer
        emitter.emit("syscall")
        result_reg = f"$t{register_counter % 10}"
        register_counter += 1
        emitter.emit(f"move {result_reg}, $v0")
        return result_reg
    
    elif func_name == "output":
        # output(x) prints an integer
        # Evaluate the argument
        if node.children and node.children[0].children:
            arg_reg = gen_expression(node.children[0].children[0].children[0], emitter)
            emitter.emit(f"move $a0, {arg_reg}")
            emitter.emit("li $v0, 1")  # syscall for print integer
            emitter.emit("syscall")
            # Print newline
            emitter.emit("la $a0, newline")
            emitter.emit("li $v0, 4")  # syscall for print string
            emitter.emit("syscall")
        return None
    
    else:
        # User-defined function
        # Evaluate and pass arguments on stack
        if node.children and node.children[0].children:
            args_list = node.children[0].children[0].children
            # Push arguments in reverse order
            for i in range(len(args_list)-1, -1, -1):
                arg_reg = gen_expression(args_list[i], emitter)
                emitter.emit("addi $sp, $sp, -4")
                emitter.emit(f"sw {arg_reg}, 0($sp)")
        
        # Call function
        emitter.emit(f"jal {func_name}")
        
        # Clean up arguments from stack
        if node.children and node.children[0].children:
            args_list = node.children[0].children[0].children
            if len(args_list) > 0:
                emitter.emit(f"addi $sp, $sp, {4 * len(args_list)}")
        
        # Result is in $v0
        result_reg = f"$t{register_counter % 10}"
        register_counter += 1
        emitter.emit(f"move {result_reg}, $v0")
        return result_reg
    

# Función mejorada para manejar asignaciones a arreglos
def gen_assign_array(node, emitter, index_reg):
    """
    Maneja asignación a elementos de arreglo: arr[i] = expr
    """
    name = node.lexeme
    offset = symbol_table.get(name)
    
    emitter.emit_comment(f"Asignación a arreglo: {name}[index]")
    
    # Evaluar expresión del lado derecho
    result_reg = gen_expression(node.children[0], emitter)
    
    if offset is not None:
        global register_counter
        offset_reg = f"$t{register_counter % 10}"
        register_counter += 1
        addr_reg = f"$t{register_counter % 10}"
        register_counter += 1
        
        # Calcular offset en bytes
        emitter.emit(f"sll {offset_reg}, {index_reg}, 2  # index * 4")
        
        # Calcular dirección
        emitter.emit(f"addi {addr_reg}, $fp, {offset}")
        emitter.emit(f"add {addr_reg}, {addr_reg}, {offset_reg}")
        
        # Guardar valor
        emitter.emit(f"sw {result_reg}, 0({addr_reg})")
    else:
        emitter.emit_comment(f"[Error] Arreglo no encontrado: {name}")
    
    return result_reg

