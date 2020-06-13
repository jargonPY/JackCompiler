#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class SymboleTable():
    
    def __init__(self):
        
        self.class_scope = { }
        # define a running index for each variable
        self.static = 0
        self.field = 0
    
    def startSubroutine(self):
        
        self.subroutine_scope = { }
        self.arg = 0
        self.var = 0
    
    def define(self, name, type_, kind):
        
        if kind == "static":
            self.class_scope[name] = [type_, kind, self.static]
            self.static += 1
        elif kind == "field":
            self.class_scope[name] = [type_, kind, self.field]
            self.field += 1
        elif kind == "argument":
            self.subroutine_scope[name] = [type_, kind, self.arg]
            self.arg += 1
        else:
            self.subroutine_scope[name] = [type_, kind, self.var]
            self.var += 1
    
    def var_count(self, kind):
        
        if kind == "static":
            return self.static
        elif kind == "field":
            return self.field
        elif kind == "argument":
            return self.arg
        else:
            return self.var
        
    def kind_of(self, name):
        
        if name in self.subroutine_scope.keys():
            # The kind is the second element in the list
            return self.subroutine_scope[name][1]
        else:
            return None
    
    def type_of(self, name):
        
        if name in self.subroutine_scope.keys():
        # The kind is the first element in the list
            return self.subroutine_scope[name][0]
        else:
            return None
    
    def index_of(self, name):
        
        if name in self.subroutine_scope.keys():
            # The kind is the third element in the list
            return self.subroutine_scope[name][2]
        else:
            return None
    
