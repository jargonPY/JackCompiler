#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 12:06:47 2020

@author: elipalchik
"""


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
        
    
    # def has_more_tokens(self):
        
    #     if self.counter < len(self.tokens):
    #         return True
    #     else:
    #         return False
    
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
                        
    # def token_type(self, line):

    #     token = [ ]
    #     for char in line:
    #         # characters seperated by white space
    #         if char == " ":
    #             # checks if a string constant is being parsed
    #             if sum([1 for i in token if i=='"']) == 1:
    #                 token.append(char)
    #                 continue
    #             else:
    #                 if len(token) > 0:
    #                     self.classify(token)
    #                     token = [ ]
    #         elif char in self.symbols:
    #             if len(token) > 0:
    #                 self.classify(token)
    #                 token = [ ]
    #             self.token_list.append(self.symbol(char))
               
    #         else:
    #             token.append(char)
    #             continue
            
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
                self.token_list.append(self.symbol(char))
               
            else:
                token.append(char)
                continue
            
    def classify(self, token):
        """ token - a list of characters """
        
        token = "".join(token)
        if token.isdigit():
            self.token_list.append(self.int_val(token))
        elif '"' in token:
            self.token_list.append(self.string_val(token))
        elif token in self.keywords:
            self.token_list.append(self.keyword(token))
        else:
            self.token_list.append(self.identifier(token))
        
    def keyword(self, token):
        return token
       # return f"<keyword> {token} </keyword>"
    
    def symbol(self, token):
        return token
      #  return f"<symbol> {token} </symbol>"
    
    def identifier(self, token):
        return token
       # return f"<identifier> {token} </identifier>"
    
    def int_val(self, token):
        return token
       # return f"<intConstant> {token} </intConstant>"
    
    def string_val(self, token):
        return token
        #return f"<stringConst> {token} </stringConst>"
    



