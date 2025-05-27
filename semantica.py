from globalTypes import *
import parser


# Estado global del semántico

tipoError_ocurrido = False     # ¿Ya detectamos algún error?
depth = []                     # Pila de ámbitos: cada elemento es un dict name→SymbolInfoExtended
current_func_ret = []          # Stack de tipos de retorno de la función activa


# Reportar errores semánticos con contexto y caret

def semanticError(node, message):
    """
    Cuando detectamos un error:
      1) Marcamos el flag
      2) Sacamos línea y texto original
      3) Imprimimos mensaje y '^' debajo del lexema
    """
    global tipoError_ocurrido
    tipoError_ocurrido = True

    ln = getattr(node, 'lineno', None)
    if ln is None:
        print(f"Error semántico: {message}")
        return

    text = parser.lineas[ln-1] if 0 <= ln-1 < len(parser.lineas) else ''
    print(f"Línea {ln}: {message}")
    if text:
        print(text)
        lex = getattr(node, 'lexeme', None)
        if lex is not None:
            idx = text.find(str(lex))
            if idx >= 0:
                print(' ' * idx + '^')


# Estructura de cada símbolo, extendida para registrar usos

class SymbolInfoExtended:
    def __init__(self, name, kind, typ, array_size=None, params=None, declared_at=0):
        self.name        = name          # identificador
        self.kind        = kind          # 'var', 'array' o 'func'
        self.type        = typ           # 'int' o 'void'
        self.array_size  = array_size    # tamaño si es array
        self.params      = params or []  # para funciones: lista de (tipo, is_array)
        self.declared_at = declared_at   # línea de declaración
        self.lines       = [declared_at] # lista de todas las líneas donde aparece


# Manejo de la pila de ámbitos

def push_scope():
    """Abre un nuevo ámbito: apilamos un diccionario vacío."""
    depth.append({})

def pop_scope():
    """Cierra el ámbito actual: desapilamos."""
    if depth:
        depth.pop()

def insert_symbol(name, info):
    """
    Inserta 'info' en el ámbito actual.
    Si ya existe en este mismo nivel, lanza error.
    """
    scope = depth[-1]
    if name in scope:
        semanticError(info, f"Símbolo '{name}' ya declarado en este ámbito")
    else:
        scope[name] = info

def lookup_symbol(name):
    """
    Busca en la pila de ámbitos (de adentro hacia fuera).
    Devuelve SymbolInfoExtended o None.
    """
    for scope in reversed(depth):
        if name in scope:
            return scope[name]
    return None

def record_use(name, lineno):
    """
    Registra un uso de 'name' en la línea 'lineno',
    añadíendola a info.lines (si info existe).
    """
    info = lookup_symbol(name)
    if info:
        info.lines.append(lineno)


# Inicialización del ámbito global con built-ins

def init_symtab():
    """
    1) Limpiamos depth
    2) push_scope() para nivel 0
    3) Insertamos input() y output(int) predefinidas
    """
    global depth
    depth = []
    push_scope()
    insert_symbol('input',  SymbolInfoExtended('input','func','int', None, [], 0))
    insert_symbol('output', SymbolInfoExtended('output','func','void',None, [('int',False)], 0))


# Impresión de la pila de ámbitos completa (debug)

def print_symtab():
    print("Tablas de símbolos por ámbito:")
    for lvl, scope in enumerate(depth):
        print(f" Ámbito nivel {lvl}:")
        for info in scope.values():
            if info.kind == 'var':
                print(f"  var   int    {info.name}  (línea {info.declared_at})")
            elif info.kind == 'array':
                print(f"  array int[{info.array_size}]  {info.name}  (línea {info.declared_at})")
            else:
                sig = ", ".join(f"{t}{'[]' if arr else ''}" for t,arr in info.params)
                print(f"  func  {info.type} {info.name}({sig})  (línea {info.declared_at})")

def print_scope(scope_name, this_scope, param_lines):
    print(f"Scope: {scope_name}\n")
    print(f"{'Variable Name':15s} {'Type':6s} {'Kind':10s} Lines")
    print(f"{'-'*15} {'-'*6} {'-'*10} {'-'*10}")
    for info in this_scope.values():
        # supón que info.lines es la lista de todas las líneas donde aparece
        lines = " ".join(str(l) for l in sorted(set(info.lines)))
        kind  = 'function' if info.kind=='func' else (
                'parameter' if info.declared_at in param_lines else
                'variable')
        print(f"{info.name:15s} {info.type:6s} {kind:10s} {lines}")
    print()


# Impresión final consolidada al estilo de tu profesor

def printSymTabConsolidated():
    """
    Imprime una tabla con columnas:
      Variable Name | Scope | Line Numbers
    mostrando declaración + todos los usos.
    """
    print("\nSymbol table:")
    print(f"{'Variable Name':15s} {'Scope':6s} Line Numbers")
    print(f"{'-'*15} {'-'*6} {'-'*12}")
    for lvl, scope in enumerate(depth):
        for name, info in scope.items():
            unique_lines = sorted(set(info.lines))
            lines_str = " ".join(str(l) for l in unique_lines)
            print(f"{name:15s} {lvl:6d} {lines_str}")


# Recorrido genérico del AST: preorder + postorder

def traverse(node, pre, post):
    if node is None:
        return
    pre(node)
    for c in getattr(node, 'children', []):
        traverse(c, pre, post)
    post(node)


# 1) Construcción de la tabla global

def tabla_global(tree):
    """
    Recorre tree.children (solo var_decl y fun_decl top-level)
    e inserta cada símbolo en el ámbito global (nivel 0).
    """
    init_symtab()
    for decl in tree.children:
        if decl.kind == 'var_decl':
            # variable global
            typ = decl.children[0].lexeme
            nm  = decl.children[1].lexeme
            if len(decl.children) == 3:
                sz = int(decl.children[2].lexeme)
                insert_symbol(nm, SymbolInfoExtended(nm,'array',typ,sz,[],decl.lineno))
            else:
                insert_symbol(nm, SymbolInfoExtended(nm,'var',typ,None,[],decl.lineno))

        elif decl.kind == 'fun_decl':
            # función global
            ret      = decl.children[0].lexeme
            name     = decl.children[1].lexeme
            params_n = decl.children[2]
            params_lst = []
            if params_n.children and params_n.children[0].kind != 'VOID':
                for p in params_n.children[0].children:
                    ptyp   = p.children[0].lexeme
                    is_arr = (len(p.children) == 3)
                    params_lst.append((ptyp, is_arr))
            insert_symbol(name,
                          SymbolInfoExtended(name,'func',ret,None,params_lst,decl.lineno))


# 2) Inserción de vars locales + chequeo de tipos

def type_check_recursive(node):
    """
    - Si es var_decl dentro de función (depth>1), la insertamos local.
    - Recorremos recursivamente hijos.
    - Postorden: chequeamos el nodo actual con checkNode().
    """
    if node.kind == 'var_decl' and len(depth) > 1:
        typ = node.children[0].lexeme
        nm  = node.children[1].lexeme
        if len(node.children) == 3:
            sz = int(node.children[2].lexeme)
            insert_symbol(nm, SymbolInfoExtended(nm,'array',typ,sz,[],node.lineno))
        else:
            insert_symbol(nm, SymbolInfoExtended(nm,'var',typ,None,[],node.lineno))

    for c in node.children:
        type_check_recursive(c)

    checkNode(node)


# Función principal del análisis semántico

def semantica(tree, imprime=True):
    """
    1) Monta tabla global e imprime.
    2) Para cada función:
       a) push_scope()
       b) mete parámetros
       c) recorre cuerpo con type_check_recursive()
       d) si imprime, print_symtab()
       e) pop_scope()
    3) Al final, printSymTabConsolidated().
    """
    global tipoError_ocurrido
    tipoError_ocurrido = False
    current_func_ret.clear()

    # --- Paso 1: globals ---
    tabla_global(tree)
    if imprime:
        print_symtab()

    # --- Paso 2: por cada función top-level ---
    for decl in tree.children:
        if decl.kind == 'fun_decl':
            # 2.a) retorno y nuevo scope
            ret = decl.children[0].lexeme
            current_func_ret.append(ret)
            push_scope()

            # 2.b) parámetros
            params_n = decl.children[2]
            if params_n.children and params_n.children[0].kind != 'VOID':
                for p in params_n.children[0].children:
                    ptyp   = p.children[0].lexeme
                    pname  = p.children[1].lexeme
                    is_arr = (len(p.children) == 3)
                    insert_symbol(pname,
                                  SymbolInfoExtended(pname,
                                                     'array' if is_arr else 'var',
                                                     ptyp, None, [], p.lineno))

            # 2.c) cuerpo
            type_check_recursive(decl)

            # 2.d) debug: imprimir tabla tras entrar
            # … justo en vez de print_symtab() …
            if imprime:
                
                # 1) Imprimir tabla de símbolos global (todos los ámbitos)
                
                print("=== Tabla de símbolos completa ===")
                print_symtab()
                print()  # línea en blanco para separación

                
                # 2) Imprimir sólo el scope de la función actual
                
                # Nombre de la función actual
                func_name = decl.children[1].lexeme

                # Recogemos las líneas donde se declararon sus parámetros
                # (decl.children[2] es el nodo 'params', cuyo primer hijo es 'param_list')
                param_nodes = decl.children[2].children[0].children  # sólo si no es VOID
                param_lines = [p.lineno for p in param_nodes]

                print(f"=== Scope de la función '{func_name}' ===")
                print_scope(func_name, depth[-1], param_lines)



            # 2.e) cerrar scope
            pop_scope()
            current_func_ret.pop()

    # si no hubo errores, confirmamos éxito
    if not tipoError_ocurrido:
        print("\nType Checking Finished")

    # --- Paso 3: tabla consolidada ---
    if imprime:
        printSymTabConsolidated()



# Reglas de inferencia de tipos (postorden)

def nullProc(node):
    pass

def checkNode(node):
    """
    Según node.kind aplica:
      - assign, addop, mulop, relop, var, NUM, call, return_stmt, selection/iteration
      - Reporta errores y asigna node.type para parents.
    """
    k = node.kind

    # assign: izq y der must be int
    if k == 'assign':
        info = lookup_symbol(node.lexeme)
        if info is None:
            semanticError(node, f"Variable '{node.lexeme}' no declarada")
            ltype = 'int'
        else:
            record_use(node.lexeme, node.lineno)
            ltype = info.type
        rtype = getattr(node.children[0], 'type', None)
        if ltype != 'int' or rtype != 'int':
            semanticError(node, "Asignación de tipo no entero")
        node.type = 'int'

    # addop/mulop: ambos operandos int → int
    elif k in ('addop','mulop'):
        l, r = node.children
        if getattr(l,'type',None)!='int' or getattr(r,'type',None)!='int':
            semanticError(node, "Operación aritmética aplicada a operandos no enteros")
        node.type = 'int'

    # relop: ambos operandos int → int
    elif k == 'relop':
        l, r = node.children
        if getattr(l,'type',None)!='int' or getattr(r,'type',None)!='int':
            semanticError(node, "Operación relacional aplicada a operandos no enteros")
        node.type = 'int'

    # var: debe existir
    elif k == 'var':
        info = lookup_symbol(node.lexeme)
        if info is None:
            semanticError(node, f"Variable '{node.lexeme}' no declarada")
            node.type = 'int'
        else:
            record_use(node.lexeme, node.lineno)
            node.type = info.type

    # NUM → int
    elif k == 'NUM':
        node.type = 'int'

    # call: existencia, aridad y tipos
    elif k == 'call':
        fname = node.lexeme
        info  = lookup_symbol(fname)
        if info is None or info.kind != 'func':
            semanticError(node, f"Llamada a función no declarada: {fname}")
            node.type = 'int'
        else:
            record_use(fname, node.lineno)
            # extraemos args reales
            args = []
            if node.children:
                args_node = node.children[0]
                if args_node.children:
                    arg_list_node = args_node.children[0]
                    args = arg_list_node.children
            # comparamos con params
            if len(args) != len(info.params):
                semanticError(node, f"Número de argumentos incorrecto en llamada a {fname}")
            else:
                for arg,(pt,_) in zip(args, info.params):
                    if getattr(arg,'type',None) != pt:
                        semanticError(arg, f"Tipo de argumento inválido en llamada a {fname}")
            node.type = info.type

    # return_stmt: chequeo según current_func_ret
    elif k == 'return_stmt':
        expected = current_func_ret[-1] if current_func_ret else None
        if node.children:
            et = getattr(node.children[0],'type',None)
            if expected != 'int':
                semanticError(node, "Return con valor en función void")
            elif et != 'int':
                semanticError(node, "Return de tipo no entero en función int")
        else:
            if expected == 'int':
                semanticError(node, "Return sin valor en función int")

    # if / while: condición debe ser int
    elif k in ('selection_stmt','iteration_stmt'):
        cond = node.children[0]
        if getattr(cond,'type',None) != 'int':
            semanticError(cond, "Condición de control no entera")
