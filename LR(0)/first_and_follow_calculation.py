# This is an utility file that contains primitives to verify if an element
# is a terminal or a non-terminal, a primitive to identify a non-terminal
# in order to access its first and follow lists, and the two main functions
# that compute first and follow of a given non-terminal.
#
# Check readme.md for details.
#
# Author: Matteo Amatori

# functions declaration
def isTerminal(element):
    if (element == element.upper()):
        return False
    else:
        return True

def isNonTerminal(element):
    if (element == element.upper()):
        return True
    else:
        return False

def identify_non_T(non_terminals, nT):
    for non_terminal in non_terminals:
        if non_terminal.name == nT:
            ret_nT = non_terminal
    return ret_nT

def compute_first(driver, production, my_non_terminals, p_prog):
    if (driver.name == production[0][0]):
        #print("Analyzing '" + production[0] + "' in the computation of first(" + driver.name + ").")
        if (isTerminal(production[0][p_prog])):
            if production[0][p_prog] not in driver.first_l:
                driver.add_first(production[0][p_prog])
                #print("Adding '" + production[0][p_prog] + "' to first(" + driver.name + ").")
            #else:
                #print("'" + production[0][p_prog] + "' already in first(" + driver.name + ").")

        elif (production[0][p_prog] == '#' and p_prog == len(production[0])-1):
            if '#' not in driver.first_l:
                driver.add_first('#')
                #print("Adding epsilon to first(" + driver.name + ").")

        elif (isNonTerminal(production[0][p_prog])):
            for element in my_non_terminals:
                if element.name == production[0][p_prog]:
                    nT = element
                    for first_nT in nT.first_l:
                        if (first_nT != '#'):
                            if first_nT not in driver.first_l:
                                driver.add_first(first_nT)
                                #print("Adding '" + first_nT + "' to first(" + driver.name + ").")
                            #else:
                                #print("'" + first_nT + "' already in first(" + driver.name + ").")
                        else:
                            if (p_prog == len(production[0])-1):
                                if "#" not in driver.first_l:
                                    driver.add_first("#")
                                    #print("Adding epsilon to first(" + driver.name + ").")
                            else:
                                if (p_prog < len(production[0])-1):
                                    #print("Calling again")
                                    compute_first(driver, production, my_non_terminals, p_prog+1)


def compute_follow(nT, production, my_non_terminals, p_prog):
    if nT.isStartSymbol:
        if '$' not in nT.follow_l:
            nT.add_follow('$')

    #print("Analyzing the production '" + production[0] + "' in the computation of follow(" + nT.name + ")..")

    if (len(production[0]) > 4 and p_prog < len(production[0])-1):
        for elem in range(p_prog, len(production[0])):
            if (isNonTerminal(production[0][elem])): # primo elemento della right-hand side è non-terminale
                nT = identify_non_T(my_non_terminals, production[0][elem])
                if (elem < len(production[0])-1):
                    if (isTerminal(production[0][elem+1])):
                        if production[0][elem+1] not in nT.follow_l:
                            nT.add_follow(production[0][elem+1])
                            #print("Adding '" + production[0][elem+1] + "' to follow(" + nT.name + ") due to rule 2.")
                    else:
                        non_T_ahead = identify_non_T(my_non_terminals, production[0][elem+1])
                        for first_to_add in non_T_ahead.first_l:
                            if (first_to_add != "#"):
                                if first_to_add not in nT.follow_l:
                                    nT.add_follow(first_to_add)
                                    #print("Adding '" + first_to_add + "' to follow(" + nT.name + ") due to rule 3")
                            else:
                                while (p_prog < len(production[0])-1):
                                    if (isTerminal(production[0][p_prog+2])):
                                        if production[0][p_prog+2] not in nT.follow_l:
                                            nT.add_follow(production[0][p_prog+2])
                                            #print("Adding '" + production[0][elem+1] + "' to follow(" + nT.name + ") due to rule 3.")
                                    else:
                                        for non_T_ahead2 in my_non_terminals:
                                            if non_T_ahead2.name == production[0][p_prog+2]:
                                                for first_to_add2 in non_T_ahead2.first_l:
                                                    if (first_to_add2 != '#'):
                                                        if first_to_add2 not in nT.follow_l:
                                                            nT.add_follow(first_to_add2)
                                                            #print("Adding '" + first_to_add2 + "' to follow(" + nT.name + ") due to rule 3")
                                    p_prog += 1
                else:
                    for element in my_non_terminals: # trovo il non-terminale nella right-hand side
                        if (element.name == production[0][-1]):
                            for driver in my_non_terminals: # trovo il driver
                                if (driver.name == production[0][0]):
                                    for follow_d in driver.follow_l:
                                        if follow_d not in element.follow_l:
                                            element.add_follow(follow_d)
                                            #print("Adding '" + follow_d + "' to follow(" + production[0][-1] + ").")
            else: # primo elemento della right-hand side è terminale
                #print("Recurring cuz i saw " + production[0][elem] + " in position " + str(elem-3))
                compute_follow(nT, production, my_non_terminals, p_prog+1)
    else:
        if (isNonTerminal(production[0][p_prog])):
            for element in my_non_terminals: # trovo il non-terminale nella right-hand side
                if (element.name == production[0][-1]):
                    for driver in my_non_terminals: # trovo il driver
                        if (driver.name == production[0][0]):
                            for follow_d in driver.follow_l:
                                if follow_d not in element.follow_l:
                                    element.add_follow(follow_d)
                                    #print("Adding '" + follow_d + "' to follow(" + production[0][-1] + ") due to rule 1.")

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
