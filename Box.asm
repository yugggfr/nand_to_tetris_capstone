// Box.asm  --  Capstone, K = 82
//
// While any key is pressed, a black box is drawn. When the key is released,
// the box is erased.
//
// Box size, worked out from K = 82:
//   start row = K            = 82
//   height                   = 20 rows   (rows 82 .. 101)
//   width = 16*((K mod 4)+1) = 16*3 = 48 pixels = 3 words, from the left edge
//
// Row r starts at SCREEN + 32*r, so the first word of the box is at
//   16384 + 32*82 = 19008

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
    @19008          // address of the first word of row 82
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
    A=A+1
    M=D             // word 2 of this row  (pixels 16..31)
    A=A+1
    M=D             // word 3 of this row  (pixels 32..47)

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
