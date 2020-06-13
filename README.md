# JackCompiler

Implementation of the Jack programming language. Jack is a Java like OOP language that was designed for the computer architecture course
at www.nand2tetris.org.

The implementation includes:
  - The assembler for the hack computer (assembler designed for the specific instruction set of the hack computer)
  - The virtual machine translator, similar in concept to Java's JVM, its a stack based abstraction that implements the
    "write once run anywhere" paradigm
  - The compiler for the Jack language, compiles to the virtual machine

Instructions, run the following commands from the terminal:
  - To run the compiler:
      python JackAnalyzer.py
  - To run VM translator:
      python vmtranslator.py
  - To run assembler:
      python assembler.py

  - In all cases you will be prompted to enter a path to the file that you'd like translate. Once the path is provided the program will       automatically translate and create a new file in the same directory. If a Jack program comprising of multiple files needs to be           compiled you can provide the directory path, the program will parse each file automatically.
