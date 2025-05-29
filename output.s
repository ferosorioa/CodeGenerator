.data
newline: .asciiz "\n"

.text
.globl sumUp
.globl main

main:
# Prolog
move $fp, $sp
addi $sp, $sp, -4
# Inicio de compound_stmt
# Declaración de variable: result (size = 1)
addi $sp, $sp, -4  # Reservar espacio para result
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Llamada a función: sumUp
# Inicio de expression
li $t0, 10
addi $sp, $sp, -4
sw $t0, 0($sp)
jal sumUp
addi $sp, $sp, 4
move $t1, $v0
sw $t1, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Llamada a función: output
# Inicio de expression
lw $t2, -4($fp)
move $a0, $t2
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Fin de compound_stmt
main_epilogue:
# Epilog
li $v0, 10
syscall

sumUp:
# Prolog
addi $sp, $sp, -8
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
addi $fp, $fp, 8
# Parámetro n en offset 0
# Inicio de compound_stmt
# Declaración de variable: i (size = 1)
addi $sp, $sp, -4  # Reservar espacio para i
# Declaración de variable: total (size = 1)
addi $sp, $sp, -4  # Reservar espacio para total
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t3, 0
sw $t3, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t4, 0
sw $t4, -8($fp)
# Fin de expression_stmt
# Inicio de while loop
while0:
# Inicio de expression
# Inicio de expression
lw $t5, -4($fp)
# Inicio de expression
lw $t6, 0($fp)
slt $t7, $t5, $t6
beq $t7, $zero, endwhile1
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t8, -8($fp)
# Inicio de expression
lw $t9, -4($fp)
add $t0, $t8, $t9
sw $t0, -8($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t1, -4($fp)
# Inicio de expression
li $t2, 1
add $t3, $t1, $t2
sw $t3, -4($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j while0
endwhile1:
# Fin de while loop
# Return statement
# Inicio de expression
lw $t4, -8($fp)
move $v0, $t4
j sumUp_epilogue
# Fin de compound_stmt
sumUp_epilogue:
# Epilog
addi $sp, $fp, -8
lw $fp, 0($sp)
lw $ra, 4($sp)
addi $sp, $sp, 8
jr $ra

