.data
newline: .asciiz "\n"
.text
.globl sumUp
.globl main

sumUp:
# Prolog
sw $ra, 0($sp)
sw $fp, -4($sp)
move $fp, $sp
addi $sp, $sp, -8
# Parámetro n en offset 8
# Inicio de compound_stmt
# Declaración de variable: i (size = 1)
addi $sp, $sp, -4  # Reservar espacio para i
# Declaración de variable: total (size = 1)
addi $sp, $sp, -4  # Reservar espacio para total
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t0, 0
sw $t0, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t1, 0
sw $t1, -8($fp)
# Fin de expression_stmt
# Inicio de while loop
while0:
# Inicio de expression
# Inicio de expression
lw $t2, -4($fp)
# Inicio de expression
lw $t3, 8($fp)
slt $t4, $t2, $t3
beq $t4, $zero, endwhile1
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t5, -8($fp)
# Inicio de expression
lw $t6, -4($fp)
add $t7, $t5, $t6
sw $t7, -8($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t8, -4($fp)
# Inicio de expression
li $t9, 1
add $t0, $t8, $t9
sw $t0, -4($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j while0
endwhile1:
# Fin de while loop
# Return statement
# Inicio de expression
lw $t1, -8($fp)
move $v0, $t1
j epilogue
# Fin de compound_stmt
epilogue:
# Epilog
move $sp, $fp
lw $fp, -4($sp)
lw $ra, 0($sp)
jr $ra

main:
# Prolog
sw $ra, 0($sp)
sw $fp, -4($sp)
move $fp, $sp
addi $sp, $sp, -8
# Inicio de compound_stmt
# Declaración de variable: result (size = 1)
addi $sp, $sp, -4  # Reservar espacio para result
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Llamada a función: sumUp
addi $sp, $sp, -4
sw $ra, 0($sp)
# Inicio de expression
li $t2, 10
move $a0, $t2
jal sumUp
lw $ra, 0($sp)
addi $sp, $sp, 4
move $t3, $v0
sw $t3, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Llamada a función: output
# Inicio de expression
lw $t4, -4($fp)
move $a0, $t4
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Fin de compound_stmt
epilogue:
# Epilog
move $sp, $fp
lw $fp, -4($sp)
lw $ra, 0($sp)
li $v0, 10
syscall

