# LALR(1) parser for grammars. This implementation is be based on the symbolic
# lookaheads for bottom-up parsing algorithm invented by Paola Quaglia. The process
# follows the base LR(0)-automaton construction, while at the same time keeping track
# of a set of recursive equations containing the lookaheads. At the end of the
# LR(0)-automaton computation, the recursive equations get solved, the lookahead lists
# get populated and the resulting automaton is a LALR(1)-automaton as it was created
# through LR(1)-automaton state merging.
# Check readme.txt in order to see input format of the grammar and eventual
# output format.
#
# Author: Matteo Amatori

import csv
import numpy
import sys
from utils import first_and_follow_calculation as ffc
from prettytable import PrettyTable
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
class recursiveEquation:
    name = ""
    symbol_list = []
    solved = False

    def __init__ (self, name):
        self.name = name
        self.symbol_list = []
        self.solved = False

    def __str__ (self):
        return str(self.name)

def create_new_rec_equation (rec_equations_counter):
    rec_eq_name = "x"+str(rec_equations_counter)
    new_equation = recursiveEquation(rec_eq_name)
    return new_equation

def add_symbol (self, element):
    self.symbol_list.append(element)
#------------------------------------------------------------------------------
class lr0Item:
    production = []
    type = ""
    dot = 0
    isReduceItem = False
    set_of_rec_equations = []

    def __init__ (self, production, dot, type, reduct):
        self.production = production
        self.dot = dot
        self.type = type
        self.isReduceItem = reduct
        self.set_of_rec_equations = []

    def __eq__ (self, other):
        if (self.production == other.production and self.type == other.type and self.dot == other.dot and self.isReduceItem == other.isReduceItem):
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.production, self.type, self.dot, self.isReduceItem))

def create_new_lr0_item (production, dot, type, reduct):
    new_item = lr0Item(production, dot, type, reduct)
    return new_item

def print_item (item):
    print(item.production, item.type, item.dot, item.isReduceItem)

def add_rec_equation (item, rec_eq):
    item.set_of_rec_equations.append(rec_eq)
#------------------------------------------------------------------------------
class lr1Item:
    production = []
    lookAhead = []
    dot = 0
    type = ""
    isReduceItem = False

    def __init__ (self, production, dot, type, reduct):
        self.production = production
        self.lookAhead = []
        self.dot = dot
        self.type = type
        self.isReduceItem = reduct

    def __eq__ (self, other):
        equal = False
        lookaheads = []
        if (self.production == other.production and self.dot == other.dot and self.type == other.type and self.isReduceItem == other.isReduceItem):
            for element in self.lookAhead:
                if (element not in lookaheads):
                    lookaheads.append(element)
            for element in other.lookAhead:
                if (element not in lookaheads):
                    lookaheads.append(element)
            for LA in lookaheads:
                if (LA in self.lookAhead):
                    if (LA in other.lookAhead):
                        equal = True
                    else:
                        equal = False
                        break
                else:
                    equal = False
                    break
        else:
            equal = False
        if (equal):
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.production, self.dot, self.type, self.isReduceItem))

def create_new_lr1_item (production, dot, type, reduct):
    new_item = lr1Item(production, dot, type, reduct)
    return new_item

def set_lookaheads (item, lookahead_l):
    item.lookAhead = lookahead_l
#------------------------------------------------------------------------------
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

def check_kernel_equality (new_kernel, state_n):
    state_n_ker = []
    for item in state_n.item_l:
        if (item.type == "Kernel"):
            state_n_ker.append(item)
    if (set(new_kernel) == set(state_n_ker)):
        return True
    else:
        return False

def apply_closure (state, my_item, recursion, rec_equations_counter):
    if (my_item.isReduceItem == "Not-Reduce"):
        if (ffc.isNonTerminal(my_item.production[my_item.dot])):
            for production in grammar:
                if (production[0][0] == my_item.production[my_item.dot]):
                    temp_lookAhead_l = []
                    if (my_item.dot == len(my_item.production)-1):
                        for element in my_item.set_of_rec_equations:
                            if (element not in temp_lookAhead_l):
                                temp_lookAhead_l.append(element)
                    else:
                        p_prog = my_item.dot
                        stopped = False
                        while (p_prog+1 <= len(my_item.production)-1 and not stopped):
                            if (ffc.isTerminal(my_item.production[p_prog+1])):
                                if (my_item.production[p_prog+1] not in temp_lookAhead_l):
                                    temp_lookAhead_l.append(my_item.production[p_prog+1])
                                    stopped = True
                            else:
                                for nT in non_terminals:
                                    if (nT.name == my_item.production[p_prog+1]):
                                        for first_nT in nT.first_l:
                                            if (first_nT != "#"):
                                                if (first_nT not in temp_lookAhead_l):
                                                    temp_lookAhead_l.append(first_nT)
                                            else:
                                                if (p_prog+1 == len(my_item.production)-1):
                                                    for item_clos_rec_eq in my_item.set_of_rec_equations:
                                                        if (item_clos_rec_eq not in temp_lookAhead_l):
                                                            temp_lookAhead_l.append(item_clos_rec_eq)
                            p_prog += 1
                    temp_type = ""
                    if (production[0][3] == "#"):
                        new_temp_item = create_new_lr0_item(production[0], 3, "Closure", "Reduce")
                        temp_type = "Reduce"
                    else:
                        new_temp_item = create_new_lr0_item(production[0], 3, "Closure", "Not-Reduce")
                        temp_type = "Not-Reduce"
                    found = False
                    for item_for_la_merge in state.item_l:
                        tmp_item = create_new_lr0_item(item_for_la_merge.production, item_for_la_merge.dot, item_for_la_merge.type, item_for_la_merge.isReduceItem)
                        if (tmp_item == new_temp_item):
                            for la_to_merge in temp_lookAhead_l:
                                if (la_to_merge not in item_for_la_merge.set_of_rec_equations[0].symbol_list):
                                    item_for_la_merge.set_of_rec_equations[0].symbol_list.append(la_to_merge)
                            found = True
                    if (not found):
                        new_item = create_new_lr0_item(production[0], 3, "Closure", temp_type)
                        new_item_rec_eq = create_new_rec_equation(rec_equations_counter)
                        rec_equations_counter += 1
                        for symb_to_add in temp_lookAhead_l:
                            if (symb_to_add not in new_item_rec_eq.symbol_list):
                                new_item_rec_eq.symbol_list.append(symb_to_add)
                        add_rec_equation(new_item, new_item_rec_eq)
                        rec_equations.append(new_item_rec_eq)
                        rec_eq_already_in_array = False
                        for rec_eq in rec_equations:
                            if (rec_eq.name == new_item_rec_eq.name):
                                rec_eq_already_in_array = True
                        if (not rec_eq_already_in_array):
                            rec_equations.append(new_item_rec_eq)
                        if (new_item not in state.item_l):
                            state.item_l.append(new_item)
                            #print("Adding " + new_item.production + " to state " + str(state.name))
                            if (recursion < 2):
                                if (ffc.isNonTerminal(new_item.production[new_item.dot])):
                                    #print("recurring for " + new_item.production, recursion)
                                    apply_closure(state, new_item, recursion+1, rec_equations_counter)
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# variables declaration section
terminal_names = []                                     # strings of terminals
non_terminal_names = []                                 # just strings
non_terminals = []                                      # actual non-terminals
lr0_states = []                                         # array of LR(0)-states
transitions = []                                        # array of transitions between LR(0)-states
rec_equations = []
state_counter = 0
transition_counter = 0
rec_equations_counter = 0


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

# collecting terminals
terminal_names.append(" ")
for production in grammar:
    for index in range(len(production[0])):
        if (production[0][index] != '#' and index >= 3):
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

# computation of the LR(0)-automaton
print("-------------------- LR(0)-automaton Computation ---------------------")
# starting state
initial_state = create_new_state(state_counter)
state_counter += 1
initial_state.isInitialState = True
s_item = create_new_lr0_item(a_grammar[0], 3, "Kernel", "Not-Reduce")
initial_lookahead = create_new_rec_equation(rec_equations_counter)
rec_equations_counter += 1
initial_lookahead.symbol_list.append("$")
add_rec_equation(s_item, initial_lookahead)
rec_equations.append(initial_lookahead)
initial_state.add_item(s_item)
apply_closure(initial_state, s_item, 0, rec_equations_counter)
lr0_states.append(initial_state)
'''
######## solution for solving recursive equations #########
another_rec_eq_1 = create_new_rec_equation(rec_equations_counter)
another_rec_eq_1.symbol_list.append("$")
temp_list = ["a", "b"]
print(another_rec_eq_1, another_rec_eq_1.symbol_list)
another_rec_eq_2 = create_new_rec_equation(rec_equations_counter)
for elem in temp_list:
    another_rec_eq_2.symbol_list.append(elem)
another_rec_eq_1.symbol_list.append(another_rec_eq_2)
print(another_rec_eq_1, another_rec_eq_1.symbol_list)

for element in another_rec_eq_1.symbol_list:
    if (not isinstance(element, str)):
        another_rec_eq_1.symbol_list.remove(element)
        for symbol in element.symbol_list:
            if (symbol not in another_rec_eq_1.symbol_list):
                another_rec_eq_1.symbol_list.append(symbol)

print(another_rec_eq_1, another_rec_eq_1.symbol_list, "\n")
#############################################################
'''
# rest of automaton computation
for state in lr0_states:
    for i in range(3): # temporary solution to recursive closure applications
        for clos_item in state.item_l:
            apply_closure(state, clos_item, 0, rec_equations_counter)
    new_symb_transitions = []
    for item in state.item_l:
        if (item.isReduceItem == "Not-Reduce"):
            if (item.production[item.dot] not in new_symb_transitions):
                new_symb_transitions.append(item.production[item.dot])

    for element in new_symb_transitions:
        require_new_state = False
        destination_state = 0
        new_state_items = []
        for item in state.item_l:
            if (item.isReduceItem != "Reduce"):
                if (item.production[item.dot] == element):
                    new_item = create_new_lr0_item(item.production, item.dot+1, "Kernel", "Reduce" if (item.dot+1 == len(item.production)) else "Not-Reduce")
                    add_rec_equation(new_item, item.set_of_rec_equations[0])
                    new_state_items.append(new_item)
        for state_n in lr0_states:
                if (check_kernel_equality(new_state_items, state_n)):
                    require_new_state = False
                    destination_state = state_n.name
                    break
                else:
                    require_new_state = True
        if (require_new_state):
            new_state = create_new_state(state_counter)
            state_counter += 1
            lr0_states.append(new_state)
            for new_state_item in new_state_items:
                if (new_state_item not in new_state.item_l):
                    new_state.add_item(new_state_item)
                apply_closure(new_state, new_state_item, 0, rec_equations_counter)
            new_transition = create_new_transition(transition_counter, element, state.name, new_state.name)
            transition_counter += 1
            if (new_transition not in transitions):
                transitions.append(new_transition)
        else:
            new_transition = create_new_transition(transition_counter, element, state.name, destination_state)
            transition_counter += 1
            if (new_transition not in transitions):
                transitions.append(new_transition)

print(rec_equations)
print("\n")
for rec_eq in rec_equations:
    print(rec_eq.name)
    print(rec_eq.symbol_list)
    print(rec_eq.solved)

finished_solving = False
i = 0
while (not finished_solving):
    print(i)
    for rec_eq in rec_equations:
        for element in rec_eq.symbol_list:
            if (not isinstance(element, str)):
                rec_eq.symbol_list.remove(element)
                #print("Removing " + element.name + " from " + rec_eq.name + " and adding ", element.symbol_list)
                for symbol in element.symbol_list:
                    if (symbol not in rec_eq.symbol_list):
                        rec_eq.symbol_list.append(symbol)
            else:
                rec_eq.solved = True
    if (all(rec_eq.solved for rec_eq in rec_equations)):
        finished_solving = True
    else:
        finished_solving = False
    i += 1
print("\n")
for rec_eq in rec_equations:
    print(rec_eq.name)
    print(rec_eq.symbol_list)
    print(rec_eq.solved)

print("LALR(1)-states:")
for state in lr0_states:
    print("\nState " + str(state.name) + ":")
    for element in state.item_l:
        print(element.production + ", Dot is on " + str(element.dot) + ", " + element.type + ", " + element.isReduceItem + ",", element.set_of_rec_equations[0].symbol_list)
print("\nLALR(1)-transitions:")
for transition in transitions:
    print(transition.name, transition.element, transition.starting_state, transition.ending_state)

# table creation
header = []
for element in terminal_names:
    if element not in header:
        header.append(element)
for element in non_terminal_names:
    if element not in header:
        header.append(element)

lr0_table = PrettyTable(header)
total_lenght = len(non_terminal_names) + len(terminal_names)
table = [["" for x in range(total_lenght)] for y in range(state_counter)]

# LALR(1)-parsing table computation
for idx_row in range(state_counter):
    for idx_col in range(total_lenght):
        if (idx_col == 0):
            table[idx_row][idx_col] = idx_row
        else:
            table[idx_row][idx_col] = []

for idx, element in enumerate(header):
    if (element == "$"):
        table[1][idx].append("Accept")
for transition in transitions:
    new_entry = ""
    if (ffc.isNonTerminal(transition.element)):
        new_entry = "Goto " + str(transition.ending_state)
        for idx, element in enumerate(header):
            if (element == transition.element):
                table[transition.starting_state][idx].append(new_entry)
    elif (ffc.isTerminal(transition.element)):
        new_entry = "S" + str(transition.ending_state)
        for idx, element in enumerate(header):
            if (element == transition.element):
                table[transition.starting_state][idx].append(new_entry)
for state in lr0_states:
    for item in state.item_l:
        if ("Q->" not in item.production):
            new_entry = ""
            if (item.isReduceItem == "Reduce"):
                for idx1, production in enumerate(grammar):
                    if (item.production == production[0]):
                        new_entry = "R" + str(idx1+1)
                for idx2, element in enumerate(header):
                    if (ffc.isTerminal(element) or element == "$"):
                        if (len(new_entry) > 0):
                            table[state.name][idx2].append(new_entry)

for i in range(state_counter):
    lr0_table.add_row(table[i])

print("\nLALR(1) parsing table of the grammar G:")
print(lr0_table)

if (ffc.verify_grammar(table, state_counter, total_lenght)):
    print("\nThe grammar G is not LALR(1).")
else:
    print("\nThe grammar G is LALR(1).")

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
