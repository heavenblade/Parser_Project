# This is a utility file that contains primitives to verify if an element
# is a terminal or a non-terminal, a primitive to identify a non-terminal
# in order to access its first and follow lists, and the two main functions
# that compute first and follow of a given non-terminal.
#
# Check readme.md for details.
#
# Author: Matteo Amatori

# functions declaration
def isTerminal(element):
    isSymbol = False
    if (element == "(" or element == ")" or element == "*" or element == "+" or element == "." or element == "-" or element == "[" or element == "]" or element == "<" or element == ">" or element == "=" or element == "^" or element == "{" or element == "}" or element == "|"):
        isSymbol = True
    if (element == element.upper() and not isSymbol):
        return False
    elif (element == element.lower() or isSymbol):
        return True

def isNonTerminal(element):
    isSymbol = False
    if (element == "(" or element == ")" or element == "*" or element == "+" or element == "." or element == "-" or element == "[" or element == "]" or element == "<" or element == ">" or element == "=" or element == "^" or element == "{" or element == "}" or element == "|"):
        isSymbol = True
    if (element == element.upper() and not isSymbol):
        return True
    elif (element == element.lower() or isSymbol):
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
    if (nT.isStartSymbol):
        if ('$' not in nT.follow_l):
            nT.add_follow('$')

    #print("Analyzing the production '" + production[0] + "' in the computation of follow(" + nT.name + ")..")

    if (production[0][-1] == nT.name):
        for non_T in my_non_terminals:
            if (production[0][0] == non_T.name):
                for follow_d in non_T.follow_l:
                    if (follow_d not in nT.follow_l):
                        nT.follow_l.append(follow_d)
                        #print("Adding '" + follow_d + "' to follow(" + production[0][-1] + ") due to rule 1.")

    if (nT.name == production[0][p_prog]):
        stopped = False
        if (len(production[0]) > 4 and p_prog < len(production[0])-1):
            if (isNonTerminal(production[0][p_prog])):
                if (isTerminal(production[0][p_prog+1])):
                    if (production[0][p_prog+1] not in nT.follow_l):
                        nT.add_follow(production[0][p_prog+1])
                        #print("Adding '" + production[0][p_prog+1] + "' to follow(" + nT.name + ") due to rule 2.")
                        compute_follow(nT, production, my_non_terminals, p_prog+1)
                else:
                    while (p_prog < len(production[0])-1 and not stopped):
                        if (isTerminal(production[0][p_prog+1])):
                            if (production[0][p_prog+1] not in nT.follow_l):
                                nT.add_follow(production[0][p_prog+1])
                            stopped = True
                        else:
                            for non_T_ahead in my_non_terminals:
                                if (non_T_ahead.name == production[0][p_prog+1]):
                                    if ("#" in non_T_ahead.first_l):
                                        for first_to_add in non_T_ahead.first_l:
                                            if (first_to_add != "#"):
                                                if (first_to_add not in nT.follow_l):
                                                    nT.add_follow(first_to_add)
                                                    #print("Adding '" + first_to_add + "' to follow(" + nT.name + ") due to rule 3.1")
                                        if (p_prog+1 == len(production[0])-1):
                                            for driver_non_T in my_non_terminals:
                                                if (driver_non_T.name == production[0][0]):
                                                    for follow_driver in driver_non_T.follow_l:
                                                        if (follow_driver not in nT.follow_l):
                                                            nT.add_follow(follow_driver)
                                                            #print("Adding '" + follow_driver + "' to follow(" + nT.name + ") due to rule 4")
                                            stopped = True
                                        if (p_prog+2 <= len(production[0])-1):
                                            p_prog += 1
                                    else:
                                        for first_to_add in non_T_ahead.first_l:
                                            if (first_to_add not in nT.follow_l):
                                                nT.add_follow(first_to_add)
                                                #print("Adding '" + first_to_add + "' to follow(" + nT.name + ") due to rule 3.2")
                                        stopped = True
                                        break
        else:
            if (isNonTerminal(production[0][p_prog])):
                for element in my_non_terminals:
                    if (element.name == production[0][-1]):
                        for driver in my_non_terminals:
                            if (driver.name == production[0][0]):
                                for follow_d in driver.follow_l:
                                    if follow_d not in element.follow_l:
                                        element.add_follow(follow_d)
                                        #print("Adding '" + follow_d + "' to follow(" + production[0][-1] + ") due to rule 1.")
    else:
        if (p_prog < len(production[0])-1):
            compute_follow(nT, production, my_non_terminals, p_prog+1)

def verify_grammar(table, rows, columns):
    found_mult_def = False
    for row in range(rows):
        for column in range(columns):
            if (column != 0):
                if (len(table[row][column]) > 1):
                    #print(table[row][column])
                    found_mult_def = True
    return found_mult_def
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
