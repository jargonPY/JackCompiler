#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from compiler.engine import CompilationEngine

class JackAnalyzer():
    """ Opens each .jack file in directory and call compilation engine """
    
    def __init__(self, path):
        
        self.path = path
        self.iter_files()
        self.parse()
        
    def iter_files(self):
        
        self.functions = { }
        self.variables = { }
        if os.path.isdir(self.path):
            for file in os.listdir(self.path):
                if ".jack" in file:
                    file = self.path + "/" + file
                    self.define_functions(file)
        else:
            file = self.path
            self.define_functions(file)
    
    def define_functions(self, file):
        
        with open(file) as f:
            for line in f:
                if len(line) == 1:continue
                elif "*" in line[0]: continue
                elif "*" in line[1]: continue
            
                if "class" in line:
                    class_name = line.split()[1]
                elif any(i in line for i in ("function", "method", "constructor")):
                    temp = line.split()
                    # temp --> [function_type, return_type, function_name]
                    func_name = temp[2].split("(")[0]
                    self.functions[class_name + "." + func_name] = [temp[0], temp[1]]
                    
    def parse(self):
        
        if os.path.isdir(self.path):
            for file in os.listdir(self.path):
                if ".jack" in file:
                    file = self.path + "/" + file
                    CompilationEngine(file, self.functions)
        else:
            file = self.path
            CompilationEngine(file, self.functions)

if __name__ == "__main__":
    path = input("Enter file or directory to compile: ")
    JackAnalyzer(path)