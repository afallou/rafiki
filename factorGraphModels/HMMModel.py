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
			abbrRemoveVowels(token)
		abbrRandomShuffleLetters(token)
		abbrRandomlyRemLetters(token)
		return token

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
				# for training error
				training_samples = 0
				training_correct = 0
				for lineno in range(1, startTestLine - 1): # line 1 is a line
					# TODO: if slow, the next line is wasteful since we get a new generator every time
					sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, lineno, train=False)] 
					# apply the abbreviation functions :) to all of the words in tokens
					tokens = [token for (separator, token) in sep_tokens] #actual list of words
					actual_tokens = copy.deepcopy(tokens)
					observations = [abbrToken(token, abbrType) for token in tokens]
					separators = [separator for (separator, token) in sep_tokens]
					matchProb.setDirpath(dirpath)
					if len(observations) == 0:
						continue
					correctedLines = legacy_viterbi(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
					print 'test here'
					training_samples += 1
					#increment training correct count if your best guess is equal to corrected lines
					if correctedLines[0][1] == tokens:
						training_correct += 1 
					# print 'compared:', actual_tokens 
					# print observations
					# print correctedLines
					# print correctedLines[0][1]
					# print correctedLines
				print 'Number of Training Samples:', training_samples
				print 'Training Correct Ratio:', float(training_correct)/(training_samples)
				print 'Training Error:', 1 - float(training_correct)/(training_samples)

				# 'hallo there {}'.format('bob')

			# for testing error
			test_samples = 0
			test_correct = 0	
			for lineno in range(startTestLine, totalLineCount + 1): # line 1 is a line
				# print 'lineno: ', lineno
				# TODO: if slow, the nesxt line is wasteful since we get a new generator every time
				sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, lineno, train=False)] 
				# apply the abbreviation functions :) to all of the words in tokens
				tokens = [token for (separator, token) in sep_tokens] #actual list of words
				actual_tokens = copy.deepcopy(tokens)
				observations = [abbrToken(token, abbrType) for token in tokens]
				separators = [separator for (separator, token) in sep_tokens]
				matchProb.setDirpath(dirpath)
				# print len(observations)
				if len(observations) == 0:
					continue
				correctedLines = legacy_viterbi(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
				test_samples += 1
				#increment training correct count if your best guess is equal to corrected lines
				# print 'compared:', actual_tokens 
				# print observations
				# print correctedLines[0][1]
				# print correctedLines
				if correctedLines[0][1] == actual_tokens:
					test_correct += 1 
			print 'Number of Test Samples:', test_samples
			print 'Test Correct Ratio:', float(test_correct)/(test_samples)
			print 'Test Error:', 1 - float(test_correct)/(test_samples)

if __name__ == "__main__":
	main()