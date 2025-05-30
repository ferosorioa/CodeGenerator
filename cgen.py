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
current_function_name = ""  


def codeGen(tree, filename):
    with open(filename, 'w') as f:
        emitter = CodeEmitter(f)

        emitter.emit(".data")
        emitter.emit("newline: .asciiz \"\\n\"")
        emitter.emit("")
        emitter.emit(".text")
        
        # Declara las funciones globales
        for child in tree.children:
            if child.kind == 'fun_decl':
                func_name = child.children[1].lexeme
                emitter.emit(f".globl {func_name}")
        
        emitter.emit("")
        
        # Genera primero la función main y luego las demás
        main_func = None
        other_funcs = []
        
        for child in tree.children:
            if child.kind == 'fun_decl':
                if child.children[1].lexeme == 'main':
                    main_func = child
                else:
                    other_funcs.append(child)
        
        # genera la función main primero
        if main_func:
            generate_code(main_func, emitter)
        
        # genera las demás funciones
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
    
    # no processamos directamente los nodos de tipo 'ID', 'NUM', etc.
    elif node.kind in ['type_specifier', 'ID', 'params', 'VOID', 'param_list', 'param', 'args', 'arg_list']:
        pass
    
    # expresiones y operaciones
    elif node.kind in ['assign', 'addop', 'mulop', 'relop', 'var', 'NUM', 'call']:
        gen_expression(node, emitter)
    
    else:
        emitter.emit_comment(f"[Warning] Tipo de nodo no manejado en generate_code: {node.kind}")




#Un stack personal por función

def gen_function(node, emitter):
    global symbol_table, offset_counter, current_function_name
    symbol_table = {}
    offset_counter = 0
    
    name = node.children[1].lexeme
    current_function_name = name  # nombre de la función actual
    
    emitter.emit(f"{name}:")
    emitter.emit_comment("Prolog")
    
    
    if name == "main":
        emitter.emit("addi $sp, $sp, -8")      # Reserve space for $ra and $fp
        emitter.emit("sw $ra, 4($sp)")         # Save return address
        emitter.emit("sw $fp, 0($sp)")         # Save old frame pointer
        emitter.emit("move $fp, $sp")          # Set new frame pointer
    else:
        emitter.emit("addi $sp, $sp, -8")      # Make space first
        emitter.emit("sw $ra, 4($sp)")         # Save return address
        emitter.emit("sw $fp, 0($sp)")         # Save frame pointer
        emitter.emit("move $fp, $sp")          # Set new frame pointer
    
    # Procesar parámetros
    params_node = node.children[2]
    if params_node.children and params_node.children[0].kind != 'VOID':
        param_offset = 8  #parametros empiezan en 8($fp) para main, 12($fp) para otras funciones
        if params_node.children[0].kind == 'param_list':
            # Multiples parametros
            for param in params_node.children[0].children:
                param_name = param.children[1].lexeme
                symbol_table[param_name] = param_offset
                param_offset += 4
                emitter.emit_comment(f"Parámetro {param_name} en offset {symbol_table[param_name]}")
        else:
            # Solo un parámetro
            param_name = params_node.children[0].children[1].lexeme
            symbol_table[param_name] = param_offset
            emitter.emit_comment(f"Parámetro {param_name} en offset {symbol_table[param_name]}")
    
    # Genera código para declaraciones locales
    for child in node.children:
        if child.kind == 'compound_stmt':
            generate_code(child, emitter)
    
    # unicamente un epílogo
    emitter.emit(f"{name}_epilogue:")
    emitter.emit_comment("Epilog")
    
    if name == "main":
        # restore stack and exit
        emitter.emit("move $sp, $fp")          # Restore stack pointer
        emitter.emit("lw $fp, 0($sp)")         # Restore frame pointer
        emitter.emit("lw $ra, 4($sp)")         # Restore return address
        emitter.emit("addi $sp, $sp, 8")       # Clean up stack
        emitter.emit("li $v0, 10")             # Exit syscall
        emitter.emit("syscall")
    else:
        # restore everything and return
        emitter.emit("move $sp, $fp")          # Restore stack pointer
        emitter.emit("lw $fp, 0($sp)")         # Restore frame pointer
        emitter.emit("lw $ra, 4($sp)")         # Restore return address
        emitter.emit("addi $sp, $sp, 8")       # Clean up stack
        emitter.emit("jr $ra")                 # Return
    
    emitter.emit("")  # para visualización, dejar una línea en blanco


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
        
        if len(node.children) > 0:  # Array access
            index_reg = gen_expression(node.children[0], emitter)
            
            if offset is not None:
                if offset > 0:  
                    addr_reg = f"$t{register_counter % 10}"
                    register_counter += 1
                    offset_reg = f"$t{register_counter % 10}"
                    register_counter += 1
                    
                    emitter.emit_comment(f"DEBUG: Accessing parameter array {name} at offset {offset}")
                    emitter.emit(f"lw {addr_reg}, {offset}($fp)  # Load array base address")
                    emitter.emit(f"sll {offset_reg}, {index_reg}, 2")
                    emitter.emit(f"# DEBUG: About to access array at calculated address")
                    emitter.emit(f"add {addr_reg}, {addr_reg}, {offset_reg}")
                    emitter.emit(f"lw {reg}, 0({addr_reg})")
                else:  # Local array - use frame pointer directly
                    offset_reg = f"$t{register_counter % 10}"
                    register_counter += 1
                    
                    emitter.emit_comment(f"DEBUG: Accessing local array {name} at offset {offset}")
                    emitter.emit(f"sll {offset_reg}, {index_reg}, 2")
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
        
       
        if len(node.children) > 1:  
            value_reg = gen_expression(node.children[0], emitter)  
            index_reg = gen_expression(node.children[1], emitter)  
            
            if offset is not None:
                offset_reg = f"$t{register_counter % 10}"
                register_counter += 1
                addr_reg = f"$t{register_counter % 10}"
                register_counter += 1
                
                emitter.emit(f"sll {offset_reg}, {index_reg}, 2")
                emitter.emit(f"addi {addr_reg}, $fp, {offset}")
                emitter.emit(f"add {addr_reg}, {addr_reg}, {offset_reg}")
                emitter.emit(f"sw {value_reg}, 0({addr_reg})")
            else:
                emitter.emit_comment(f"[Error] Array no encontrado: {name}")
            return value_reg
        else:  # Simple variable 
            result = gen_expression(node.children[0], emitter)
            if offset is not None:
                emitter.emit(f"sw {result}, {offset}($fp)")
            else:
                emitter.emit_comment(f"[Error] Variable no encontrada para asignación: {name}")
            return result
    
    elif node.kind == 'call':
        func_name = node.lexeme
        # Handle built-in functions
        if func_name == "output":
            if node.children and node.children[0].children:
                arg_reg = gen_expression(node.children[0].children[0].children[0], emitter)
                emitter.emit(f"move $a0, {arg_reg}")
                emitter.emit("li $v0, 1")
                emitter.emit("syscall")
                emitter.emit("la $a0, newline")
                emitter.emit("li $v0, 4")
                emitter.emit("syscall")
            return None
        
        elif func_name in ['findMax', 'calculateSum']:
            emitter.emit_comment(f"DEBUG: Array function call detected")
            if node.children and node.children[0].children:
                args_list = node.children[0].children[0].children
                
                if len(args_list) > 1:
                    second_arg = args_list[1]
                    emitter.emit_comment(f"DEBUG: Pushing second arg (size) first")
                    arg_reg = gen_expression(second_arg, emitter)
                    emitter.emit("addi $sp, $sp, -4")
                    emitter.emit(f"sw {arg_reg}, 0($sp)")
                
                if len(args_list) > 0:
                    first_arg = args_list[0]
                    emitter.emit_comment(f"DEBUG: Pushing first arg (array) second")
                    
                    if first_arg.kind == 'var' and len(first_arg.children) == 0:
                        # This is an array name - pass address
                        var_name = first_arg.lexeme
                        var_offset = symbol_table.get(var_name)
                        emitter.emit_comment(f"DEBUG: Array {var_name} at offset {var_offset}")
                        
                        addr_reg = f"$t{register_counter % 10}"
                        register_counter += 1
                        # Calculate the actual array address
                        emitter.emit(f"addi {addr_reg}, $fp, {var_offset}  # Array address")
                        emitter.emit(f"# DEBUG: Calculated address in {addr_reg}")
                        emitter.emit("addi $sp, $sp, -4")
                        emitter.emit(f"sw {addr_reg}, 0($sp)")
                    else:
                        # Regular expression
                        arg_reg = gen_expression(first_arg, emitter)
                        emitter.emit("addi $sp, $sp, -4")
                        emitter.emit(f"sw {arg_reg}, 0($sp)")
            
            # Call function
            emitter.emit(f"jal {func_name}")
            emitter.emit(f"addi $sp, $sp, 8")  # Clean up 2 args
            
            result_reg = f"$t{register_counter % 10}"
            register_counter += 1
            emitter.emit(f"move {result_reg}, $v0")
            return result_reg
        
        else:
            return gen_call(node, emitter)
    
    else:
        emitter.emit_comment(f"[Warning] Tipo de expresión no manejado: {node.kind}")
        return "$zero"




# === Funciones necesarias para traducir el AST a MIPS ===

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
            # Push arguments onto stack (no need to reverse - they'll be accessed by offset)
            for arg in args_list:
                arg_reg = gen_expression(arg, emitter)
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

