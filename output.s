.data
newline: .asciiz "\n"
.text
.globl main
main:
# Prolog
sw $ra, 0($sp)
sw $fp, -4($sp)
move $fp, $sp
addi $sp, $sp, -8
# Inicio de compound_stmt
# Declaración de variable: x (size = 1)
addi $sp, $sp, -4  # Reservar espacio para x
# Declaración de variable: y (size = 1)
addi $sp, $sp, -4  # Reservar espacio para y
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t0, 5
sw $t0, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t1, -4($fp)
# Inicio de expression
li $t2, 1
add $t3, $t1, $t2
sw $t3, -8($fp)
# Fin de expression_stmt
# Fin de compound_stmt
# Epilog
move $sp, $fp
lw $fp, -4($sp)
lw $ra, 0($sp)
jr $ra
