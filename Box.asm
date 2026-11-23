// Box.asm  --  Capstone, K = 04
// Author: Yug Verma (Roll No.: 2501350004)
//
// While any key is pressed, a black box is drawn. When the key is released,
// the box is erased.
//
// Box size, worked out from K = 04:
//   start row = K            = 4
//   height                   = 20 rows   (rows 4 .. 23)
//   width = 16*((K mod 4)+1) = 16*(0+1) = 16 pixels = 1 word, from the left edge
//
// Row r starts at SCREEN + 32*r, so the first word of the box is at
//   16384 + 32*4 = 16512

(MAIN)
    @KBD
    D=M
    @PRESSED
    D;JNE           // a key is down  -> go and paint black

    @color
    M=0             // no key         -> paint white (erase)
    @DRAW
    0;JMP

(PRESSED)
    @color
    M=-1            // -1 = 1111111111111111 = 16 black pixels

(DRAW)
    @16512          // address of the first word of row 4 (16384 + 32*4)
    D=A
    @addr
    M=D
    @20
    D=A
    @rows
    M=D             // rows = 20 rows still to draw

(ROW)
    @color
    D=M             // D = colour to write
    @addr
    A=M
    M=D             // word 1 of this row  (pixels 0..15)

    @32
    D=A
    @addr
    M=D+M           // addr = addr + 32   (start of next row)

    @rows
    M=M-1
    D=M
    @ROW
    D;JGT           // more rows left? repeat

    @MAIN
    0;JMP           // check the keyboard again
