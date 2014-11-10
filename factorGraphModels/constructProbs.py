import re
import token
import tokenize
import io
from exceptions import NotImplementedError

class MatchProbs:
    def getProb(self, state, emission):
        # TODO
        pass


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
                self.transProb[key1][key2] = ImmutableNormalizingDict(self.transProb[key1][key2])
        return TransitionProbs(self.transProb)


    
