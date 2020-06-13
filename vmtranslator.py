#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string as s
import os

class VMTranslator():
    
    function = {"add":"add()", "sub":"sub()", "neg":"neg()", 
            "eq":"eq()", "gt":"gt()", "lt":"lt()",
            "and":"and_()", "or":"or_()", "not":"not_()",
            "label":"create_label()"}
    
    def __init__(self, path):
        
        self.path = path
        self.asm = ""
        # Label for gt, lt methods
        self.lbl = self.unique_label()
        # Translates the vm file and saves to asm file
        self.parser()
        
    def unique_label(self):
        """ Helper function to differentiate gt, lt labels """
        curr = 0
        while curr < 26:
            yield s.ascii_uppercase[curr]
            curr += 1
            
    def parser(self):
        # parse every file in directory
        if os.path.isdir(self.path):
            self.write_init()
            for file in os.listdir(self.path):
                if ".vm" in file:
                    self.file = self.path + "/" + file
                    self.parse_file()
        else:
            self.file = self.path
            self.parse_file()
        # write file to disk
        self.write()
        
    def write_init(self):
        """ 
        Initialize stack pointer to 256
        Invoke Sys.init --> invokes the main function of the main program
        """
        
        string = "@256\n"\
                 "D=A\n"\
                 "@0\n"\
                 "M=D\n"
        #string += self.goto("Sys.init")
        string += self.call_func("Sys.init", "0")
        self.asm += string
        
    def parse_file(self):
        
        with open(self.file) as f:
            # method is used to ensure that labels have the form (function:label)
            for line in f:
                # Remove comments and spaces
                if line[:2] == "//":continue
                if len(line) <= 1: continue
                line = line.split(" ")
                line = [x.replace("\n", "") for x in line]
                if "push" in line:
                    ## [push, static, 5] --> cmd=static, arg=5
                    string = self.push(line[1], line[2])
                elif "pop" in line:
                    string = self.pop(line[1], line[2])
                elif "label" in line:
                    string = self.create_label(line[1])
                elif "if-goto" in line:
                    string = self.if_goto(line[1])
                elif "goto" in line:
                    string = self.goto(line[1])
                elif "function" in line:
                    string = self.declare_func(line[1], line[2])
                elif "return" in line:
                    string = self.return_()
                elif "call" in line:
                    string = self.call_func(line[1], line[2])
                else:
                    ## In general eval is not safe, as arbitrary code will be run
                    func = VMTranslator.function[line[0]]
                    string = eval(f"self.{func}")
                ## Is there a more efficient way to concatenate the strings?
                ## Since strings are immutable, string is always recreated
                self.asm += string
                
    def add(self):
        string = "@0\n"    \
                 "M=M-1\n" \
                 "A=M\n"   \
                 "D=M\n"   \
                 "@0\n"    \
                 "M=M-1\n" \
                 "A=M\n"   \
                 "M=M+D\n" \
                 "@0\n"    \
                 "M=M+1\n"
        return string
    
    def sub(self):
        string = "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M\n"\
                 "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "M=M-D\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string
    
    def neg(self):
        string = "@0\n"   \
                 "M=M-1\n"\
                 "A=M\n"\
                 "M=-M\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string
    
    def eq(self):
        lbl = next(self.lbl)         
        string = "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M\n"\
                 "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "M=M-D\n"\
                 "D=M\n"\
                 f"@EQ{lbl}\n"\
                 "D;JEQ\n"\
                 "@0\n"\
                 "A=M\n"\
                 "M=0\n"\
                 f"@END{lbl}\n"\
                 "0;JMP\n"\
            f"(EQ{lbl})\n"\
                 "@0\n"\
                 "A=M\n"\
                 "M=-1\n"\
            f"(END{lbl})\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string

    
    def gt(self):
        lbl = next(self.lbl)
        string = "@0\n"   \
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M\n"\
                 "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M-D\n"\
                 f"@GT{lbl}\n"\
                 "D;JGT\n"\
                 "@0\n"\
                 "A=M\n"\
                 "M=0\n"\
                 f"@END{lbl}\n"\
                 "0;JMP\n"\
            f"(GT{lbl})\n"\
                 "@0\n"\
                 "A=M\n"\
                 "M=-1\n"\
            f"(END{lbl})\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string
    
    def lt(self):
        lbl = next(self.lbl)
        string = "@0\n"   \
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M\n"\
                 "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M-D\n"\
                 f"@LT{lbl}\n"\
                 "D;JLT\n"\
                 "@0\n"\
                 "A=M\n"\
                 "M=0\n"\
                 f"@END{lbl}\n"\
                 "0;JMP\n"\
            f"(LT{lbl})\n"\
                 "@0\n"\
                 "A=M\n"\
                 "M=-1\n"\
            f"(END{lbl})\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string
    
    def and_(self):
        string = "@0\n"    \
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M\n"\
                 "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "M=D&M\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string

    
    def or_(self):
        string = "@0\n"   \
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=M\n"\
                 "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "M=D|M\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string
    
    def not_(self):
        string = "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "M=!M\n"\
                 "@0\n"\
                 "M=M+1\n"
        return string
    
    """ PUSH / POP COMMANDS """
    
    def pop(self, cmd, arg):
        if cmd in ["local", "argument", "this", "that"]:
            ## Maps to RAM location
            trans = {"local":"1", "argument":"2", "this":"3", "that":"4"}
            string = f"@{arg}\n" \
                     "D=A\n"           \
                     f"@{trans[cmd]}\n"        \
                     "M=M+D\n"         \
                     "@0\n"            \
                     "M=M-1\n"         \
                     "A=M\n"           \
                     "D=M\n"           \
                     f"@{trans[cmd]}\n"           \
                     "A=M\n"           \
                     "M=D\n"            \
                     f"@{arg}\n"         \
                     "D=A\n"           \
                     f"@{trans[cmd]}\n"           \
                     "M=M-D\n"           
        if cmd == "temp":
            loc = 5 + int(arg)
            string = "@0\n"\
                     "M=M-1\n"\
                     "A=M\n"\
                     "D=M\n"\
                     f"@{loc}\n"\
                     "M=D\n"
        if cmd == "pointer":
            # SP-- , This/That = *SP
            point = {"0":"3", "1":"4"}
            string = "@0\n" \
                     "M=M-1\n"\
                     "A=M\n"\
                     "D=M\n"\
                     f"@{point[arg]}\n"\
                     "M=D\n"
        if cmd == "static":
            # class/method has access to static variables of the file
            # threrefore static variables act as class variables
            label = self.file.split("/")[-1].replace(".vm", "") + f".{arg}"
            # SP-- , @file.arg = *SP
            string = "@0\n"   \
                     "M=M-1\n"\
                     "A=M\n"\
                     "D=M\n"\
                     f"@{label}\n"\
                     "M=D\n"
        return string
    
    def push(self, cmd, arg):
        if cmd == "constant":
            string = f"@{arg}\n"  \
                     "D=A\n"      \
                     "@0\n"       \
                     "A=M\n"      \
                     "M=D\n"      \
                     "@0\n"       \
                     "M=M+1\n"
        if cmd in ["local", "argument", "this", "that"]:
            ## Maps to RAM location
            trans = {"local":"1", "argument":"2", "this":"3", "that":"4"}
            string = f"@{trans[cmd]}\n" \
                     "D=M\n"            \
                     f"@{arg}\n"        \
                     "A=D+A\n"          \
                     "D=M\n"            \
                     "@0\n"             \
                     "A=M\n"            \
                     "M=D\n"            \
                     "@0\n"             \
                     "M=M+1\n"   
        if cmd == "temp":
            loc = 5 + int(arg)
            string = f"@{loc}\n"   \
                     "D=M\n"     \
                     "@0\n"\
                     "A=M\n"\
                     "M=D\n"     \
                     "@0\n"      \
                     "M=M+1\n"
        if cmd == "pointer":
            ## 0 --> THIS --> RAM[3] , 1 --> THAT --> RAM[4]
            point = {"0":"3", "1":"4"}
            string = f"@{point[arg]}\n" \
                     "D=M\n"            \
                     "@0\n"             \
                     "A=M\n"            \
                     "M=D\n"            \
                     "@0\n"             \
                     "M=M+1\n"
        if cmd == "static":
            label = self.file.split("/")[-1].replace(".vm", "") + f".{arg}"
            string = f"@{label}\n" \
                     "D=M\n"       \
                     "@0\n"        \
                     "A=M\n"       \
                     "M=D\n"       \
                     "@0\n"        \
                     "M=M+1\n"
        return string
    
    """ BRANCHING COMMANDS """
    
    def create_label(self, label):

        return f"({label})\n"

    def goto(self, label):
        string = f"@{label}\n"\
                 "0;JMP\n"
        return string
    
    def if_goto(self, label):
        string = "@0\n"\
                 "M=M-1\n"\
                 "A=M\n"\
                 "D=-M\n"\
                 f"@{label}\n"\
                 "D;JGT\n"
        return string
    
    """ SUBROUTINE COMMANDS """
    
    def call_func(self, func_name, num_args):
        lbl = next(self.lbl) ## All function names should be unique
        # return address, continue executing from this line onwards
        string = self.push("constant", f"RETURN.{func_name}.{lbl}")
        # Pushes LCL --> RAM[1] onto stack
        string += "@1\n"\
                  "D=M\n"\
                  "@0\n"\
                  "A=M\n"\
                  "M=D\n"\
                  "@0\n"\
                  "M=M+1\n"\
                  "@2\n"\
                  "D=M\n"\
                  "@0\n"\
                  "A=M\n"\
                  "M=D\n"\
                  "@0\n"\
                  "M=M+1\n"\
                  "@3\n"\
                  "D=M\n"\
                  "@0\n"\
                  "A=M\n"\
                  "M=D\n"\
                  "@0\n"\
                  "M=M+1\n"\
                  "@4\n"\
                  "D=M\n"\
                  "@0\n"\
                  "A=M\n"\
                  "M=D\n"\
                  "@0\n"\
                  "M=M+1\n"
        # Set ARG=SP-n-5
        string += f"@{num_args}\n"\
                  "D=-A\n"\
                  "@5\n"\
                  "D=D-A\n"\
                  "@0\n"\
                  "D=M+D\n"\
                  "@2\n"\
                  "M=D\n"
        # Set LCL=SP
        string += "@0\n"\
                  "D=M\n"\
                  "@1\n"\
                  "M=D\n"
        # goto function
        string += self.goto(func_name)
        # create label for return address, location of command following the call command
        string += f"(RETURN.{func_name}.{lbl})\n"
        return string
    
    def declare_func(self, func_name, num_local):
        # Each function should generate a label that refers to its entry point
        # Initialize local variables, for i in num_args to 0 and push to stack
        string = f"({func_name})\n"
        for k in range(int(num_local)):
            string += self.push("constant", "0")
            string += self.pop("local", f"{k}")
        return string
                
    def return_(self):
        
        string = "@1\n"\
                 "D=M\n"\
                 "@5\n"\
                 "M=D\n"\
                 "A=D-A\n"\
                 "D=M\n"\
                 "@6\n"\
                 "M=D\n"
        # Return value
        string += self.pop("argument", "0")
        # SP = ARG + 1
        string += "@2\n"\
                 "D=M\n"\
                 "@1\n"\
                 "D=D+A\n"\
                 "@0\n"\
                 "M=D\n"
        string += self._restore()
        # implements goto return address
        string += "@6\n"\
                  "A=M\n"\
                  "0;JMP\n"
        return string
    
    def _restore(self):
        # Restores This, That, Arg, Local
        string = "@5\n"\
                 "D=M\n"\
                 "@1\n"\
                 "A=D-A\n"\
                 "D=M\n"\
                 "@4\n"\
                 "M=D\n"\
                 "@5\n"\
                 "D=M\n"\
                 "@2\n"\
                 "A=D-A\n"\
                 "D=M\n"\
                 "@3\n"\
                 "M=D\n"\
                 "@5\n"\
                 "D=M\n"\
                 "@3\n"\
                 "A=D-A\n"\
                 "D=M\n"\
                 "@2\n"\
                 "M=D\n"\
                 "@5\n"\
                 "D=M\n"\
                 "@4\n"\
                 "A=D-A\n"\
                 "D=M\n"\
                 "@1\n"\
                 "M=D\n"
        return string
    
    def write(self):
        
        if os.path.isdir(self.path):
            file_name = self.path + "/" + self.path.split("/")[-1] + ".asm"
        else:
            file_name = self.path.replace(".vm", ".asm")
            
        with open(file_name, "w") as f:
            f.write(self.asm)

        
if __name__ == "__main__":
    print("Enter file or directory to translate: ")
    path = input()
    VMTranslator(path)
        
        
        
        
        
        
        