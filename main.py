# mainParser.py
# For this code generator implementation we used the:
# - Parser, Semantic Analyzer, and Code Generator from Emilia Salazar Leipen

from globalTypes import *
from parser import parser, globales as parser_globales
from semantica import semantica
from cgen import *

if __name__ == "__main__":
    path = 'pruebas.c-' #sample.c-
    with open(path, 'r') as f:
        prog = f.read()
    prog += '$'
    progLong = len(prog)
    posicion = 0

    parser_globales(prog, posicion, progLong)
    ast = parser(imprime=True)
    semantica(ast, imprime=True)
    codeGen(ast,"output.s")

