#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from symboletable import SymboleTable
from vmwriter import VMWriter
from jacktoken import JackTokenizer

class CompilationEngine():
    
    def __init__(self, file, functions):
        
        self.symb = {"+":"add", "-":"sub", "*":"call Math.multiply 2", "/":"call Math.divide 2",
                          "<":"lt", ">":"gt", "~":"not", "=":"eq", "|":"or",
                          "&":"and"}
        
        self.functions = functions
        self.tokenizer = JackTokenizer(file)
        self.vmwriter = VMWriter(file.replace(".jack", ".vm"))
        
        self.local_scope = { } # used to store the defined variables of the function
        self.count = 0
        self.labels = [ ]
        self.token = None
        
        self.compile_class()
        
    def get_next(self, num):
        
        for i in range(num):
            token = self.tokenizer.advance()
        return token
        
    def compile_class(self):
        
        self.scope_table = SymboleTable()
        self.class_name =  self.get_next(2) # skip 'class'
        self.token = self.get_next(2) # skip '{'
        
        self.compile_class_var_dec()
        while self.token != "}":
            self.compile_subroutine()
            self.token = self.get_next(1)
            
        self.vmwriter.close()
        
    def compile_class_var_dec(self):

        while self.token not in ["constructor", "function", "method"]:
            if self.token in ["field", "static"]:
                kind = self.token
                type_ = self.get_next(1)
                name = self.get_next(1)
            else:
                name = self.token
            self.scope_table.define(name, type_, kind)
            self.token = self.get_next(2)
                
    def compile_subroutine(self):
        
        self.scope_table.startSubroutine()
        function_type = self.token # constructor/method/function      
        self.func_name = self.class_name + "." + self.get_next(2) # function type name
        
        # define arguments
        if function_type == "method":
            self.scope_table.define("this", f"{self.class_name}", "argument") # adds 'this' to argument list
        self.token = self.get_next(2) # skip "("
        self.compile_paramterlist()
        
        # define local variables
        self.token = self.get_next(2) # skip '{'
        self.compile_var_dec()
        # assign 'this' to current object
        self._assign_pointer(function_type)
        # compile statements
        self._iter_statements()
            
    def compile_paramterlist(self):
        
        while self.token != ")":
            kind = "argument"
            type_ = self.token 
            name = self.get_next(1)
            self.scope_table.define(name, type_, kind)
            self.token = self.get_next(1) # either ',' or ')'
            if self.token == ",":
                self.token = self.get_next(1)
                
    def _assign_pointer(self, function_type):
        
        # assign pointer 'this' to object
        if function_type == "constructor":
            num_fields = self.scope_table.var_count("field")
            self.vmwriter.write_push("constant", num_fields)
            self.vmwriter.write_call("Memory.alloc", 1)
            self.vmwriter.write_pop("pointer", 0)
        elif function_type == "method":
            self.vmwriter.write_push("argument", 0)
            self.vmwriter.write_pop("pointer", 0)
       
    def compile_var_dec(self):

        while self.token not in ["let", "do", "while", "if", "return"]:
            kind = "var"
            if self.token == "var":
                type_ = self.get_next(1)
                name = self.get_next(1)
            else:
                name = self.token
            self.scope_table.define(name, type_, kind)
            self.token = self.get_next(2) # will be either "var_name", "var", or "statement"
        # create label for the function
        self.vmwriter.write_function(self.func_name, self.scope_table.var_count("var"))
    
    def compile_statements(self):

        if self.token == "if":
            self.compile_if()
        elif self.token == "while":
            self.compile_while()
        elif self.token == "do":
            self.compile_do()
        elif self.token == "let":
            self.compile_let()
        elif self.token == "return":
            self.compile_return()
        else:
            print("COMPILE_STATEMENTS: ", self.token)
    
    def compile_do(self):
        """ do subroutineCall """
        self.token = self.get_next(1)
        self.compile_expression()
            
    def compile_let(self):
        """ let var([exp]?) = exp """

        var = self.get_next(1) # gets variable
        temp = self.get_next(1)
        # if variable is an array
        if temp == "[":
            self.compile_array(var)
        else:
            self.token = self.get_next(1) # right-hand side expression
            self._add_to_local_scope(var)
            self.compile_expression() # writes right-hand to stack
            kind, index = self.get_variable(var)
            self.vmwriter.write_pop(kind, index)
    
    def compile_array(self, var):
        
        kind, index = self.get_variable(var)
        self.vmwriter.write_push(kind, index)
        self.token = self.get_next(1) # starts expression in brackets --> var[expression
        self.compile_expression()
        self.vmwriter.write_arithmetic("add")
        self.token = self.get_next(2) # skip "="
        self.compile_expression()
        self.vmwriter.write_pop("temp", "0")
        self.vmwriter.write_pop("pointer", "1")
        self.vmwriter.write_push("temp", "0")
        self.vmwriter.write_pop("that", "0")
        
    def _add_to_local_scope(self, var):
        # let variable = Class.method()
        if self.token[0].isupper():
            self.local_scope[var] = self.token
        
    def compile_while(self):
        
        self.count += 1
        self.labels.append(self.count)
        self.vmwriter.write_label(f"WHILE.B.{self.labels[-1]}")
        
        # code for computing condition
        self.token = self.get_next(2) # skip "("
        self.compile_expression()
        # negate it
        self.vmwriter.write_arithmetic("not")
        self.vmwriter.write_if(f"WHILE.E.{self.labels[-1]}")
        
        # code for statement in loop
        self.token = self.get_next(1)
        self._iter_statements()
        
        self.vmwriter.write_goto(f"WHILE.B.{self.labels[-1]}")
        self.vmwriter.write_label(f"WHILE.E.{self.labels[-1]}")
        del self.labels[-1]
        
    def compile_return(self):
        """ Called when return is reached """
        
        self.token = self.get_next(1)
        if self.token == ";": # if void function (i.e. doesn't return a value)
            self.vmwriter.write_push("constant", "0")
        else: # self.token is an expression
            self.compile_expression()
        self.vmwriter.write_return()
        
    def compile_if(self):

        self.count += 1
        self.labels.append(self.count)
        
        self.token = self.get_next(2) # skip '('
        self.compile_expression()
        # negate it
        self.vmwriter.write_arithmetic("not")
        self.vmwriter.write_if(f"IF.{self.labels[-1]}")
        
        # compile statement
        self.token = self.get_next(1)
        self._iter_statements()

        # check if there is an 'else' statement
        if self.tokenizer.peek() != "else":
            self.vmwriter.write_label(f"IF.{self.labels[-1]}")
            del self.labels[-1]
            return None
        else:
            self.vmwriter.write_goto(f"ELSE.{self.labels[-1]}")
            # create the labels
            self.vmwriter.write_label(f"IF.{self.labels[-1]}")
      
        self.token = self.get_next(2)
        self._iter_statements()
        self.vmwriter.write_label(f"ELSE.{self.labels[-1]}")
        del self.labels[-1]
        
    def _iter_statements(self):
        
        while self.token != "}":
            self.compile_statements()
            self.token = self.get_next(1)
            
    def compile_expression(self):
        """ exp --> term (op term)? """
            
        exp = [ ]
        while self.token not in (";", "{", "]"): # tuples are fixed length
            if self.token == "(": 
                new_exp = self.compile_expression_list()
                if len(new_exp) > 0:
                    exp.append(new_exp)
                    
            # '[' indicates an array
            elif self.token == "[":
                new_exp = self.compile_expression_list()
                exp[-1] = ["Array", exp[-1], new_exp]
                
            elif self.token == ".":
                exp[-1] = exp[-1] + "." + self.get_next(1)
                
            else:
                prev = self.token
                # closing brakcet gets appended while parsing conditions (while, if)
                if prev != ")":
                    exp.append(prev)
            self.token = self.get_next(1)
        self.code_write(exp)
            
    def compile_expression_list(self):
       
        new_exp = [ ]
        temp = [ ]
        self.token = self.get_next(1)
        while self.token not in [")", "]"]:
           
            if self.token == "(":
               x = self.compile_expression_list()
               new_exp.append(x)
               
            elif self.token == "[":
                x = self.compile_expression_list()
                new_exp[-1] = ["Array", new_exp[-1], x]
                
            elif self.token == ".":
                new_exp[-1] = new_exp[-1] + "." + self.get_next(1)
                self.token = self.get_next(1)
                args = self.compile_expression_list()
                new_exp[-1] = [new_exp[-1], args]
                
            elif self.token == ",":
                temp.append(new_exp)
                new_exp = [ ]
            
            else:
                new_exp.append(self.token)
            self.token = self.get_next(1)
            
        if len(temp) > 0:
            temp.append(new_exp)
            new_exp = temp
        # tell code_write that its a function call for functions with no arguments ex. Square.new()   
        if len(new_exp) == 0: 
            new_exp = "func_call"
        return new_exp
    
    def code_write(self, exp):
        
        # exp --> term
        if type(exp) == str:
            self.term = exp
            self.compile_term()
        # exp --> [expression]
        elif len(exp) == 1:
            exp = exp[0]
            self.code_write(exp)
        # exp --> [Array, variable, [expression]]
        elif exp[0] == "Array":
            self.code_write(exp[2])
            self._right_array(exp[1])
            
        # op exp --> in this form op = - (neg) or op = ~ (not)
        elif exp[0] in self.tokenizer.symbols:
            self.code_write(exp[1])
            self._op_uniary(exp[0])
            
        # exp op exp
        elif exp[1] in self.tokenizer.symbols:
           # print("SYMB: ", exp[1])
            self.code_write(exp[0])
            self.code_write(exp[2])
            self.vmwriter.write_arithmetic(self.symb[exp[1]])
            
        # f(exp1, exp2, ...)
        elif len(exp) == 2:  # second item should be a list
            name, return_type, num_args = self._compile_call(exp)
            self.vmwriter.write_call(name, num_args)
            # void functions return "0" which must be popped from the stack     
            if return_type == "void":
                self.vmwriter.write_pop("temp", "0")        
                
        else:
            print("CODE WRITE NOT WORKING: ", exp, type(exp), len(exp))
    
    def _right_array(self, var):
        """ wrties array when array is on the right of a variable declaration
            let variable = array[index] """
        
        kind, index = self.get_variable(var)
        self.vmwriter.write_push(kind, index)
        self.vmwriter.write_arithmetic("add")
        self.vmwriter.write_pop("pointer", "1")
        self.vmwriter.write_push("that", "0")
        
    def _op_uniary(self, exp):
        """ used to write the operations 'not' (~) and 'neg' (-)
            called when exp = [operation, expression] """
            
        if exp[0] == "-":
            self.vmwriter.write_arithmetic("neg")
        else:
            self.vmwriter.write_arithmetic("not")
            
    def _compile_call(self, exp):
        """ exp --> [function_call, [expressions]] """
        
        num_args = 0
        # user defined class.function()
        if exp[0] in self.functions.keys(): 
            name = exp[0]
        # game.run() --> Square.run()
        elif "." in exp[0]:
            temp = exp[0].split(".") # temp = [variable, function]
            variable = temp[0]
            if variable in self.local_scope.keys():
                name = self.local_scope[variable] + "." + temp[1]
            else:
                print("Assumed to be OS call: ", exp)
                num_args = self._compile_args(exp, num_args)
                return exp[0], False, num_args
        # function calls within class, run() --> Square.run()
        else: 
            variable = exp[0]
            name = self.class_name + "." + exp[0]
               
        if self.functions[name][0] == "method":
            kind, index = self.get_variable(variable) # add 'this' as argument
            if kind == None:
                if "this" in self.scope_table.subroutine_scope.keys():
                    self.vmwriter.write_push("argument", 0)
                else:
                    self.vmwriter.write_push("pointer", 0)
            else:
                self.vmwriter.write_push(kind, index)
            num_args += 1
        
        return_type = self.functions[name][1] # return_type --> void, int etc.
        num_args = self._compile_args(exp, num_args)
        return name, return_type, num_args
    
    def _compile_args(self, exp, num_args):
        # add function arguments to stack
        if exp[1] != "func_call": # exp[1] --> [expressions]
            if type(exp[1][0]) == str:
                self.code_write(exp[1])
                num_args += 1
            else:
                for arg in exp[1]:
                    self.code_write(arg)
                    num_args += 1
        return num_args
 
    def compile_term(self):
        
        kind, index = self.get_variable(self.term)
        if (kind != None) and (self.term != "this"):
            self.vmwriter.write_push(kind, index)
            
        elif self.term.isdigit():
            self.vmwriter.write_push("constant", self.term)
            
        elif self.term == "true":
            self.vmwriter.write_push("constant", 1) 
            self.vmwriter.write_arithmetic("neg") # true is represented by -1
            
        elif self.term == "false":
            self.vmwriter.write_push("constant", 0)
            
        elif self.term == "null":
            self.vmwriter.write_push("constant", 0)
            
        elif self.term == "this": # this
            self.vmwriter.write_push("pointer", 0)
            
        elif '"' in self.term: # stringConstant
            self.compile_string()
        else:
            print("COMPILE_TERM NOT WORKING", self.term)
    
    def get_variable(self, variable):
        
        if variable in self.scope_table.class_scope.keys():
            kind = self.scope_table.class_scope[variable][1]
            if kind == "field":
                kind = "this"            
            index = self.scope_table.class_scope[variable][2]
            return kind, index
            
        elif variable in self.scope_table.subroutine_scope.keys(): # push subroutine variable
            kind = self.scope_table.kind_of(variable)
            if kind == "var":
                kind = "local"
            index = self.scope_table.index_of(variable)
            return kind, index
        
        else:
            return None, None
            
    def compile_string(self):
        
        self.vmwriter.write_push("constant", len(self.term))
        self.vmwriter.write_call("String.new", 1)
        for char in self.term:
            self.vmwriter.write_push("constant", ord(char))
            self.vmwriter.write_call("String.appendChar", 2) # 2 args since 'this' is an arg
        


    
    
    
    

    
    
    
    
    


    
    