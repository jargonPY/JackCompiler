#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Assemble():
    
    def __init__(self, file):
        
        self.MEMORY = 16
        self.INSTRUCTION = 0
        self.LOOP = None
        self.file = file
        self.binary = ""
        
        self.symbols = {"null":"000", "M":"001", "D":"010", "MD":"011",
                        "A""":"100", "AM":"101" , "AD":"110", "AMD":"111",
                        "null":"000", "JGT":"001", "JEQ":"010", "JGE":"011",
                        "JLT":"100", "JNE":"101" , "JLE":"110", "JMP":"111",
                        }

    def parse(self):
        
        with open(self.file) as f:
            ## First run
            for line in f:
                if (line[:2] == "//") or (len(line) == 1):continue
                ## Remove trailing comments
                line = line.split("//")[0]
                self.first_pass(line)
                ## Next instruction
                self.INSTRUCTION += 1
            ## Second run
            for line in f:
                if (line[:2] == "//") or (len(line) == 1):continue
                line = line.split("//")[0]
                self.binary += self.second_pass(line)
                self.binary += "\n"
                    
    def first_pass(self, line):
        """ Adds symbols representing jump points """
     
        if "(" and ")" in line:
            symbol = line.strip("()")
            self.symbols[symbol] = '{0:016b}'.format(self.INSTRUCTION)
                
            
    def second_pass(self, line):
        """ Adds all A and C instructions """
            
        if "@" in line:
            symbol = line.strip("@") ## Removes comments and @
            return self.get_a(symbol)
            
        ## dest = compt ; jump
        elif "=" and ";" in line:
            symbol = symbol.split("=")
            dest = symbol[0]
            comp = symbol[1].split(";")[0]
            jump = symbol[1].split(";")[1]
        elif "=" in line:
            symbol = symbol.split("=")
            dest = symbol[0]
            comp = symbol[1]
            jump = "null"
        else:
            symbol = symbol.split(";")
            dest = "null"
            comp = symbol[0]
            jump = symbol[1]
        return self.get_c(dest, comp, jump)
    
    def get_a(self, symbol):
        """ Gets A-instructions """
        
        if symbol.isdigit():
                return '{0:016b}'.format(int(symbol))
            
        elif symbol in self.symbols:
            return self.symbols[symbol]
        
        else:
            self.symbols[symbol] = '{0:016b}'.format(self.MEMORY)
            self.MEMORY += 1
            return self.symbols[symbol]
    
    def get_c(self, dest, comp, jump):
        """ Gets C-instructions """
        
        code="111" ## Beggining of a C-instruction
        code += self.symbols[dest] + self.symbols[comp] + self.symbols[jump]
        return code
    
    def write(self):
        
        file = self.file.replace(".asm", ".hash")
        with open(file, "w") as f:
            f.write(self.binary)
            
    
if __name__ == "__main__":
    file = input("Path to file: ")
    assembler = Assemble(file)
    assembler.parse()
    assembler.write()
    
    
    
    