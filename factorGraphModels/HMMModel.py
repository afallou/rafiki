import argparse
import sys, os, io
from constructProbs import TransitionProbsBuilder, MatchProbsBuilder, getSeparatorAndToken
from extract_features import vowels
import itertools
import tokenize
import random
from solveHMM import particle_filtering, viterbi
import copy 
import pdb
import parser
import numpy
import time    
"""
    Return a list of filenames 
"""
removalProb = 0.5
switchProb = 0.5
RNG_SEED = 1989
AVERAGE_NUM = 1

verbose = False

def getDirpaths(root, keep_fn=lambda x: True):
    filepaths = [ [dirpath + '/' + fname for fname in filenames] for dirpath, _, filenames in os.walk(root)]
    flattened = list(itertools.chain(*filepaths))
    return filter(keep_fn, flattened)


# operates on strings 
class AbbrOperation:
    def __init__(self, abbr_Type, seed=RNG_SEED):
        self.rng = random.Random()
        self.rng.seed(RNG_SEED)
        self.abbr_Type = abbr_Type

    def reset(self, seed=RNG_SEED):
        self.rng.seed(seed)

    def __call__(self, string):
        if self.abbr_Type == 0:
            return string
        elif self.abbr_Type == 1:
            res = self.__abbrRandomShuffleLetters(string)
            return self.__abbrRandomlyRemLetters(res)
        else:
            res = self.__abbrRandomShuffleLetters(string)
            res = self.__abbrRandomlyRemLetters(res)
            self.__abbrRemoveVowelsTesting(res)
            return res

    # the following all take in a string and return a string 
    def __abbrRemoveVowelsTesting(self, string):
        return ''.join([l for l in string if l not in vowels])

    def __abbrRandomlyRemLetters(self, string):
        return ''.join([l for l in string if self.rng.random() > removalProb])

    def __abbrRandomShuffleLetters(self, string):
        array = list(string)
        for i in range(len(array)):
            if self.rng.random() < switchProb and i+1 < len(array):
                letter = array[i]
                array[i] = array[i+1]
                array[i+1] = letter
        return ''.join(array)

def parsesCorrectly(last_separator, seps):
    if last_separator is None:
        last_separator = ''
    seps = seps + [last_separator]
    def func(probs_and_names_so_far):
        names_so_far = probs_and_names_so_far[1]
        serialized_path = ''.join([str(names_so_far[i])+seps[i+1] for i in xrange(len(names_so_far))])
        try:
            parser.suite(serialized_path)
        except Exception as e:
            if str(e).startswith('unexpected EOF'):
                return True
            else:
                return False
        return True
    return func

def runAndTrainingError(g, dataType, startLine, endLine, abbrType, matchProb, transProb, matchProbBuilder, dirpath, solve_fn, useParseFilter=True):
    samples_count = 0
    correct_count = 0
    for lineno in range(startLine, endLine):
        sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, lineno, train=False)]
        last_sep = sep_tokens[-1][0]
        sep_tokens = sep_tokens[:-1]  
        # apply the abbreviation functions :) to all of the words in tokens
        tokens = [token for (separator, token) in sep_tokens] #actual list of words
        actual_tokens = copy.deepcopy(tokens)
        abbrCallable = AbbrOperation(abbrType)
        observations = [token.apply(abbrCallable) for token in tokens]
        separators = [separator for (separator, token) in sep_tokens]
        matchProb.setDirpath(dirpath)
        if len(observations) == 0:
            continue
        correctedLines = solve_fn(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
        samples_count += 1
        #increment training correct count if your best guess is equal to corrected lines
        # print 'comparison:', tokens, correctedLines
        if useParseFilter:
          correctedLines = filter(parsesCorrectly(last_sep, separators), correctedLines)
        comparisons = [line == actual_tokens for (_, line) in correctedLines]
        if any(comparisons):
            correct_count += 1
        if verbose:
            print 'original:', actual_tokens 
            print 'abbreviated:', observations
            print 'corrected:', correctedLines
    error = 1 - float(correct_count)/(samples_count)
    print 'Number of {} Samples:'.format(dataType), samples_count
    print '{} Correct Ratio:'.format(dataType), float(correct_count)/(samples_count)
    print '{} Error:'.format(dataType), error
    return error

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'root', help='the directory to start recursively searching from')
    parser.add_argument(
        'percentage', help='percentage of each file (at end) to be used for testing')
    parser.add_argument(
        'solve', help='solve algo (legacy_viterbi or pfilter)')
    parser.add_argument(
        'training_error', type = int, default = 0, help='calculate training error - 1 or not - 0')
    parser.add_argument(
        'abbr_Type', type = int, default = 0, help='what abbr function to apply: 0 - nothing, 1 - switch & remove, 2 - switch, remove, & no vowels')
    # can make the following option-controlled later if we start looking at other langs
    def isPythonFile(dirpath):
        return dirpath[len(dirpath)-3:len(dirpath)] == ".py"

    args = parser.parse_args()
    dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)
    percentage = float(args.percentage)
    solve_fn = viterbi
    if args.solve == 'pfilter':
        print "Using particle_filtering"
        solve_fn = particle_filtering
    else:
        print "Using Viterbi"

    training_error_check = bool(args.training_error)
    abbrType = int(args.abbr_Type)

    abbrCallable = AbbrOperation(abbrType)
    transProbBuilder = TransitionProbsBuilder(percentage)
    matchProbBuilder = MatchProbsBuilder(abbrCallable, percentage)
    for dirpath in dirpaths:
        transProbBuilder.updateTransitionProbs(dirpath)
        matchProbBuilder.updateMatchProbsTrainingData(dirpath) 

    matchProb = matchProbBuilder.build()
    transProb = transProbBuilder.build(len(matchProbBuilder.allNames))

    test_errors = []
    training_errors = []
    for _ in xrange(AVERAGE_NUM):
        for dirpath in dirpaths:
            with open(dirpath, 'r') as f:
                totalLineCount = sum(1 for line in f)
                f.seek(0)
                startTestLine = int(totalLineCount * (1 - percentage))
                g = tokenize.generate_tokens(io.BytesIO(f.read()).readline)
                if training_error_check:
                    training_errors.append(runAndTrainingError(g, 'Train', 1, startTestLine, abbrType, matchProb, transProb, matchProbBuilder, dirpath, solve_fn))
                t1 = time.clock()
                test_errors.append(runAndTrainingError(g, 'Test', startTestLine+1, totalLineCount+1, abbrType, matchProb, transProb, matchProbBuilder, dirpath, solve_fn))
                t2 = time.clock()
                print "test time:", t2 - t1
    if training_error_check:
        print "Average training error:", numpy.mean(training_errors)
    print "Average test error:", numpy.mean(test_errors)

if __name__ == "__main__":
    main()
