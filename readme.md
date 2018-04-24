# Parsers in Python Project - by Amatori Matteo

Hello world!
My name is Amatori Matteo and this project was born after I successfully passed my exam of Formal Languages and Compilers in January 2018.
I cannot stop saying that this course was definitely the best of the whole Computer Science course.

For this reason I thought I could give myself a try with some challenges and proceed with the creation of the following parsers, written in Python.
Sadly, I know that Python is sub-optimal for stuff like this (C could have been much better, of course), but at the moment I am pretty confident with it, so here it is.

Finished development:  
LL(1)-parser

Current development:  
LR(0)-parser

Future development:  
SLR(0)-parser  
LR(1)-parser  
LALR(1)-parser

In order to correctly use the software you have to write the grammar you want to parse in the 'grammar.txt' file, following the format underneath.
If the right hand side of a production contains epsilon, write the character '#' instead of epsilon, the software reads it as it's epsilon.  

Example:  
S->AB  
A->a  
B->#  

# Usage:

LL(1)-parser:
```
> python3 ll1_parser.py
```
LR(0)-parser:
```
> python3 lr0_parser.py
```
SLR(0)-parser:
```
> python3 slr0_parser.py
```
LR(1)-parser:
```
> python3 lr1_parser.py
```
LALR(1)-parser:
```
> python3 lalr1_parser.py
```
