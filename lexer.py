from globalTypes import *

def globales(prog, pos, long):
    global programa, posicion, progLong
    programa = prog
    posicion = pos
    progLong = long

lineno = 1 

'''
Comenzamos usando la aplicación de reserved lookup, es una función que nos ayuda a encontrar las palabras reservadas del lenguaje C-
'''
def reservedLookup(tokenString):

    for w in ReservedWords:
        if tokenString == w.value:
            return TokenType(tokenString)
    return TokenType.ID


""" La función getToken se encarga de leer el siguiente token del programa fuente utilizando un autómata finito. Este autómata comienza en un estado inicial y, según el primer carácter que encuentra, transita a diferentes estados (por ejemplo, para números, identificadores, comentarios, operadores, etc.). Durante la transición, va acumulando en una cadena el lexema correspondiente hasta que determina que el token está completo.

Una vez que se ha reconocido completamente el token, la función retorna un par formado por el tipo de token y su lexema. En otras palabras, getToken analiza el programa carácter por carácter, siguiendo un conjunto de reglas predefinidas mediante estados, para extraer y clasificar las unidades léxicas, permitiendo luego que el compilador o analizador sintáctico procese la estructura del programa. """
def getToken(imprime=True):
    global posicion, programa, progLong, lineno

    tokenString = ""
    currentToken = None
    state = StateType.START
    # Inicializa el estado como START y comienza un loop mientras que no se haya llegado al final del programa
    while state != StateType.DONE:
        if posicion >= progLong:
            if state == StateType.INCOMMENT:
                currentToken = TokenType.COMMENT
            else:
                currentToken = TokenType.ENDFILE
            state = StateType.DONE
            break
        # Obtenemos el caracter actual del programa
        c = programa[posicion]

        # Dependiendo el estado en el que se encuentre, se ejecutará una acción diferente
        if state == StateType.START:
            if c == '$':
                # end-of-file sentinel
                state = StateType.DONE
                currentToken = TokenType.ENDFILE
                tokenString = '$'
                posicion += 1
                break

            elif c in [' ', '\t', '\n']:
                posicion += 1
                if c == '\n':
                    lineno += 1
                continue
            elif c == '/':
                # Si el caracter es un '/', se verifica si el siguiente caracter es un '*', si lo es, se cambia al estado de INCOMMENT
                if (posicion + 1 < progLong) and (programa[posicion + 1] == '*'):
                    state = StateType.INCOMMENT
                    tokenString += c
                    posicion += 1
                    c = programa[posicion]
                    tokenString += c
                    posicion += 1
                    continue
                else:
                    # Si no es un '/', se verifica si el siguiente caracter es un '=', si lo es, se cambia al estado de DONE
                    state = StateType.DONE
                    currentToken = TokenType.OVER
                    tokenString += c
                    posicion += 1
            #Si el caracter es un '=', se verifica si el siguiente caracter es un '=', si lo es, se cambia al estado de DONE. Esto es para ver si es un igual o un igual igual ya que son tokens diferentes.
            elif c == '=':
                if (posicion + 1 < progLong) and (programa[posicion + 1] == '='):
                    tokenString += c  
                    posicion += 1
                    tokenString += programa[posicion] 
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.EQEQ
                else:
                    tokenString += c
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.EQ
            # Si el caracter es un '<', se verifica si el siguiente caracter es un '=', si lo es, se cambia al estado de DONE. Esto es para observar si es un menor a sólo o un menor o igual a, ya que se manejan como tokens diferentes. 
            elif c == '<':
                if (posicion + 1 < progLong) and (programa[posicion + 1] == '='):
                    tokenString += c
                    posicion += 1
                    tokenString += programa[posicion]
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.LE
                
                else:
                    tokenString += c
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.LT
            # Si el caracter es un '>', se verifica si el siguiente caracter es un '=', si lo es, se cambia al estado de DONE. Esto es para observar si es un mayor a sólo o un mayor o igual a, ya que se manejan como tokens diferentes.
            elif c == '>':
                if (posicion + 1 < progLong) and (programa[posicion + 1] == '='):
                    tokenString += c
                    posicion += 1
                    tokenString += programa[posicion]
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.GE
                else:
                    tokenString += c
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.GT
            # Si el caracter es un '!', se verifica si el siguiente caracter es un '=', si lo es, se cambia al estado de DONE. Si no es un diferente a, entonces se maneja como un error.
            elif c == '!':
                if (posicion + 1 < progLong) and (programa[posicion + 1] == '='):
                    tokenString += c
                    posicion += 1
                    tokenString += programa[posicion]
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.NE
                else:
                    tokenString += c
                    posicion += 1
                    state = StateType.DONE
                    currentToken = TokenType.ERROR
            #Si c isdigit, se cambia al estado de INNUM y se agrega el caracter a la cadena de tokenString. Esto es para observar si es un número o un identificador, ya que se manejan como tokens diferentes. El estado INNUM es para ver que todo el tokens sea un INT.
            elif c.isdigit():
                state = StateType.INNUM
                tokenString += c
                posicion += 1
            # Si c es alfabético, se cambia al estado de INID y se agrega el caracter a la cadena de tokenString. Esto es para observar si es un número o un identificador, ya que se manejan como tokens diferentes. El estado INID es para ver que todo el tokens sea un ID.
            elif c.isalpha():
                state = StateType.INID
                tokenString += c
                posicion += 1
            #Los siguientes son tokens normales que no requieren de más verificación. Se cambian al estado de DONE y se agrega el caracter a la cadena de tokenString.
            elif c == '(':
                state = StateType.DONE
                currentToken = TokenType.LPAREN
                tokenString += c
                posicion += 1
            elif c == ')':
                state = StateType.DONE
                currentToken = TokenType.RPAREN
                tokenString += c
                posicion += 1
            elif c == '[':
                state = StateType.DONE
                currentToken = TokenType.LBRACKET
                tokenString += c
                posicion += 1
            elif c == ']':
                state = StateType.DONE
                currentToken = TokenType.RBRACKET
                tokenString += c
                posicion += 1

            elif c == ';':
                state = StateType.DONE
                currentToken = TokenType.SEMI
                tokenString += c
                posicion += 1
            elif c == ',':
                state = StateType.DONE
                currentToken = TokenType.COMMA
                tokenString += c
                posicion += 1
            elif c == '{':
                state = StateType.DONE
                currentToken = TokenType.LBRACE
                tokenString += c
                posicion += 1
            elif c == '}':
                state = StateType.DONE
                currentToken = TokenType.RBRACE
                tokenString += c
                posicion += 1
            elif c == '[':
                state = StateType.DONE
                currentToken = TokenType.LBRACKET
                tokenString += c
                posicion += 1
            elif c == ']':
                state = StateType.DONE
                currentToken = TokenType.RBRACKET
                tokenString += c
                posicion += 1
            elif c == '+':
                state = StateType.DONE
                currentToken = TokenType.PLUS
                tokenString += c
                posicion += 1
            elif c == '-':
                state = StateType.DONE
                currentToken = TokenType.MINUS
                tokenString += c
                posicion += 1
            elif c == '*':
                state = StateType.DONE
                currentToken = TokenType.TIMES
                tokenString += c
                posicion += 1

            else:
                state = StateType.DONE
                currentToken = TokenType.ERROR
                tokenString += c
                posicion += 1
        # Si el estado es INCOMMENT, se verifica si el siguiente caracter es un '/', si lo es, se cambia al estado de DONE. Esto es para observar si es un comentario o no.
        elif state == StateType.INCOMMENT:
            if c == '*' and (posicion + 1 < progLong) and (programa[posicion + 1] == '/'):
                tokenString += c
                posicion += 1
                c = programa[posicion]
                tokenString += c
                posicion += 1
                state = StateType.DONE
                currentToken = TokenType.COMMENT
            else:
                tokenString += c
                if c == '\n':
                    lineno += 1
                posicion += 1

    
        # Si el estado es INNUM, se verifica si el siguiente caracter es un dígito, si lo es, se agrega a la cadena de tokenString. Si no es un dígito, se verifica si es alfabético, si lo es, se cambia al estado de ERROR y se cambia al estado de DONE. Si no es ninguno de los dos, se cambia al estado de DONE.
        elif state == StateType.INNUM:
            if c.isdigit():
                tokenString += c
                posicion += 1
            elif c.isalpha():
                tokenString += c
                currentToken = TokenType.ERROR
                state = StateType.DONE
                posicion += 1
            else:
                currentToken = TokenType.NUM
                state = StateType.DONE

        # Si el estado es INID, se verifica si el siguiente caracter es alfabético, si lo es, se agrega a la cadena de tokenString. Si no es alfabético, se verifica si es un dígito, si lo es, se cambia al estado de ERROR y se cambia al estado de DONE. Si no es ninguno de los dos, se cambia al estado de DONE.
        elif state == StateType.INID:
            if c.isalpha():
                tokenString += c
                posicion += 1
            elif c.isdigit():
                tokenString += c
                currentToken = TokenType.ERROR
                state = StateType.DONE
                posicion += 1
            else:
                currentToken = TokenType.ID
                state = StateType.DONE

    # Si el token es un identificador, se verifica si es una palabra reservada, si lo es, se cambia al token correspondiente. Si no es una palabra reservada, se deja como un identificador. Esto es una vez que tengas un token marcado cómo ID, se debe verificar que en realidad sea un ID y no una palabra reservada
    if currentToken == TokenType.ID:
        currentToken = reservedLookup(tokenString)

    #Si el token es un error se maneja de manera diferente, sino se imprime el token con el valor.
    if imprime:
        if currentToken == TokenType.ERROR:
            print(f"ERROR EN LÍNEA {lineno}: {currentToken} = {tokenString}")
        else:
            print(f"Línea {lineno}: {currentToken} = {tokenString}")

    return currentToken, tokenString
