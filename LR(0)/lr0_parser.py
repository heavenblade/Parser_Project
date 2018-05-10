# This is a LR(0) parser for grammars. It may not be optimized but it's
# a project i'm conducting in the free time during my university studies.
#
# Check readme.txt in order to see input format of the grammar and eventual
# output format.
#
# Author: Matteo Amatori

import csv
import numpy
import first_and_follow_calculation as ffc
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

class lr0Item:
    production = []
    type = ""
    dot = 0
    isReductionItem = False

    def __init__ (self, production, type, dot, reduct):
        self.production = production
        self.type = type
        self.dot = dot
        self.isReductionItem = reduct

def create_new_item (production, type, dot, reduct):
    new_state = lr0Item(production, type, dot, reduct)
    return new_state

def check_item_equality(item_1, item_2):
    if (item_1.production == item_2.production):
        if (item_1.type == item_2.type):
            if (item_1.dot == item_2.dot):
                if (item_1.isReductionItem == item_2.isReductionItem):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

def verify_if_reduction(item, dot):
    if (dot == len(item.production)):
        return True
    else:
        return False

class lr0State:
    name = 0
    item_l = []
    isInitialState = False

    def __init__ (self, state_count):
        self.name = state_count
        self.item_l = []
        self.isInitialState = False

    def add_item (self, item):
        self.item_l.append(item)

def create_new_state (name):
    new_state = lr0State(name)
    return new_state

class transition:
    name = 0
    element = ''
    starting_state = 0
    ending_state = 0

    def __init__ (self, transition_count, elem, s_state, e_state):
        self.name = transition_count
        self.element = elem
        self.starting_state = s_state
        self.ending_state = e_state

def create_new_transition (name, element, s_state, e_state):
    new_transition = transition(name, element, s_state, e_state)
    return new_transition

# variables declaration section
terminal_names = []                                     # strings of terminals
non_terminal_names = []                                 # just strings
non_terminals = []                                      # actual non-terminals
lr0_states = []                                         # array of lr0-states
transitions = []                                        # array of transitions between lr0-states
state_counter = 0
transition_counter = 0

# input section
with open("grammar.txt", 'r') as f:
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

# collecting terminals
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
for i in range(0, 1):
    for element in non_terminals:
        for row in grammar:
            ffc.compute_follow(element, row, non_terminals, 3)

for element in non_terminals:
    print("Follow(" + element.name + "):")
    print(element.follow_l)

# creation of augmented grammar
a_grammar = []
prev_starting_symb = ''
for element in non_terminals:
    if element.isStartSymbol:
        prev_starting_symb = element.name
starting_prod = "Q->" + prev_starting_symb
a_grammar.append(starting_prod)
for prod in grammar:
    a_grammar.append(prod[0])

print("\nAugmented grammar:")
for production in a_grammar:
    print(production)

# computation of the LR(0) automa
initial_state = create_new_state(state_counter)
state_counter += 1
initial_state.isInitialState = True
item = create_new_item(a_grammar[0], "Kernel", 3, False)
initial_state.item_l.append(item)
for kernel_i in initial_state.item_l:
    for production in grammar:
        if kernel_i.production[kernel_i.dot] == production[0][0]:
            if (verify_if_reduction(kernel_i, kernel_i.dot)):
                item = create_new_item(production[0], "Closure", 3, True)
            else:
                item = create_new_item(production[0], "Closure", 3, False)
            if item not in initial_state.item_l:
                initial_state.item_l.append(item)
lr0_states.append(initial_state)

# ciclo for che per ogni simbolo dietro al dot crea transizioni verso nuovo stato
new_symb_transitions = [] # array che contiene i simboli con cui devo muovermi
for state in lr0_states:
    for item in state.item_l:
        if (not item.isReductionItem):
            if item.production[item.dot] not in new_symb_transitions:
                new_symb_transitions.append(item.production[item.dot])
    for element in new_symb_transitions:
        require_new_state = True
        destination_state = 0
        new_state_items = []
        for item in state.item_l:
            print(item.production, item.dot)
            if (item.production[item.dot] == element):
                new_item = create_new_item(item.production, item.dot+1, item.type, "Reduction" if verify_if_reduction(item, item.dot+1) else "Not-reduction")
                new_state_items.append(new_item)
                for state_n in lr0_states: #controllo che non esista un altro stato con lo stesso kernel con require_new_state
                    for item_n in state_n.item_l:
                        if (item_n.type == "Kernel"):
                            if (check_item_equality(item, item_n)):
                                require_new_state = False
                            else:
                                require_new_state = True
                    if (not require_new_state):
                        destination_state = state_n.name
                if (require_new_state):
                    new_state = create_new_state(state_counter)
                    state_counter += 1
                    lr0_states.append(new_state)
                    for new_state_item in new_state_items:
                        new_state.add_item(new_state_item)
                    new_transition = create_new_transition(transition_counter, element, state.name, new_state.name)
                    transitions.append(new_transition)
                    transition_counter += 1
                else:
                    new_transition = create_new_transition(transition_counter, element, state.name, destination_state)
                    transitions.append(new_transition)
                    transition_counter += 1


print("\nState " + str(initial_state.name) + ":")
for element in initial_state.item_l:
    print(element.production, str(element.dot), element.type, "Reduction" if element.isReductionItem else "Not-reduction")

# table Computation
header = []
for element in terminal_names:
    if element not in header:
        header.append(element)
for element in non_terminal_names:
    if element not in header:
        header.append(element)

ll1_table = PrettyTable(header)
total_lenght = len(non_terminal_names) + len(terminal_names)
table = [["" for x in range(total_lenght)] for y in range(10)] # 10 -> numero di stati

for idx_row in range(10):
    for idx_col in range(total_lenght):
        if (idx_col == 0):
            table[idx_row][idx_col] = idx_row
        else:
            table[idx_row][idx_col] = []

for i in range(10):
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
