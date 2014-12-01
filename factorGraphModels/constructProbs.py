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
from extract_features import getFeatureVector

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
        if not self.isName and not other.isName:
            return True
        if self.isName and other.isName and other.getName()==self.getName():
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(str(self.isName)+self.name) if self.isName else hash(str(self.isName))

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
                    self.allNames.add(MaybeName(True, lineno, tokval))
                    self.X.append(feature_vec)
                    self.Y.append(1)

                    randomName = random.sample(self.allNames, 1)[0]
                    while random == tokval:
                        randomName = random.sample(self.allNames, 1)[0]
                    assert(randomName.isName)

                    feature_vec = getFeatureVector(randomName.getName(), abbrToken, lineno, self.last_seen_in_file[dirpath])
                    self.X.append(feature_vec)
                    self.Y.append(0)

    def build(self):
        self.logreg.fit(self.X, self.Y)
        return MatchProbs(self.logreg, self.last_seen_in_file)

class MatchProbs:
    CONSTANT_MATCH_PROB = 1.0
    def __init__(self, logreg, last_seen_in_file):
        self.logreg = logreg 
        # last_seen_in_file is a map from filename => {name:[lineno1, lineno2, ...]}
        self.last_seen_in_file = last_seen_in_file
        self.dirpath = None
        self.lineno = None
        # print 'coeffs', self.logreg.coef_
    def setDirpath(self, dirpath): # TODO: this seems error prone, change to arg of getProb
        self.dirpath = dirpath

    def getProb(self, name, abbr):
        """
            name: a string 
            abbr: a MaybeName (TODO: what if this is not a name?)
        """
        assert(self.dirpath is not None)
        if not abbr.isName or not name.isName:
            return MatchProbs.CONSTANT_MATCH_PROB
        else:
            feature_vec = getFeatureVector(name.getName(), abbr.getName(), abbr.lineno, self.last_seen_in_file[self.dirpath])
            # print self.logreg.classes_
            return self.logreg.predict_proba([feature_vec])[0][1] # TODO check order in self.classes_

class TransitionProbs:
    CONSTANT_TRANSITION_PROB = 1.0
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

        self.lambda_val = lambda_val

    def getProb(self, s0, sep, s1):
        # if not s0.isName or not s0.isName:
        #    return CONSTANT_TRANSITION_PROB
        try:
            return self.transProb[s0][sep][s1] * self.lambda_val + self.startProb.get(s0, 0) * (1- self.lambda_val)
        except KeyError:
            return 0

    def getStartProb(self, s0):
        if not s0.isName:
            return TransitionProbs.CONSTANT_TRANSITION_PROB
        else:
            return self.startProb.get(s0, 0)


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
            if lineno < testTrainLine:
                continue
            elif lineno  > testTrainLine:
                return

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
                # if not maybe_name.isName:
                    # continue
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



