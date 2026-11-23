#!/usr/bin/env python3
"""
Hack assembler  --  Nand to Tetris capstone (K = 82)

Usage:   python3 assembler.py Prog.asm        ->  writes Prog.hack

Extra feature (K mod 3 = 1):
    A wrong line does not crash the assembler. Instead it prints a clear
    message with the line number, e.g.   Line 7: invalid instruction 'D=Q+1'
    All errors in the file are reported, and no .hack file is written
    if there was at least one error.

How it works (two readings of the file):
    First reading : remove comments / blank lines, and remember the
                    instruction number of every label like (LOOP).
    Second reading: translate each instruction into 16 bits.
                    New variables get RAM addresses 16, 17, 18, ...
"""

import re
import sys

# ---------------------------------------------------------------- tables
COMP = {
    # a = 0
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    # a = 1  (same operations, but with M instead of A)
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
for _i in range(16):
    PREDEFINED["R%d" % _i] = _i

SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


class AsmError(Exception):
    """One wrong line. Carries the line number and a message."""

    def __init__(self, line_no, message):
        super().__init__(message)
        self.line_no = line_no
        self.message = message


# ---------------------------------------------------------------- helpers
def clean(line):
    """Remove comment and ALL whitespace (spaces are not significant in Hack)."""
    line = line.split("//", 1)[0]
    return "".join(line.split())


def translate_c(code, line_no):
    """Translate one C-instruction:  dest=comp;jump"""
    dest, comp, jump = "", code, ""
    if "=" in code:
        dest, comp = code.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)

    if dest not in DEST:
        raise AsmError(line_no, "invalid destination '%s' in '%s'" % (dest, code))
    if comp not in COMP:
        if comp == "":
            raise AsmError(line_no, "missing computation in '%s'" % code)
        raise AsmError(line_no, "invalid instruction '%s'" % code)
    if jump not in JUMP:
        raise AsmError(line_no, "invalid jump '%s' in '%s'" % (jump, code))

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


# ---------------------------------------------------------------- assembler
def assemble(lines):
    """Return (list_of_16bit_strings, list_of_errors)."""
    errors = []
    symbols = dict(PREDEFINED)

    # -------- first reading: strip lines, find labels ------------------
    program = []            # (source_line_number, text)
    rom_address = 0
    for line_no, raw in enumerate(lines, start=1):
        text = clean(raw)
        if not text:
            continue

        if text.startswith("("):                      # label  (LOOP)
            if not text.endswith(")") or len(text) < 3:
                errors.append(AsmError(line_no, "bad label '%s'" % text))
                continue
            name = text[1:-1]
            if not SYMBOL_RE.match(name):
                errors.append(AsmError(line_no, "invalid label name '%s'" % name))
                continue
            if name in symbols:
                errors.append(AsmError(line_no, "label '%s' is already defined" % name))
                continue
            symbols[name] = rom_address               # label -> next instruction
        else:
            program.append((line_no, text))
            rom_address += 1

    # -------- second reading: translate --------------------------------
    next_variable = 16
    output = []
    for line_no, text in program:
        try:
            if text.startswith("@"):                  # A-instruction
                value = text[1:]
                if value == "":
                    raise AsmError(line_no, "'@' must be followed by a number or a name")
                if value.isdigit():
                    number = int(value)
                    if number > 32767:
                        raise AsmError(line_no, "address %d is too large (max 32767)" % number)
                elif SYMBOL_RE.match(value):
                    if value not in symbols:          # new variable
                        symbols[value] = next_variable
                        next_variable += 1
                    number = symbols[value]
                else:
                    raise AsmError(line_no, "invalid A-instruction '%s'" % text)
                output.append(format(number, "016b"))
            else:                                     # C-instruction
                output.append(translate_c(text, line_no))
        except AsmError as err:
            errors.append(err)

    errors.sort(key=lambda e: e.line_no)
    return output, errors


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python3 assembler.py Prog.asm")
        return 2

    path = sys.argv[1]
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except OSError as e:
        print("Cannot open '%s': %s" % (path, e.strerror))
        return 2

    output, errors = assemble(lines)

    if errors:
        for err in errors:
            print("Line %d: %s" % (err.line_no, err.message))
        print("%d error(s). No .hack file written." % len(errors))
        return 1

    out_path = path[:-4] + ".hack"
    with open(out_path, "w") as f:
        f.write("\n".join(output) + "\n")
    print("OK: %s -> %s (%d instructions)" % (path, out_path, len(output)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
