import re
import token
import tokenize
import io
from exceptions import NotImplementedError
import sys
from sklearn import linear_model
import random

vowels = set(['a','e','i','o','u'])

def abbrRemoveVowels(token):
    ''.join([l for l in token if l not in vowels]);

def getNumSharedCharClass(tok1, tok2, charClassFn):
    tok1Consonants = Counter([l for l in tok1 if charClassFn(l)])
    tok2Consonants = Counter([l for l in tok2 if charClassFn(l)])
    return sum([min(tok1Consonants[c],tok2Consonants[c]) for c in tok1Consonants])


class MatchProbsBuilder:
    def __init__(self):
        self.allNames = set()
        self.logreg = linear_model.LogisticRegression()
        self.last_seen_in_file = {}
        self.X = []
        self.Y = []

    def updateMatchProbsTrainingData(self, dirpath, abbrFn):
        def getClosestDistance(lineno, linenoList):
            lastlineno = None
            for l in linenoList:
                if l > lineno:
                    assert(lastlineno is not None)
                    return abs(lineno-lastlineno)
                else: 
                    lastlineno = l 

        with open(dirpath,'r') as f:
            content=f.read()
            g = tokenize.generate_tokens(io.BytesIO(content).readline)
            self.last_seen_in_file[dirpath] = {}
            for toknum, tokval, startloc, endloc, lineno in g:
                if toknum == token.NAME:
                    if tokval not in self.last_seen_in_file[dirpath]:
                        self.last_seen_in_file[tokval] = {}
                    last_seen_in_file_for_tokval = last_seen_in_file[dirpath][tokval]

                    abbrToken = abbrFn(tokval)
                    feature_vec = getFeatureVec(tokval, abbr, self.last_seen_in_file)
                    last_seen_in_file_for_tokval.append(lineno) # order important
                    self.allNames.append(tokval)
                    self.X.append(feature_vec)
                    self.Y.append(1)

                    randomName = random.choice(self.allNames)
                    while random == tokval:
                        randomName = random.choice(self.allNames)

                    feature_vec = getFeatureVec(random, abbr, self.last_seen_in_file)
                    self.X.append(feature_vec)
                    self.Y.append(0)

    def build(self):
        self.logreg.fit(self.X, self.Y)
        return MatchProbs(self.logreg, self.last_seen_in_file)
        

def getFeatureVector(name, abbr, last_seen_in_file):
    return [getNumSharedConsonants(abbrToken, tokval), 
            # others 
            (1 if tokval in self.last_seen_in_file[dirpath] else 0),
            getClosestDistance(lineno,self.last_seen_in_file_for_tokval) if tokval in self.last_seen_in_file[dirpath] else sys.maxint] # TODO


# Features
def getNumSharedConsonants(tok1, tok2):
    charClassFn = lambda l: l not in vowels
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
    orderedLettersRecurse(tok1, tok2, counts)
    
def orderedLettersRecurse(tok1, tok2, counts):
    if len(tok1) == 0 or len(tok2) == 0:
        return 0
    else:
        count1 = Counter(tok1)
        count2 = Counter(tok2)
        shared_letters_count = sum([min(count1, count2) for c in count1])
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
    return 1. * getNumSharedCapitals(tok1, tok2) / len(tok1)

def getPercentageSharedConsonants(tok1, tok2):
    return 1. * getNumSharedConsonants(tok1, tok2) / len(tok1)

def getPercentageSharedLetters(tok1, tok2):
    return 1. * getNumSharedLetters(tok1, tok2) / len(tok1)

def getOtherPercentageSharedLetters(tok1, tok2):
    return 1. * getNumSharedLetters(tok1, tok2) / len(tok2)

class MatchProbs:
    def __init__(self, logreg, last_seen_in_file):
        self.logreg = logreg 
        # last_seen_in_file is a map from filename => {name:[lineno1, lineno2, ...]}
        self.last_seen_in_file = last_seen_in_file

    def getProb(self, name, abbr):
        feature_vec = getFeatureVec(name, abbr, self.last_seen_in_file)
        print self.classes_
        return self.logreg.predict_proba([feature_vec])[0][0] # TODO check order in self.classes_



class ImmutableNormalizingDict:
  """
    Warning: incomplete dict interface! May fix later

    This is overkill, thought I needed it but turns out I don't, may refactor later
  """
  def __init__(self, python_dict):
    self.store = python_dict
    self.summed = float(sum(self.store.values()))

  def __getitem__(self, key):
    return self.store[key] / self.summed

  def __contains__(self, key):
    return key in self.store

  def __str__(self):
    return str(self.store)

class TransitionProbs:
    def __init__(self, transProb, lambda_val=0.7):
        self.transProb = transProb
        self.startProb = {s0:sum(self.transProb[s0][transition].summed for transition in self.transProb[s0]) for s0 in self.transProb}
        self.startProb = {state:float(self.startProb[state])/sum(self.startProb.values()) for state in self.startProb}
        self.lambda_val = lambda_val

    def getProb(self, s0, sep, s1):
        return self.transProb[s0][sep][s1] * self.lambda_val + self.startProb[s0] * (1- self.lambda_val)

    def getStartProb(self, s0):
        return self.startProb[s0]

"""
    Return:
        transProb such that transProb[w0][sep][w1] gives you the count
"""
class TransitionProbsBuilder:
    # we're going to treat every thing other than name, string, number as a separator

    def __init__(self):
        self.transProb = {}

    def updateTransitionProbs(self, dirpath):
        with open(dirpath,'r') as f:
            content=f.read()
            g = tokenize.generate_tokens(io.BytesIO(content).readline)
            prev_non_sep_tok = None
            prev_sep = None # this is the separator that comes after prev_non_sep_tok
            for toknum, tokval, _, _, _  in g:
                # we see a token that is not a separator
                if toknum == tokenize.COMMENT:
                    continue
                if toknum == token.NAME:
                    if prev_non_sep_tok != None and prev_sep != None:
                        if prev_non_sep_tok in self.transProb:
                            if prev_sep in self.transProb[prev_non_sep_tok]:
                                if tokval in self.transProb[prev_non_sep_tok][prev_sep]:
                                    self.transProb[prev_non_sep_tok][prev_sep][tokval] += 1
                                else:
                                    self.transProb[prev_non_sep_tok][prev_sep][tokval] = 1
                            else:
                                self.transProb[prev_non_sep_tok][prev_sep] = {tokval: 1}

                        else:
                            self.transProb[prev_non_sep_tok] = {prev_sep: {tokval: 1}}
                    prev_non_sep_tok = tokval
                    prev_sep = None
                elif toknum != token.NAME and toknum != token.NUMBER and toknum != token.STRING: # we see a token that is a separator
                    if prev_non_sep_tok != None:
                        if prev_sep is None:
                            prev_sep = tokval
                        else:
                            prev_sep = prev_sep + tokval # multiple separators in a row; treat as a special separator

    def build(self):
        # replace all the innermost dicts with ImmutableNormalizingDicts
        for key1 in self.transProb:
            for key2 in self.transProb[key1]:
		print key1
		print key2
		print self.transProb[key1][key2]
                self.transProb[key1][key2] = ImmutableNormalizingDict(self.transProb[key1][key2])
        return TransitionProbs(self.transProb)



