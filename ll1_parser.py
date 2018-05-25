# This is a LL(1) parser for grammars. It may not be optimized but it's
# a project i'm conducting in the free time during my university studies.
#
# Check readme.txt in order to see input format of the grammar and eventual
# output format.
#
# Author: Matteo Amatori

import csv
import numpy
from utils import first_and_follow_calculation as ffc
from prettytable import PrettyTable

class nonTerminal:
    name = ''
    first_l = []
    follow_l = []
    isStartSymbol = False

    def __init__ (self, non_terminal_name):
        self.name = non_terminal_name
        self.first_l = []
        self.follow_l = []
        self.isStartSymbol = False

    def add_first (self, element):
        self.first_l.append(element)

    def add_follow (self, element):
        self.follow_l.append(element)

# variables declaration section
terminal_names = []
non_terminal_names = []                                 # just strings
non_terminals = []                                      # actual non-terminals

# input section
with open("utils/grammar.txt", 'r', encoding = 'ISO-8859-1') as f:
    input_file = csv.reader(f)
    grammar = []
    for row in input_file:
        if (len(row) != 0):
            grammar = grammar + [row]

f.close()

# collecting non-terminals
for index in range(len(grammar)):
    driver = grammar[index][0][0]
    if driver not in non_terminal_names:
        non_terminal_names.append(driver)
        non_terminals.append(nonTerminal(driver))

#collecting terminals
terminal_names.append(" ")
for production in grammar:
    for index in range(len(production[0])):
        if (production[0][index] != '#' and production[0][index] != '-' and production[0][index] != '>'):
            if (ffc.isTerminal(production[0][index])):
                if (production[0][index] not in terminal_names):
                    terminal_names.append(production[0][index])
terminal_names.append("$")

non_terminals[0].isStartSymbol = True

print("Grammar:")
for element in grammar:
    print(element[0])

# first computation
print("------------------------- First Computation --------------------------")
for i in range(0, 2):
    for element in reversed(non_terminals):
        for row in grammar:
            ffc.compute_first(element, row, non_terminals, 3)

for element in non_terminals:
    print("First(" + element.name + "):")
    print(element.first_l)

# follow computation
print("------------------------- Follow Computation -------------------------")
for i in range(0, 2):
    for element in non_terminals:
        for row in grammar:
            ffc.compute_follow(element, row, non_terminals, 3)

for element in non_terminals:
    print("Follow(" + element.name + "):")
    print(element.follow_l)

# table Computation
ll1_table = PrettyTable(terminal_names)

table = [["" for x in range(len(terminal_names))] for y in range(len(non_terminal_names))]

for idx_row, element in enumerate(non_terminal_names, 0):
    for idx_col in range(len(terminal_names)):
        if (idx_col == 0):
            table[idx_row][idx_col] = element
        else:
            table[idx_row][idx_col] = []

for production in grammar:
    p_prog = 3
    if (production[0][p_prog] == '#'):
        for element in non_terminals:
            if (element.name == production[0][0]):
                nT = element
                for follow_nT in nT.follow_l:
                    driver_index = 0
                    terminal_index = 0
                    for idx, element_1 in enumerate(non_terminal_names, 0):
                        if (element_1 == production[0][0]):
                            driver_index = idx
                    for idx, element_2 in enumerate(terminal_names, 0):
                        if (element_2 == follow_nT):
                            terminal_index = idx
                    table[driver_index][terminal_index].append(production[0])
    elif (ffc.isTerminal(production[0][p_prog])):
        driver_index = 0
        terminal_index = 0
        for idx, element in enumerate(non_terminal_names, 0):
            if (element == production[0][0]):
                driver_index = idx
        for idx, element in enumerate(terminal_names, 0):
            if (element == production[0][p_prog]):
                terminal_index = idx
        table[driver_index][terminal_index].append(production[0])
    elif (ffc.isNonTerminal(production[0][p_prog])):
        for element in non_terminals:
            if (element.name == production[0][p_prog]):
                nT = element
                for first_nT in nT.first_l:
                    if (first_nT != '#'):
                        driver_index = 0
                        terminal_index = 0
                        for idx, element_1 in enumerate(non_terminal_names, 0):
                            if (element_1 == production[0][0]):
                                driver_index = idx
                        for idx, element_2 in enumerate(terminal_names, 0):
                            if (element_2 == first_nT):
                                terminal_index = idx
                        table[driver_index][terminal_index].append(production[0])
                    else:
                        while (p_prog < len(production[0])-1):
                            if (ffc.isTerminal(production[0][p_prog+1])):
                                driver_index = 0
                                terminal_index = 0
                                for idx, element in enumerate(non_terminal_names, 0):
                                    if (element == production[0][0]):
                                        driver_index = idx
                                for idx, element in enumerate(terminal_names, 0):
                                    if (element == production[0][p_prog+1]):
                                        terminal_index = idx
                                table[driver_index][terminal_index].append(production[0])
                            elif (ffc.isNonTerminal(production[0][p_prog+1])):
                                for element in non_terminals:
                                    if (element.name == production[0][p_prog+1]):
                                        nT = element
                                        for first_nT in nT.first_l:
                                            if (first_nT != '#'):
                                                driver_index = 0
                                                terminal_index = 0
                                                for idx, element_1 in enumerate(non_terminal_names, 0):
                                                    if (element_1 == production[0][0]):
                                                        driver_index = idx
                                                for idx, element_2 in enumerate(terminal_names, 0):
                                                    if (element_2 == first_nT):
                                                        terminal_index = idx
                                                table[driver_index][terminal_index].append(production[0])
                            p_prog += 1

for i in range(len(non_terminal_names)):
    ll1_table.add_row(table[i])

print("\nLL(1) parsing table of the grammar G:")
print(ll1_table)

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
