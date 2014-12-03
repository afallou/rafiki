import argparse
import sys, os, io
from constructProbs import TransitionProbsBuilder, MatchProbsBuilder, getSeparatorAndToken
from extract_features import vowels
import itertools
import tokenize
from solveHMM import viterbi
import random

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

def abbrToken(token):
	return abbrRandomlyRemLetters(abbrRandomShuffleLetters(token))

def main():
	print 'working!!!!'
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'root', help='the directory to start recursively searching from')
	parser.add_argument(
		'percentage', help='percentage of each file (at end) to be used for testing')
	parser.add_argument(
		'training_error', type = int, default = 0, help='calculate training error - 1 or not - 0')

	# can make the following option-controlled later if we start looking at other langs
	def isPythonFile(dirpath):
		return dirpath[len(dirpath)-3:len(dirpath)] == ".py"

	args = parser.parse_args()
	dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)
	percentage = float(args.percentage)
	training_error_check = bool(args.training_error)
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

			if training_error_check:	
				# for training error
				training_samples = 0
				training_correct = 0
				for lineno in range(1, startTestLine - 1): # line 1 is a line
					print 'lineno: ', lineno
					# TODO: if slow, the next line is wasteful since we get a new generator every time
					sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, lineno, train=False)] 
					# apply the abbreviation functions :) to all of the words in tokens
					tokens = [token for (separator, token) in sep_tokens] #actual list of words
					observations = [abbrToken(tokens) for token in tokens]
					separators = [separator for (separator, token) in sep_tokens]
					matchProb.setDirpath(dirpath)
					prob, correctedLines = viterbi(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
					training_samples += 1
					#increment training correct count if your best guess is equal to corrected lines
					print 'comparison:', tokens, correctedLines
					if correctedLines == tokens:
						training_correct += 1 
				print 'Number of Training Samples:', training_samples
				print 'Training Correct Ratio:', float(training_correct)/(training_samples)
				print 'Training Error:', 1 - float(training_correct)/(training_samples)

			# for testing error
			testing_samples = 0
			testing_correct = 0	
			for lineno in range(startTestLine, totalLineCount + 1): # line 1 is a line
				print 'lineno: ', lineno
				# TODO: if slow, the next line is wasteful since we get a new generator every time
				sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, lineno, train=False)] 
				# apply the abbreviation functions :) to all of the words in tokens
				tokens = [token for (separator, token) in sep_tokens] #actual list of words
				observations = [abbrToken(tokens) for token in tokens]
				separators = [separator for (separator, token) in sep_tokens]
				matchProb.setDirpath(dirpath)
				prob, correctedLines = viterbi(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
				testing_samples += 1
				#increment training correct count if your best guess is equal to corrected lines
				print 'comparison:', tokens, correctedLines
				if correctedLines == tokens:
					testing_correct += 1 

				print 'Number of Test Samples:', testing_samples
				print 'Test Correct Ratio:', float(test_correct)/(test_samples)
				print 'Test Error:', 1 - float(test_correct)/(test_samples)

if __name__ == "__main__":
	main()