''' Robert Ramsay 2011 Google Code Jam
Introduction

Magicka is an action-adventure game developed by Arrowhead Game Studios. In 
Magicka you play a wizard, invoking and combining elements to create Magicks. 
This problem has a similar idea, but it does not assume that you have played 
Magicka.

Note: "invoke" means "call on." For this problem, it is a technical term and 
you don't need to know its normal English meaning.

Problem

As a wizard, you can invoke eight elements, which are the "base" elements. Each 
base element is a single character from {Q, W, E, R, A, S, D, F}. When you 
invoke an element, it gets appended to your element list. For example: if you 
invoke W and then invoke A, (we'll call that "invoking WA" for short) then your 
element list will be [W, A].

We will specify pairs of base elements that combine to form non-base elements 
(the other 18 capital letters). For example, Q and F might combine to form T. 
If the two elements from a pair appear at the end of the element list, then 
both elements of the pair will be immediately removed, and they will be 
replaced by the element they form. In the example above, if the element list 
looks like [A, Q, F] or [A, F, Q] at any point, it will become [A, T].

We will specify pairs of base elements that are opposed to each other. After 
you invoke an element, if it isn't immediately combined to form another 
element, and it is opposed to something in your element list, then your 
element list will be cleared.

For example, suppose Q and F combine to make T. R and F are opposed to each 
other. Then invoking the following things (in order, from left to right) will 
have the following results:

QF -> [T] (Q and F combine to form T)
QEF -> [Q, E, F] (Q and F can't combine because they were never at the end of 
    the element list together)
RFE -> [E] (F and R are opposed, so the list is cleared; then E is invoked)
REF -> [] (F and R are opposed, so the list is cleared)
RQF -> [R, T] (QF combine to make T, so the list is not cleared)
RFQ -> [Q] (F and R are opposed, so the list is cleared)
Given a list of elements to invoke, what will be in the element list when 
you're done?

Input

The first line of the input gives the number of test cases, T. T test cases 
follow. Each test case consists of a single line, containing the following 
space-separated elements in order:

First an integer C, followed by C strings, each containing three characters: 
two base elements followed by a non-base element. This indicates that the two 
base elements combine to form the non-base element. Next will come an integer 
D, followed by D strings, each containing two characters: two base elements 
that are opposed to each other. Finally there will be an integer N, followed by 
a single string containing N characters: the series of base elements you are to 
invoke. You will invoke them in the order they appear in the string (leftmost 
character first, and so on).

Output

For each test case, output one line containing "Case #x: y", where x is the 
case number (starting from 1) and y is a list in the format "[e0, e1, ...]" 
where ei is the ith element of the final element list. Please see the sample 
output for examples.

Limits

1 <= T <= 100.
Each pair of base elements may only appear together in one combination, though 
they may appear in a combination and also be opposed to each other.
No base element may be opposed to itself.
Unlike in the computer game Magicka, there is no limit to the length of the 
element list.

Small dataset

0 <= C <= 1.
0 <= D <= 1.
1 <= N <= 10.
Large dataset

0 <= C <= 36.
0 <= D <= 28.
1 <= N <= 100.

Sample

Input 

5
0 0 2 EA
1 QRI 0 4 RRQR
1 QFT 1 QF 7 FAQFDFQ
1 EEZ 1 QE 7 QEEEERA
0 1 QW 2 QW 	

Output 

Case #1: [E, A]
Case #2: [R, I, R]
Case #3: [F, D, T]
Case #4: [Z, E, R, A]
Case #5: []
'''

def invoke(combos, opposed, spell):
    l = 0
    element_list = []
    for element in spell:
        for c in combos:
            if len(element_list) > 1 and set(element_list[-2:]) == c[0]:
                del element_list[-2:]
                element_list.append(c[1])
                continue
        for o in opposed:
            if o[0] in element_list and o[1] in element_list:
                element_list = []
        element_list.append(element)
    return ''.join(element_list)

if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rt') as enchantments:
        enchantments.next()
        count = 1
        for test_case in enchantments:
            buff = test_case.strip().split(' ')
            c = int(buff.pop(0))
            combine = [(set(s[:2]),s[2]) for s in buff[:c]]
            del buff[:c]
            d = int(buff.pop(0))
            oppose = buff[:d]
            del buff[:d]
            print "Case #%d: %s" % (count, invoke(combine, oppose, buff[1]))
            count += 1
