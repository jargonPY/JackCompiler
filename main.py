import os
import sys

from compiler.JackAnalyzer import JackAnalyzer
from vm.vmtranslator import VMTranslator
from assembler.assembler import Assemble

if __name__ == "__main__":
    path = sys.argv[1]

    if os.path.isdir(path):
        for file in os.listdir(path):
            if ".jack" in file:
                JackAnalyzer(path + "/" + file)
                VMTranslator(path + "/" + file.replace(".jack", ".vm"))
                Assemble(path + "/" + file.replace(".jack", ".asm"))
    else:
        JackAnalyzer(path)
        VMTranslator(path.replace(".jack", ".vm"))
        Assemble(path.replace(".jack", ".asm"))