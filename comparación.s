# This is a mockup of the MIPS code that would be generated from your AST
# for the 'bigTest' and 'main' functions, assuming all variables are local
# and stored on the stack using the frame pointer ($fp).

.data
newline: .asciiz "\n"

.text
.globl main

# === Function: bigTest ===
bigTest:
    # Prolog
    sw $ra, 0($sp)
    sw $fp, -4($sp)
    move $fp, $sp
    addi $sp, $sp, -60  # reserve space for locals: total, data[5], i, val, t, j, X, Y, Z, P, Q

    # total = 0
    li $t0, 0
    sw $t0, -4($fp)      # total at -4

    # data[0] = N (arg0)
    sw $a0, -8($fp)      # data[0] at -8
    sw $a1, -4($fp)      # M might be used too

    # data[1] = M
    sw $a1, -12($fp)

    # data[2] = N + M
    add $t0, $a0, $a1
    sw $t0, -16($fp)

    # data[3] = N * M
    mul $t0, $a0, $a1
    sw $t0, -20($fp)

    # data[4] = N - M
    sub $t0, $a0, $a1
    sw $t0, -24($fp)

    # i = 0
    li $t0, 0
    sw $t0, -28($fp)     # i at -28

WHILE1:
    lw $t0, -28($fp)
    lw $t1, $a0
    bge $t0, $t1, ENDWHILE1

    # if i < 5
    lw $t0, -28($fp)
    li $t1, 5
    bge $t0, $t1, ELSE1

    # val = data[i]
    sll $t2, $t0, 2
    addi $t3, $fp, -8
    sub $t3, $t3, $t2
    lw $t4, 0($t3)
    sw $t4, -32($fp)     # val at -32
    j ENDIF1

ELSE1:
    # t = i - 5
    lw $t0, -28($fp)
    li $t1, 5
    sub $t2, $t0, $t1
    sw $t2, -36($fp)     # t at -36

    # val = data[t]
    sll $t2, $t2, 2
    addi $t3, $fp, -8
    sub $t3, $t3, $t2
    lw $t4, 0($t3)
    sw $t4, -32($fp)

ENDIF1:
    # total = total + val
    lw $t0, -4($fp)
    lw $t1, -32($fp)
    add $t2, $t0, $t1
    sw $t2, -4($fp)

    # i = i + 1
    lw $t0, -28($fp)
    li $t1, 1
    add $t0, $t0, $t1
    sw $t0, -28($fp)

    j WHILE1
ENDWHILE1:

# second while: j < M
    li $t0, 0
    sw $t0, -40($fp)     # j at -40
WHILE2:
    lw $t0, -40($fp)
    lw $t1, $a1
    bge $t0, $t1, ENDWHILE2

    # total = total + j
    lw $t2, -4($fp)
    add $t2, $t2, $t0
    sw $t2, -4($fp)

    # j = j + 1
    li $t3, 1
    add $t0, $t0, $t3
    sw $t0, -40($fp)
    j WHILE2
ENDWHILE2:

    # X = total
    lw $t0, -4($fp)
    sw $t0, -44($fp)     # X at -44
    # Y = data[3]
    lw $t1, -20($fp)
    sw $t1, -48($fp)     # Y at -48

    # if (X >= Y)
    bge $t0, $t1, IF2
    # else
    lw $t2, -48($fp)     # Y
    lw $t3, -44($fp)     # X
    sub $t4, $t2, $t3
    sw $t4, -52($fp)     # Z at -52
    sw $t4, -4($fp)
    j ENDIF2
IF2:
    sw $t0, -4($fp)
ENDIF2:

    # P = total
    lw $t0, -4($fp)
    sw $t0, -56($fp)     # P at -56
    # Q = P * 2
    li $t1, 2
    mul $t2, $t0, $t1
    sw $t2, -60($fp)     # Q at -60

    # if Q > 100
    li $t3, 100
    ble $t2, $t3, ELSE3
    sw $t2, -4($fp)
    j ENDIF3
ELSE3:
    lw $t4, -4($fp)
    add $t5, $t4, $t2
    sw $t5, -4($fp)
ENDIF3:

    # output(total)
    lw $a0, -4($fp)
    li $v0, 1
    syscall
    li $v0, 4
    la $a0, newline
    syscall

    jr $ra


# === Function: main ===
main:
    sw $ra, 0($sp)
    sw $fp, -4($sp)
    move $fp, $sp
    addi $sp, $sp, -20  # a, b, temp, inner

    li $v0, 5
    syscall
    move $t0, $v0
    sw $t0, -4($fp)     # a at -4

    li $v0, 5
    syscall
    move $t1, $v0
    sw $t1, -8($fp)     # b at -8

    move $a0, $t0
    move $a1, $t1
    jal bigTest

    # temp = a + b
    add $t2, $t0, $t1
    sw $t2, -12($fp)

    # if temp != 0
    beq $t2, $zero, ELSE4
    # inner = temp * 2
    li $t3, 2
    mul $t4, $t2, $t3
    sw $t4, -16($fp)
    move $a0, $t4
    li $v0, 1
    syscall
    li $v0, 4
    la $a0, newline
    syscall
    j ENDIF4
ELSE4:
    li $a0, 0
    li $v0, 1
    syscall
    li $v0, 4
    la $a0, newline
    syscall
ENDIF4:

    jr $ra
