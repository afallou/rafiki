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
    tok1Consonants = Counter([l for l in tok1 if charClassFn(l)])
    tok2Consonants = Counter([l for l in tok2 if charClassFn(l)])
    return sum([min(tok1Consonants[c],tok2Consonants[c]) for c in tok1Consonants])


class MatchProbsBuilder:
    def __init__(self, abbrFn, percentage=0.2):
        self.allNames = set()
        self.percentTest = percentage
        self.abbrFn = abbrFn
        self.logreg = linear_model.LogisticRegression()
        self.last_seen_in_file = {}
        self.X = []
        self.Y = []

    def updateMatchProbsTrainingData(self, dirpath):
        with open(dirpath,'r') as f:
            totalLineCount = sum(1 for line in f)
            f.seek(0)
            stopTrainLine = int(totalLineCount * (1 - float(self.percentTest)))
            g = tokenize.generate_tokens(io.BytesIO(f.read()).readline)
            self.last_seen_in_file[dirpath] = {}
            for toknum, tokval, startloc, _, _ in g:
                lineno, _ = startloc
                if lineno >= stopTrainLine:
                    return 

                abbrToken = self.abbrFn(tokval)
                feature_vec = getFeatureVector(tokval, abbrToken, lineno, self.last_seen_in_file[dirpath])

                if toknum == token.NAME:
                    if tokval not in self.last_seen_in_file[dirpath]:
                        self.last_seen_in_file[dirpath][tokval] = []
                    last_seen_in_file_for_tokval = self.last_seen_in_file[dirpath][tokval]
                    last_seen_in_file_for_tokval.append(lineno) # order important
                    self.allNames.add(tokval)
                    self.X.append(feature_vec)
                    self.Y.append(1)

                    randomName = random.sample(self.allNames, 1)
                    while random == tokval:
                        randomName = random.sample(self.allNames, 1)

                    feature_vec = getFeatureVector(randomName[0], abbrToken, lineno, self.last_seen_in_file[dirpath])
                    self.X.append(feature_vec)
                    self.Y.append(0)

    def build(self):
        self.logreg.fit(self.X, self.Y)
        return MatchProbs(self.logreg, self.last_seen_in_file)
        

def getFeatureVector(name, abbr, abbr_lineno, last_seen_in_file):
    def getClosestDistance(lineno, linenoList):
        return lineno - max(linenoList)
    MAX_NUM_LINES = 30
    return [getNumSharedConsonants(abbr, name), 
            getNumSharedCapitals(abbr, name),
            getNumSharedNonLetters(abbr, name),
            getNumSharedLetters(abbr, name),
            getNumSharedOrderedLetters(abbr, name),
            getNumSharedOrderedLetters(abbr, name),
            getPercentageSharedCapitals(abbr, name),
            getPercentageSharedConsonants(abbr, name),
            getPercentageSharedLetters(abbr, name),
            getOtherPercentageSharedLetters(abbr, name),
            (1 if name in last_seen_in_file else 0),
            getClosestDistance(abbr_lineno,last_seen_in_file[name]) if name in last_seen_in_file else MAX_NUM_LINES] # TODO


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

def getOtherPercentageSharedLetters(tok1, tok2):
    return 1. * getNumSharedLetters(tok1, tok2) / len(tok2) if len(tok2) > 0 else 0

class MatchProbs:
    def __init__(self, logreg, last_seen_in_file):
        self.logreg = logreg 
        # last_seen_in_file is a map from filename => {name:[lineno1, lineno2, ...]}
        self.last_seen_in_file = last_seen_in_file
        self.dirpath = None
        self.lineno = None
        # print 'coeffs', self.logreg.coef_
    def setDirpath(self, dirpath):
        self.dirpath = dirpath

    def getProb(self, name, abbr):
        """
            name: a string 
            abbr: a MaybeName (TODO: what if this is not a name?)
        """
        assert(self.dirpath is not None)
        feature_vec = getFeatureVector(name, abbr.getName(), abbr.lineno, self.last_seen_in_file[self.dirpath])
        # print self.logreg.classes_
        return self.logreg.predict_proba([feature_vec])[0][1] # TODO check order in self.classes_

class TransitionProbs:
    def __init__(self, transProb, lambda_val=0.7):
        self.transProb = deepcopy(transProb)
        for s0 in transProb:
            for transition in transProb[s0]:
                for s1 in transProb[s0][transition]:
                    self.transProb[s0][transition][s1] = transProb[s0][transition][s1] / float(sum(transProb[s0][transition].values()))

        self.startProb = {}
        for s0 in self.transProb:
            self.startProb[s0] = sum([sum(countsDict.values()) for countsDict in self.transProb[s0].values()])
        for s0 in self.transProb:
            self.startProb[s0] = self.startProb[s0]/sum(self.startProb.values())

        print 'startProb'
        print self.startProb

       # for s0 in self.transProb:

        #self.startProb = {state:float(sum(self.transProb[state][transition].values() for transition in self.transProb[state]))/sum(self.startProb.values()) for state in self.startProb}
        self.lambda_val = lambda_val

    def getProb(self, s0, sep, s1):
        print "s0==", s0, "==sep==", sep, "==s1==", s1, "=="
        s0 = MaybeName(True, 0, s0)
        s1 = MaybeName(True, 0, s1)
        try:
            print ('asdfgtransProb' + str(self.transProb[s0][sep][s1]))
            return self.transProb[s0][sep][s1] * self.lambda_val + self.startProb.get(s0, 0) * (1- self.lambda_val)
        except KeyError:
            return 0

    def getStartProb(self, s0):
        return self.startProb.get(MaybeName(True, 0, s0), 0)

class MaybeName:
    def __init__(self,isName, lineno, name=None):
        assert((name is None and not isName) or (name is not None and isName))
        self.isName = isName
        self.name = name
        self.lineno = lineno

    def getName(self):
        assert(self.isName)
        return self.name

    def __repr__(self):
        return self.name if self.isName else 'CONSTANT'
    
    def __eq__(self, other):
        if not self.isName and other.isName:
            return True
        if self.isName and other.isName and other.getName()==self.getName():
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(str(self.isName)+self.name) if self.isName else hash(str(self.isName))


SPACE = ' '
def getSeparatorAndToken(token_gen, testTrainLine, train=True): # generator, yields (separator, MaybeName)
    at_beginning = True
    prev_sep = None # this is the separator that comes after prev_non_sep_tok
    for toknum, tokval, startloc, _, _  in token_gen:
        lineno, _ = startloc
        if train:
            if lineno >= testTrainLine:
                return
        else:
            if lineno != testTrainLine:
                continue

        # we see a token that is not a separator
        if toknum == tokenize.COMMENT:
            continue
        if toknum == token.NAME:
            if not at_beginning and prev_sep is None:
                prev_sep = SPACE
            yield (prev_sep, MaybeName(True, lineno, tokval))
            prev_sep = None
        elif toknum == token.NUMBER or toknum == token.STRING:
            if not at_beginning and prev_sep is None:
                prev_sep = SPACE 
            yield(prev_sep, MaybeName(False, lineno))
            prev_sep = None
        elif at_beginning:
            continue
        else:  
            if prev_sep is None:
                prev_sep = tokval
            else:
                prev_sep = prev_sep + tokval # multiple separators in a row; treat as a special separator 
        at_beginning = False



"""
    Return:
        transProb such that transProb[w0][sep][w1] gives you the count
"""
class TransitionProbsBuilder:
    # we're going to treat every thing other than name, string, number as a separator

    def __init__(self, percentage=0.2):
        self.transProb = {}
        self.percentTest = percentage

    def updateTransitionProbs(self, dirpath):
        with open(dirpath,'r') as f:
            totalLineCount = sum(1 for line in f)
            f.seek(0)
            stopTrainLine = int(totalLineCount * (1 - float(self.percentTest)))
            g = tokenize.generate_tokens(io.BytesIO(f.read()).readline)
            prev_non_sep_tok = None
            for prev_sep, maybe_name  in getSeparatorAndToken(g, stopTrainLine):
                assert((prev_non_sep_tok is None and prev_sep is None) or (prev_non_sep_tok is not None and prev_sep is not None))
                if prev_non_sep_tok is not None and prev_sep is not None:
                    if prev_non_sep_tok in self.transProb:
                        if prev_sep in self.transProb[prev_non_sep_tok]:
                            if maybe_name in self.transProb[prev_non_sep_tok][prev_sep]:
                                self.transProb[prev_non_sep_tok][prev_sep][maybe_name] += 1
                            else:
                                self.transProb[prev_non_sep_tok][prev_sep][maybe_name] = 1
                        else:
                            self.transProb[prev_non_sep_tok][prev_sep] = {maybe_name: 1}

                    else:
                        self.transProb[prev_non_sep_tok] = {prev_sep: {maybe_name: 1}}
                
                prev_non_sep_tok = maybe_name

    def build(self):
        return TransitionProbs(self.transProb)



