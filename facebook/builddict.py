'''Takes the Facebook supplied word list and turns it into a dictionary
of lists sorted by string length and stores it in a pickle for
efficient loading later.
'''
from __future__ import with_statement
import cPickle

d = {}
with open("twl06.txt") as wordlist
    for line in wordlist:
        word = line.strip()
        if len(word) in d:
            d[len(word)].append(word)
        else:
            d[len(word)] = [word]

with open("dict.txt", 'wb') as output:
    cPickle.dump(d, output, -1)
