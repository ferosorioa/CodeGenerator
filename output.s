.data
newline: .asciiz "\n"

.text
.globl findMax
.globl calculateSum
.globl factorial
.globl main

main:
# Prolog
addi $sp, $sp, -8
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# Inicio de compound_stmt
# Declaración de variable: numbers (size = 5)
addi $sp, $sp, -20  # Reservar espacio para numbers
# Declaración de variable: i (size = 1)
addi $sp, $sp, -4  # Reservar espacio para i
# Declaración de variable: size (size = 1)
addi $sp, $sp, -4  # Reservar espacio para size
# Declaración de variable: maximum (size = 1)
addi $sp, $sp, -4  # Reservar espacio para maximum
# Declaración de variable: total (size = 1)
addi $sp, $sp, -4  # Reservar espacio para total
# Declaración de variable: fact (size = 1)
addi $sp, $sp, -4  # Reservar espacio para fact
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t0, 5
sw $t0, -28($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t1, 15
# Inicio de expression
li $t2, 0
sll $t3, $t2, 2
addi $t4, $fp, -20
add $t4, $t4, $t3
sw $t1, 0($t4)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t5, 3
# Inicio de expression
li $t6, 1
sll $t7, $t6, 2
addi $t8, $fp, -20
add $t8, $t8, $t7
sw $t5, 0($t8)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t9, 27
# Inicio de expression
li $t0, 2
sll $t1, $t0, 2
addi $t2, $fp, -20
add $t2, $t2, $t1
sw $t9, 0($t2)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t3, 8
# Inicio de expression
li $t4, 3
sll $t5, $t4, 2
addi $t6, $fp, -20
add $t6, $t6, $t5
sw $t3, 0($t6)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t7, 19
# Inicio de expression
li $t8, 4
sll $t9, $t8, 2
addi $t0, $fp, -20
add $t0, $t0, $t9
sw $t7, 0($t0)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
li $t1, 999
move $a0, $t1
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t2, 0
sw $t2, -24($fp)
# Fin de expression_stmt
# Inicio de while loop
while0:
# Inicio de expression
# Inicio de expression
lw $t3, -24($fp)
# Inicio de expression
lw $t4, -28($fp)
slt $t5, $t3, $t4
beq $t5, $zero, endwhile1
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
# Inicio de expression
lw $t7, -24($fp)
# DEBUG: Accessing local array numbers at offset -20
sll $t8, $t7, 2
addi $t8, $t8, -20
add $t8, $t8, $fp
lw $t6, 0($t8)
move $a0, $t6
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t9, -24($fp)
# Inicio de expression
li $t0, 1
add $t1, $t9, $t0
sw $t1, -24($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j while0
endwhile1:
# Fin de while loop
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# DEBUG: Processing call to findMax
# DEBUG: Array function call detected
# DEBUG: Pushing second arg (size) first
# Inicio de expression
lw $t2, -28($fp)
addi $sp, $sp, -4
sw $t2, 0($sp)
# DEBUG: Pushing first arg (array) second
# DEBUG: Array numbers at offset -20
addi $t3, $fp, -20  # Array address
# DEBUG: Calculated address in $t3
addi $sp, $sp, -4
sw $t3, 0($sp)
jal findMax
addi $sp, $sp, 8
move $t4, $v0
sw $t4, -32($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
li $t5, 888
move $a0, $t5
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
lw $t6, -32($fp)
move $a0, $t6
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# DEBUG: Processing call to calculateSum
# DEBUG: Array function call detected
# DEBUG: Pushing second arg (size) first
# Inicio de expression
lw $t7, -28($fp)
addi $sp, $sp, -4
sw $t7, 0($sp)
# DEBUG: Pushing first arg (array) second
# DEBUG: Array numbers at offset -20
addi $t8, $fp, -20  # Array address
# DEBUG: Calculated address in $t8
addi $sp, $sp, -4
sw $t8, 0($sp)
jal calculateSum
addi $sp, $sp, 8
move $t9, $v0
sw $t9, -36($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
li $t0, 777
move $a0, $t0
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
lw $t1, -36($fp)
move $a0, $t1
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de if statement
# Inicio de expression
# Inicio de expression
lw $t2, -32($fp)
# Inicio de expression
li $t3, 10
slt $t4, $t3, $t2
xori $t4, $t4, 1
beq $t4, $zero, else2
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# DEBUG: Processing call to factorial
# Llamada a función: factorial
# Inicio de expression
lw $t5, -32($fp)
addi $sp, $sp, -4
sw $t5, 0($sp)
jal factorial
addi $sp, $sp, 4
move $t6, $v0
sw $t6, -40($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
li $t7, 666
move $a0, $t7
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
lw $t8, -40($fp)
move $a0, $t8
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Fin de compound_stmt
j endif3
else2:
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
li $t9, 555
move $a0, $t9
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Fin de compound_stmt
endif3:
# Fin de if statement
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
li $t0, 444
move $a0, $t0
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t1, 0
sw $t1, -24($fp)
# Fin de expression_stmt
# Inicio de while loop
while4:
# Inicio de expression
# Inicio de expression
lw $t2, -24($fp)
# Inicio de expression
lw $t3, -28($fp)
slt $t4, $t2, $t3
beq $t4, $zero, endwhile5
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t6, -24($fp)
# DEBUG: Accessing local array numbers at offset -20
sll $t7, $t6, 2
addi $t7, $t7, -20
add $t7, $t7, $fp
lw $t5, 0($t7)
# Inicio de expression
li $t8, 2
mul $t9, $t5, $t8
# Inicio de expression
lw $t0, -24($fp)
sll $t1, $t0, 2
addi $t2, $fp, -20
add $t2, $t2, $t1
sw $t9, 0($t2)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# DEBUG: Processing call to output
# Inicio de expression
# Inicio de expression
lw $t4, -24($fp)
# DEBUG: Accessing local array numbers at offset -20
sll $t5, $t4, 2
addi $t5, $t5, -20
add $t5, $t5, $fp
lw $t3, 0($t5)
move $a0, $t3
li $v0, 1
syscall
la $a0, newline
li $v0, 4
syscall
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t6, -24($fp)
# Inicio de expression
li $t7, 1
add $t8, $t6, $t7
sw $t8, -24($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j while4
endwhile5:
# Fin de while loop
# Fin de compound_stmt
main_epilogue:
# Epilog
move $sp, $fp
lw $fp, 0($sp)
lw $ra, 4($sp)
addi $sp, $sp, 8
li $v0, 10
syscall

findMax:
# Prolog
addi $sp, $sp, -8
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# Parámetro arr en offset 8
# Parámetro size en offset 12
# Inicio de compound_stmt
# Declaración de variable: max (size = 1)
addi $sp, $sp, -4  # Reservar espacio para max
# Declaración de variable: i (size = 1)
addi $sp, $sp, -4  # Reservar espacio para i
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
li $t0, 0
# DEBUG: Accessing parameter array arr at offset 8
lw $t1, 8($fp)  # Load array base address
sll $t2, $t0, 2
# DEBUG: About to access array at calculated address
add $t1, $t1, $t2
lw $t9, 0($t1)
sw $t9, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t3, 1
sw $t3, -8($fp)
# Fin de expression_stmt
# Inicio de while loop
while6:
# Inicio de expression
# Inicio de expression
lw $t4, -8($fp)
# Inicio de expression
lw $t5, 12($fp)
slt $t6, $t4, $t5
beq $t6, $zero, endwhile7
# Inicio de compound_stmt
# Inicio de if statement
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t8, -8($fp)
# DEBUG: Accessing parameter array arr at offset 8
lw $t9, 8($fp)  # Load array base address
sll $t0, $t8, 2
# DEBUG: About to access array at calculated address
add $t9, $t9, $t0
lw $t7, 0($t9)
# Inicio de expression
lw $t1, -4($fp)
slt $t2, $t1, $t7
beq $t2, $zero, else8
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t4, -8($fp)
# DEBUG: Accessing parameter array arr at offset 8
lw $t5, 8($fp)  # Load array base address
sll $t6, $t4, 2
# DEBUG: About to access array at calculated address
add $t5, $t5, $t6
lw $t3, 0($t5)
sw $t3, -4($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j endif9
else8:
endif9:
# Fin de if statement
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t7, -8($fp)
# Inicio de expression
li $t8, 1
add $t9, $t7, $t8
sw $t9, -8($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j while6
endwhile7:
# Fin de while loop
# Return statement
# Inicio de expression
lw $t0, -4($fp)
move $v0, $t0
j findMax_epilogue
# Fin de compound_stmt
findMax_epilogue:
# Epilog
move $sp, $fp
lw $fp, 0($sp)
lw $ra, 4($sp)
addi $sp, $sp, 8
jr $ra

calculateSum:
# Prolog
addi $sp, $sp, -8
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# Parámetro arr en offset 8
# Parámetro size en offset 12
# Inicio de compound_stmt
# Declaración de variable: sum (size = 1)
addi $sp, $sp, -4  # Reservar espacio para sum
# Declaración de variable: i (size = 1)
addi $sp, $sp, -4  # Reservar espacio para i
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t1, 0
sw $t1, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t2, 0
sw $t2, -8($fp)
# Fin de expression_stmt
# Inicio de while loop
while10:
# Inicio de expression
# Inicio de expression
lw $t3, -8($fp)
# Inicio de expression
lw $t4, 12($fp)
slt $t5, $t3, $t4
beq $t5, $zero, endwhile11
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t6, -4($fp)
# Inicio de expression
# Inicio de expression
lw $t8, -8($fp)
# DEBUG: Accessing parameter array arr at offset 8
lw $t9, 8($fp)  # Load array base address
sll $t0, $t8, 2
# DEBUG: About to access array at calculated address
add $t9, $t9, $t0
lw $t7, 0($t9)
add $t1, $t6, $t7
sw $t1, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t2, -8($fp)
# Inicio de expression
li $t3, 1
add $t4, $t2, $t3
sw $t4, -8($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j while10
endwhile11:
# Fin de while loop
# Return statement
# Inicio de expression
lw $t5, -4($fp)
move $v0, $t5
j calculateSum_epilogue
# Fin de compound_stmt
calculateSum_epilogue:
# Epilog
move $sp, $fp
lw $fp, 0($sp)
lw $ra, 4($sp)
addi $sp, $sp, 8
jr $ra

factorial:
# Prolog
addi $sp, $sp, -8
sw $ra, 4($sp)
sw $fp, 0($sp)
move $fp, $sp
# Parámetro n en offset 8
# Inicio de compound_stmt
# Declaración de variable: result (size = 1)
addi $sp, $sp, -4  # Reservar espacio para result
# Declaración de variable: i (size = 1)
addi $sp, $sp, -4  # Reservar espacio para i
# Inicio de if statement
# Inicio de expression
# Inicio de expression
lw $t6, 8($fp)
# Inicio de expression
li $t7, 1
slt $t8, $t7, $t6
xori $t8, $t8, 1
beq $t8, $zero, else12
# Inicio de compound_stmt
# Return statement
# Inicio de expression
li $t9, 1
move $v0, $t9
j factorial_epilogue
# Fin de compound_stmt
j endif13
else12:
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t0, 1
sw $t0, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
li $t1, 2
sw $t1, -8($fp)
# Fin de expression_stmt
# Inicio de while loop
while14:
# Inicio de expression
# Inicio de expression
lw $t2, -8($fp)
# Inicio de expression
lw $t3, 8($fp)
slt $t4, $t3, $t2
xori $t4, $t4, 1
beq $t4, $zero, endwhile15
# Inicio de compound_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t5, -4($fp)
# Inicio de expression
lw $t6, -8($fp)
mul $t7, $t5, $t6
sw $t7, -4($fp)
# Fin de expression_stmt
# Inicio de expression_stmt
# Inicio de expression
# Inicio de expression
# Inicio de expression
lw $t8, -8($fp)
# Inicio de expression
li $t9, 1
add $t0, $t8, $t9
sw $t0, -8($fp)
# Fin de expression_stmt
# Fin de compound_stmt
j while14
endwhile15:
# Fin de while loop
# Return statement
# Inicio de expression
lw $t1, -4($fp)
move $v0, $t1
j factorial_epilogue
# Fin de compound_stmt
endif13:
# Fin de if statement
# Fin de compound_stmt
factorial_epilogue:
# Epilog
move $sp, $fp
lw $fp, 0($sp)
lw $ra, 4($sp)
addi $sp, $sp, 8
jr $ra

