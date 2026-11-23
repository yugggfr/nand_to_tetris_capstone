# Nand to Tetris Capstone: Drawing a Box on the Hack Computer

**Course:** Nand to Tetris – I (ETCCNT301), K.R. Mangalam University  
**Student:** Yug Verma  
**Roll no.:** 2501350004  
**K value:** 04  

## Parameters derived from K
- The box begins at row 4, spans 20 rows (rows 4 to 23), and is 16 pixels wide (1 word per row).
- Its first screen address is 16384 + 32 × 4 = 16512.
- Since K mod 3 = 4 mod 3 = 1, my assembler's bonus feature is a clear error message that reports the line number of any invalid line.

## Project contents
| File | Description |
|---|---|
| `CPU.hdl` | Hack CPU implementation (Part A) |
| `Memory.hdl` | Memory map combining RAM, Screen and Keyboard (Part A) |
| `Computer.hdl` | Top-level chip wiring ROM, CPU and Memory (Part A) |
| `assembler.py` | Hack assembler written in Python with error reporting (Part B) |
| `Box.asm` | Assembly program that draws a black box while a key is held (Part C) |
| `Box.hack` | Machine code produced by assembling `Box.asm` with my own assembler |

## Running the project
- **Assembler:** run `python assembler.py Box.asm` to generate `Box.hack`.
- **Chips:** place the three `.hdl` files in `projects/5` of the Nand to Tetris software suite, then run the official `.tst` scripts in the Hardware Simulator.
- **Box program:** open `Box.hack` in the CPU Emulator, turn on the keyboard, start the program, and hold down any key to see the box appear.
