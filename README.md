# JackCompiler

Implementation of the Jack programming languate. Jack is a Java like OOP language that was designed for the computer architecture course
at www.nand2tetris.org. 

The implementation includes:
  - The assembler for the hack computer (assmbler designed for the specific instruction set of the hack computer)
  - The virtual machine translator, similar in concept to Java's JVM, its a stack based abstraction that implements the
    "write once run anywhere" paradigm
  - The compiler for the Jack language, compiles to the virtual machine
