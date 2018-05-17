# This is a LALR(1) parser for grammars. This version is based on the LR(1)-automaton
# states merging. If the states share the same LR(0)-items they get merged in a
# unique state with the lookaheads merged together. The future implementation will be
# based on the recursive equatios algorithm invented by Paola Quaglia. The process
# follows the base LR(0)-automaton construction, while at the same time keeping track
# of a set of recursive equations containing the lookaheads. At the end of the
# LR(0)-automaton computation, the recursive equations get solved and the resulting
# automaton is a LALR(1)-automaton as it was created through LR(1)-automaton state
# merging.
#
# Check readme.txt in order to see input format of the grammar and eventual
# output format.
#
# Author: Matteo Amatori

import csv
import numpy
import sys
import first_and_follow_calculation as ffc
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
class lr0Item:
    production = []
    type = ""
    dot = 0
    isReduceItem = False

    def __init__ (self, production, type, dot, reduct):
        self.production = production
        self.type = type
        self.dot = dot
        self.isReduceItem = reduct

    def __eq__ (self, other):
        if (self.production == other.production and self.type == other.type and self.dot == other.dot and self.isReduceItem == other.isReduceItem):
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.production, self.type, self.dot, self.isReduceItem))

def create_new_lr0_item (production, type, dot, reduct):
    new_state = lr0Item(production, type, dot, reduct)
    return new_state
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

def create_new_item (production, dot, type, reduct):
    new_state = lr1Item(production, dot, type, reduct)
    return new_state

def set_lookaheads (item, lookahead_l):
    item.lookAhead = lookahead_l

def print_item(item):
    print(item.production, item.lookAhead, item.dot, item.type, item.isReduceItem)
#------------------------------------------------------------------------------
class lr1State:
    name = 0
    item_l = []
    isInitialState = False
    gotMerged = False

    def __init__ (self, state_count):
        self.name = state_count
        self.item_l = []
        self.isInitialState = False
        self.gotMerged = False

    def add_item (self, item):
        self.item_l.append(item)

def create_new_state (name):
    new_state = lr1State(name)
    return new_state

def check_kernel_equality(new_kernel, state_n):
    state_n_ker = []
    for item in state_n.item_l:
        if (item.type == "Kernel"):
            state_n_ker.append(item)
    if (set(new_kernel) == set(state_n_ker)):
        return True
    else:
        return False

def check_states_equality_for_merge(set_1, set_2):
    if (set(set_1) == set(set_2)):
        return True
    else:
        return False

def apply_closure(state, my_item):
    if (my_item.isReduceItem == "Not-Reduce"):
        if (ffc.isNonTerminal(my_item.production[my_item.dot])):
            for production in grammar:
                if (production[0][0] == my_item.production[my_item.dot]):
                    temp_lookAhead_l = []
                    if (my_item.dot == len(my_item.production)-1):
                        for element in my_item.lookAhead:
                            temp_lookAhead_l.append(element)
                    else:
                        p_prog = my_item.dot
                        while (p_prog+1 <= len(my_item.production)-1):
                            if (ffc.isTerminal(my_item.production[p_prog+1])):
                                if (my_item.production[p_prog+1] not in temp_lookAhead_l):
                                    temp_lookAhead_l.append(my_item.production[p_prog+1])
                            else:
                                for nT in non_terminals:
                                    if (nT.name == my_item.production[p_prog+1]):
                                        for first_nT in nT.first_l:
                                            if (first_nT != "#"):
                                                if (first_nT not in temp_lookAhead_l):
                                                    temp_lookAhead_l.append(first_nT)
                                            else:
                                                if (p_prog+1 == len(my_item.production)-1):
                                                    for item_clos_LA in my_item.lookAhead:
                                                        if (item_clos_LA not in temp_lookAhead_l):
                                                            temp_lookAhead_l.append(item_clos_LA)
                            p_prog += 1
                    if (production[0][3] == "#"):
                        new_item = create_new_item(production[0], 3, "Closure", "Reduce")
                        set_lookaheads(new_item, temp_lookAhead_l)
                    else:
                        new_item = create_new_item(production[0], 3, "Closure", "Not-Reduce")
                        set_lookaheads(new_item, temp_lookAhead_l)
                    if (new_item not in state.item_l):
                        state.item_l.append(new_item)
                    if (ffc.isNonTerminal(new_item.production[new_item.dot])):
                        apply_closure(state, new_item)
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
lr1_states = []                                         # array that will contain the LR(1)-automaton
lr1_transitions = []                                    # array of transitions between the LR(1)-automaton states
lr1_state_counter = 0
lr1_transition_counter = 0
lalr1_states = []                                       # array that will contain the LALR(1)-automaton
lalr1_transitions = []                                  # array of transitions between the LALR(1)-automaton states
lalr1_state_counter = 0
lalr1_transition_counter = 0

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

# computation of the LR(1)-automaton
print("---------------------- LR(0)-automa Computation ----------------------")
# starting state
initial_state = create_new_state(lr1_state_counter)
lr1_state_counter += 1
initial_state.isInitialState = True
s_item = create_new_item(a_grammar[0], 3, "Kernel", "Not-Reduce")
set_lookaheads(s_item, ['$'])
initial_state.add_item(s_item)
apply_closure(initial_state, s_item)
lr1_states.append(initial_state)

# rest of automaton computation
for state in lr1_states:
    for i in range(3): # temporary solution to recursive closure applications
        for clos_item in state.item_l:
            apply_closure(state, clos_item)
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
            if (item.production[item.dot] == element):
                new_item = create_new_item(item.production, item.dot+1, "Kernel", "Reduce" if (item.dot+1 == len(item.production)) else "Not-Reduce")
                set_lookaheads(new_item, item.lookAhead)
                new_state_items.append(new_item)
        for state_n in lr1_states:
                if (check_kernel_equality(new_state_items, state_n)):
                    require_new_state = False
                    destination_state = state_n.name
                    break
                else:
                    require_new_state = True
        if (require_new_state):
            new_state = create_new_state(lr1_state_counter)
            lr1_state_counter += 1
            lr1_states.append(new_state)
            for new_state_item in new_state_items:
                if (new_state_item not in new_state.item_l):
                    new_state.add_item(new_state_item)
                apply_closure(new_state, new_state_item)
            new_transition = create_new_transition(lr1_transition_counter, element, state.name, new_state.name)
            lr1_transition_counter += 1
            if (new_transition not in lr1_transitions):
                lr1_transitions.append(new_transition)
        else:
            new_transition = create_new_transition(lr1_transition_counter, element, state.name, destination_state)
            lr1_transition_counter += 1
            if (new_transition not in lr1_transitions):
                lr1_transitions.append(new_transition)

# merging of the states that share the same LR(0)-items with different lookaheads using the lookahead merging technique
check_merge_matrix = numpy.zeros(shape = (lr1_state_counter, lr1_state_counter))
new_lalr1_states = []
for i in range(lr1_state_counter):
    for j in range(lr1_state_counter):
        if (i == j):
            check_merge_matrix[i][j] = 1
for state in lr1_states:
    for state_check in lr1_states:
        equal = False
        if (check_merge_matrix[state.name][state_check.name] != 1 and check_merge_matrix[state_check.name][state.name] != 1):
            first_item_l = []
            second_item_l = []
            for lr1_item in state.item_l:
                new_tmp_lr0_item = create_new_lr0_item (lr1_item.production, lr1_item.dot, lr1_item.type, lr1_item.isReduceItem)
                first_item_l.append(new_tmp_lr0_item)
            for lr1_item in state_check.item_l:
                new_tmp_lr0_item = create_new_lr0_item (lr1_item.production, lr1_item.dot, lr1_item.type, lr1_item.isReduceItem)
                second_item_l.append(new_tmp_lr0_item)
            if (check_states_equality_for_merge(first_item_l, second_item_l)):
                equal = True
                state_1 = state
                state_2 = state_check
            else:
                equal = False
            if (equal):
                new_name = str(state.name)+str(state_check.name)
                new_state = create_new_state(new_name)
                print("\nmerging "+str(state.name)+" and "+str(state_check.name))
                for item_1 in state_1.item_l:
                    temp_lookaheads = []
                    for item_2 in state_2.item_l:
                        if (item_1.production == item_2.production and item_1.dot == item_2.dot and item_1.type == item_2.type and item_1.isReduceItem == item_2.isReduceItem):
                            print_item(item_1)
                            print_item(item_2)
                            for LA_1 in item_1.lookAhead:
                                temp_lookaheads.append(LA_1)
                            for LA_2 in item_2.lookAhead:
                                if (LA_2 not in item_1.lookAhead):
                                    print("adding "+LA_2+" to "+item_1.production)
                                    temp_lookaheads.append(LA_2)
                    new_item = create_new_item(item_1.production, item_1.dot, item_1.type, item_1.isReduceItem)
                    set_lookaheads(new_item, temp_lookaheads)
                    new_state.add_item(new_item)
                check_merge_matrix[state.name][state_check.name] = 1
                check_merge_matrix[state_check.name][state.name] = 1
                state.gotMerged = True
                state_check.gotMerged = True
                new_lalr1_states.append(new_state)
for state in lr1_states:
    if (not state.gotMerged):
        lalr1_states.append(state)
        lalr1_state_counter += 1
    else:
        for new_state in new_lalr1_states:
            if (str(state.name) in str(new_state.name) and new_state not in lalr1_states):
                lalr1_states.append(new_state)
                lalr1_state_counter += 1

print("\nLR(1)-states:")
for state in lr1_states:
    print("\nState " + str(state.name) + ":")
    for element in state.item_l:
        print(element.production + ",", element.lookAhead, ", " + str(element.dot) + ", " + element.type + ", " + element.isReduceItem)
print("\nLALR(1)-states:")
for state in lalr1_states:
    print("\nState " + str(state.name) + ":")
    for element in state.item_l:
        print(element.production + ",", element.lookAhead, ", " + str(element.dot) + ", " + element.type + ", " + element.isReduceItem)
for transition in lr1_transitions:
    print("\nTransition " + str(transition.name) + ":")
    print(transition.name,  transition.element, transition.starting_state, transition.ending_state)

# table Computation
header = []
for element in terminal_names:
    if element not in header:
        header.append(element)
for element in non_terminal_names:
    if element not in header:
        header.append(element)

lalr1_table = PrettyTable(header)
total_lenght = len(non_terminal_names) + len(terminal_names)
table = [["" for x in range(total_lenght)] for y in range(lalr1_state_counter)] #TBM

# LALR(1)-parsing table computation
for idx_row in range(lalr1_state_counter): #TBM
    for idx_col in range(total_lenght):
        if (idx_col == 0):
            table[idx_row][idx_col] = lalr1_states[idx_row].name
        else:
            table[idx_row][idx_col] = []

for idx, element in enumerate(header):
    if (element == "$"):
        table[1][idx].append("Accept")
for transition in lr1_transitions:
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
for state_idx, state in enumerate(lalr1_states):
    for item in state.item_l:
        if (item.production != "Q->S"):
            new_entry = ""
            if (item.isReduceItem == "Reduce"):
                for idx1, production in enumerate(grammar):
                    if (item.production == production[0]):
                        new_entry = "R" + str(idx1+1)
                for idx2, element in enumerate(header):
                    for LA in item.lookAhead:
                        if (element == LA):
                            table[state_idx][idx2].append(new_entry)

for i in range(lalr1_state_counter): #TBM
    lalr1_table.add_row(table[i])

print("\nLALR(1) parsing table of the grammar G:")
print(lalr1_table)

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
