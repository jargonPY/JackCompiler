import os
import sys

from compiler.JackAnalyzer import JackAnalyzer
from vm.vmtranslator import VMTranslator
from assembler.assembler import Assemble

if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        print("Please provide a file/directory path")
    elif (len(sys.argv) > 2):
        print("Too many arguments")
    else:
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