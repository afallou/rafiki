import argparse
import sys, os, io
from constructProbs import TransitionProbsBuilder, MatchProbsBuilder, getSeparatorAndToken
from extract_features import vowels
import itertools
import tokenize
import random
from solveHMM import viterbi, particle_filtering

"""
	Return a list of filenames 
"""
removalProb = 0.3
switchProb = 0.3

def getDirpaths(root, keep_fn=lambda x: True):
	filepaths = [ [dirpath + '/' + fname for fname in filenames] for dirpath, _, filenames in os.walk(root)]
	flattened = list(itertools.chain(*filepaths))
	print(flattened)
	return filter(keep_fn, flattened)

def abbrRemoveVowels(token):
	return ''.join([l for l in token if l not in vowels])

def abbrRandomlyRemLetters(token):
	return ''.join([l for l in token if random.random() > removalProb])

def abbrRandomShuffleLetters(token):
	array = [l for l in token]
	for i in range(len(array)):
		if random.random() < switchProb and i+1 < len(array):
			letter = array[i]
			array[i] = array[i+1]
			array[i+1] = letter
	return ''.join(array)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'root', help='the directory to start recursively searching from')
	parser.add_argument(
		'percentage', help='percentage of each file (at end) to be used for testing')
	parser.add_argument(
		'solve', help='solve algo (viterbi or pfilter)')
	
	# can make the following option-controlled later if we start looking at other langs
	def isPythonFile(dirpath):
		return dirpath[len(dirpath)-3:len(dirpath)] == ".py"

	args = parser.parse_args()
	dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)
	percentage = float(args.percentage)

	solve_fn = viterbi
	if args.solve == 'pfilter':
		print "Using particle_filtering"
	else:
		print "Using Viterbi"


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
			print totalLineCount
			f.seek(0)
			startTestLine = int(totalLineCount * (1 - percentage))
			g = tokenize.generate_tokens(io.BytesIO(f.read()).readline)

			for lineno in range(startTestLine, totalLineCount + 1): # line 1 is a line
				print 'lineno: ', lineno
				# TODO: if slow, the next line is wasteful since we get a new generator every time
				sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, lineno, train=False)]
				observations = [token for (separator, token) in sep_tokens]
				separators = [separator for (separator, token) in sep_tokens]
				matchProb.setDirpath(dirpath)
				correctedLine = solve_fn(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
				print observations
				print correctedLine

if __name__ == "__main__":
	main()