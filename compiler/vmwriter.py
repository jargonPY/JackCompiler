#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class VMWriter():
    
    def __init__(self, output_file):
        # write directly to file as to avoid storing entire program in memory
        self.file = open(output_file, "w")
    
    def write_push(self, segment, index):
        
        self.file.write(f"push {segment} {index}\n")
    
    def write_pop(self, segment, index):
        
        self.file.write(f"pop {segment} {index}\n")
    
    def write_arithmetic(self, command):
        
        self.file.write(f"{command}\n")
    
    def write_label(self, label):
        
        self.file.write(f"label ({label})\n")
    
    def write_goto(self, label):
        
        self.file.write(f"goto ({label})\n")
    
    def write_if(self, label):
        
        self.file.write(f"if-goto ({label})\n")
    
    def write_call(self, name, nArgs):
        
        self.file.write(f"call {name} {nArgs}\n")
    
    def write_function(self, name, nLocals):
        
        self.file.write(f"function {name} {nLocals}\n")
    
    def write_return(self):
        
        self.file.write(f"return\n")
    
    def close(self):
        
        self.file.close()