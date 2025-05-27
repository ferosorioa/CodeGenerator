from enum import Enum

class TokenType(Enum):

    ENDFILE = '$'
    ERROR   = 301
 
    IF      = 'if'
    ELSE    = 'else'
    WHILE   = 'while'
    INT     = 'int'
    VOID    = 'void'
    RETURN  = 'return'

    ID      = 310
    NUM     = 311


    EQ      = '='      
    EQEQ    = '=='     
    LT      = '<'
    LE      = '<='    
    GT      = '>'
    GE      = '>='     
    NE      = '!='   
    PLUS    = '+'
    MINUS   = '-'
    TIMES   = '*'
    OVER    = '/'
    LPAREN  = '('
    RPAREN  = ')'
    LBRACE  = '{'
    RBRACE  = '}'
    LBRACKET= '['
    RBRACKET= ']'
    SEMI    = ';'
    COMMA   = ','

    COMMENT = 'comment'
    

class StateType(Enum):
    START     = 0
    INCOMMENT = 2
    INNUM     = 3
    INID      = 4
    DONE      = 5

class ReservedWords(Enum):
    IF     = 'if'
    ELSE   = 'else'
    WHILE  = 'while'
    INT    = 'int'
    VOID   = 'void'
    RETURN = 'return'
