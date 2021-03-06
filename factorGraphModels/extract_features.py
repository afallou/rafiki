import re
import token
import tokenize
import io
from exceptions import NotImplementedError
import sys
from sklearn import linear_model
import random
from collections import Counter
from copy import deepcopy

vowels = set(['a','e','i','o','u'])

def getNumSharedCharClass(tok1, tok2, charClassFn):
    count = 0
    word1 = [l for l in tok1 if charClassFn(l)]
    word2 = [l for l in tok2 if charClassFn(l)]
    trackerSet = set()
    for i in range(len(word1)):
        for j in range(len(word2)):
            if word1[i] == word2[j] and (j not in trackerSet):
                count += 1
                trackerSet.add(j)
                break # breaking so it only adds 1 per letter in word1
    return count

# Features
def getNumSharedConsonants(tok1, tok2):
    charClassFn = lambda l: l not in vowels and l.isalpha() #make sure consanant and a letter
    return getNumSharedCharClass(tok1, tok2, charClassFn)

def getNumSharedCapitals(tok1, tok2):
    charClassFn = lambda l: l.isupper()
    return getNumSharedCharClass(tok1, tok2, charClassFn)

def getNumSharedNonLetters(tok1, tok2):
    charClassFn = lambda l: not l.isalpha()
    return getNumSharedCharClass(tok1, tok2, charClassFn)

def getNumSharedLetters(tok1, tok2):
    charClassFn = lambda l: l.isalpha()
    return getNumSharedCharClass(tok1, tok2, charClassFn)

def getNumSharedOrderedLetters(tok1, tok2):
    counts = [[-1 for _ in xrange(len(tok2))] for _ in xrange(len(tok1))]
    return orderedLettersRecurse(tok1, tok2, counts)
    
def orderedLettersRecurse(tok1, tok2, counts):
    if len(tok1) == 0 or len(tok2) == 0:
        return 0
    else:
        count1 = Counter(tok1)
        count2 = Counter(tok2)
        shared_letters_count = sum([min(count1[c], count2[c]) for c in count1])
        if shared_letters_count == 0:
            return 0
        else:
            max_shared = 0
            for i in xrange(len(tok1)):
                for j in xrange(len(tok2)):
                    if tok1[i] == tok2[j]:
                        if counts[i][j] < 0:
                            counts[i][j] = orderedLettersRecurse(tok1[i+1:], tok2[j+1:], counts)
                        max_shared = max(1 + counts[i][j], max_shared)
            return max_shared

def getPercentageSharedCapitals(tok1, tok2):
    return 1. * getNumSharedCapitals(tok1, tok2) / len(tok1) if len(tok1) > 0 else 0

def getPercentageSharedConsonants(tok1, tok2):
    return 1. * getNumSharedConsonants(tok1, tok2) / len(tok1) if len(tok1) > 0 else 0

def getPercentageSharedLetters(tok1, tok2):
    return 1. * getNumSharedLetters(tok1, tok2) / len(tok1) if len(tok1) > 0 else 0

def getFeatureVector(name, abbr, abbr_lineno, last_seen_in_file):
    def getClosestDistance(lineno, linenoList):
        return lineno - max(linenoList)
    MAX_NUM_LINES = 30
    return [getNumSharedConsonants(abbr, name), 
            getNumSharedCapitals(abbr, name),
            getNumSharedNonLetters(abbr, name),
            getNumSharedLetters(abbr, name),
            getNumSharedOrderedLetters(abbr, name),
            getPercentageSharedCapitals(abbr, name),
            getPercentageSharedConsonants(abbr, name),
            getPercentageSharedLetters(abbr, name),
            getPercentageSharedLetters(name, abbr),
            (1 if name in last_seen_in_file else 0),
            getClosestDistance(abbr_lineno,last_seen_in_file[name]) if name in last_seen_in_file else MAX_NUM_LINES] # TODO
