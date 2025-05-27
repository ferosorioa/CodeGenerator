# mainParser.py

from globalTypes import *
from parser import parser, globales as parser_globales
from semantica import semantica

if __name__ == "__main__":
    fileName = "sample"
    with open(fileName + '.c-', 'r') as f:
        prog = f.read()
    prog += '$'
    progLong = len(prog)
    posicion = 0

    parser_globales(prog, posicion, progLong)
    ast = parser(imprime=True)
    semantica(ast, imprime=True)
