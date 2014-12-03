import argparse
import sys, os, io
from constructProbs import TransitionProbsBuilder, MatchProbsBuilder, getSeparatorAndToken
from extract_features import vowels
import itertools
import tokenize
import random
from solveHMM import legacy_viterbi, particle_filtering
import copy 
    
"""
    Return a list of filenames 
"""
removalProb = 0.15
switchProb = 0.15
random.seed(1989)

def getDirpaths(root, keep_fn=lambda x: True):
    filepaths = [ [dirpath + '/' + fname for fname in filenames] for dirpath, _, filenames in os.walk(root)]
    flattened = list(itertools.chain(*filepaths))
    print(flattened)
    return filter(keep_fn, flattened)

def abbrRemoveVowels(token):
    return ''.join([l for l in token if l not in vowels])

def abbrRemoveVowelsTesting(token):
    token.setName(''.join([l for l in token.getName() if l not in vowels]))

def abbrRandomlyRemLetters(token):
    token.setName(''.join([l for l in token.getName() if random.random() > removalProb]))

def abbrRandomShuffleLetters(token):
    array = [l for l in token.getName()]
    for i in range(len(array)):
        if random.random() < switchProb and i+1 < len(array):
            letter = array[i]
            array[i] = array[i+1]
            array[i+1] = letter
    token.setName(''.join(array))

def abbrToken(token, abbrType):
    if token is None or not token.isName:
        return token
    if abbrType == 0:
        return token
    else:
        if abbrType == 2: # remove vowels and all, if type is 1 then shuffle and remove
            abbrRemoveVowelsTesting(token)
        abbrRandomShuffleLetters(token)
        abbrRandomlyRemLetters(token)
        return token

def runAndTrainingError(g, datatype, startLine, endLine, abbrType, matchProb, transProb, matchProbBuilder):
    samples_count = 0
    correct_count = 0
    for lineno in range(startLine, endLine):
        sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, lineno, train=False)] 
        # apply the abbreviation functions :) to all of the words in tokens
        tokens = [token for (separator, token) in sep_tokens] #actual list of words
        observations = [abbrToken(token, abbrType) for token in tokens]
        separators = [separator for (separator, token) in sep_tokens]
        matchProb.setDirpath(dirpath)
        if len(observations) == 0:
            continue
        correctedLines = viterbi(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
        samples_count += 1
        #increment training correct count if your best guess is equal to corrected lines
        # print 'comparison:', tokens, correctedLines
        if correctedLines[0][1] == tokens:
            correct_count += 1
    # print 'compared:', actual_tokens 
        # print observations
        # print correctedLines
        # print correctedLines[0][1]
        # print correctedLines
    print 'Number of {} Samples:'.format(dataType), samples_count
    print '{} Correct Ratio:'.format(dataType), float(correct_count)/(samples_count)
    print '{} Error:'.format(dataType), 1 - float(correct_count)/(samples_count)

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
    solve_fn = legacy_viterbi
    if args.solve == 'pfilter':
        print "Using particle_filtering"
    else:
        print "Using Viterbi"

    training_error_check = bool(args.training_error)
    abbrType = int(args.abbr_Type)

    transProbBuilder = TransitionProbsBuilder(percentage)
    matchProbBuilder = MatchProbsBuilder(abbrRemoveVowels, percentage)
    for dirpath in dirpaths:
        transProbBuilder.updateTransitionProbs(dirpath)
        matchProbBuilder.updateMatchProbsTrainingData(dirpath)

    transProb = transProbBuilder.build()
    matchProb = matchProbBuilder.build()

    for dirpath in dirpaths:
        with open(dirpath, 'r') as f:
            totalLineCount = sum(1 for line in f)
            f.seek(0)
            startTestLine = int(totalLineCount * (1 - percentage))
            g = tokenize.generate_tokens(io.BytesIO(f.read()).readline)
            if training_error_check:
                runAndTrainingError(g, 'Train', 1, startTestLine)
            runAndTrainingError(g, 'Test', startTestLine+1, totalLineCount+1, abbrType, matchProb, transProb, matchProbBuilder)

if __name__ == "__main__":
    main()
