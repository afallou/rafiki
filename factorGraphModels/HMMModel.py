import argparse
import sys, os, io
from constructProbs import TransitionProbsBuilder, MatchProbsBuilder, abbrRemoveVowels, getSeparatorAndToken
import itertools
import tokenize

"""
	Return a list of filenames 
"""
def getDirpaths(root, keep_fn=lambda x: True):
	filepaths = [ [dirpath + '/' + fname for fname in filenames] for dirpath, _, filenames in os.walk(root)]
	flattened = list(itertools.chain(*filepaths))
	print(flattened)
	return filter(keep_fn, flattened)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'root', help='the directory to start recursively searching from')
	parser.add_argument(
		'percentage', help='percentage of each file (at end) to be used for testing')
	
	# can make the following option-controlled later if we start looking at other langs
	def isPythonFile(dirpath):
		return dirpath[len(dirpath)-3:len(dirpath)] == ".py"

	args = parser.parse_args()
	dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)
	percentTest = float(args.percentage)
	transProbBuilder = TransitionProbsBuilder(percentage)
	matchProbBuilder = MatchProbsBuilder(abbrFn, percentage)
	for dirpath in dirpaths:
		transProbBuilder.updateTransitionProbs(dirpath)
		matchProbBuilder.updateMatchProbsTrainingData(dirpath, abbrRemoveVowels)

	transProb = transProbBuilder.build()
	matchProb = matchProbBuilder.build()

	for dirpath in dirpaths:

		with open(dirpath, 'r') as f:
			totalLineCount = sum(1 for line in f)
			f.seek(0)
			startTestLine = int(totalLineCount * (1 - percentTest))
			lineCount = 0

			for line in f:
				if lineCount >= startTestLine:
					g = tokenize.generate_tokens(io.BytesIO(line).readline)
					observations = [token for (separator, token) in getSeparatorAndToken(g)]
					separators = [separator for (separator, token) in getSeparatorAndToken(g)]
					correctedLine = viterbi(observations, matchProb.allStates, transProb, matchProb, separators[1:])
				lineCount += 1
	

if __name__ == "__main__":
	main()