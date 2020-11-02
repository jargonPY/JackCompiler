#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class JackTokenizer():
    
    def __init__(self, file):
        
        self.symbols = ["{", "}", "[", "]", "(", ")", ".", ";", "+", "-", "*", "/",
                        "&", "|", "<", ">", "=", "~", ","]
        self.keywords = ["class", "contructor", "function", "method", "field", "static",
                        "var", "int", "char", "boolean", "void", "true", "false", 
                        "null", "this", "let", "do", "if", "else", "while", "return"]
        self.file = file
        self.token_list = [ ]
        self.counter = 0
        
        self.parse() # start tokenizing
    
    def advance(self):
        
        self.curr_token = self.token_list[self.counter]
        self.counter += 1
            
        return self.curr_token
    
    def peek(self):
        
        self.curr_token = self.token_list[self.counter]
        return self.curr_token
    
    def open_file(self):
        
        with open(self.file) as f:
            for line in f:
                yield line
    
    def parse(self):
        
        line_gen = self.open_file() # Create generator
        for line in line_gen:
            line = line.strip()
            # remove lines that only contain whitespace
            if len(line) == 0: continue
            # remove all lines with comments
            if "/**" in line: continue
            if "*/" in line: continue
            if line[0] == "*": continue
            # remove in-line comments
            if "//" in line:
                line = line.split("//")[0]
                if len(line) == 0: continue
            # tokenize line
            self.token_type(line)
            
    def token_type(self, line):

        token = [ ]
        for char in line:
            # checks if a string constant is being parsed
            if sum([1 for i in token if i=='"']) == 1:
                    token.append(char)
                    continue
            # characters seperated by white space
            elif char == " ":
                if len(token) > 0:
                    self.classify(token)
                    token = [ ]
            elif char in self.symbols:
                if len(token) > 0:
                    self.classify(token)
                    token = [ ]
                self.token_list.append(char)
               
            else:
                token.append(char)
                continue

    def classify(self, token):

        token = "".join(token)
        self.token_list.append(token)

