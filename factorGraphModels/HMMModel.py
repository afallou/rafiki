import argparse
import sys, os, io
from constructProbs import TransitionProbsBuilder, MatchProbsBuilder, getSeparatorAndToken
from extract_features import vowels
import itertools
import tokenize
from solveHMM import viterbi

"""
	Return a list of filenames 
"""
def getDirpaths(root, keep_fn=lambda x: True):
	filepaths = [ [dirpath + '/' + fname for fname in filenames] for dirpath, _, filenames in os.walk(root)]
	flattened = list(itertools.chain(*filepaths))
	print(flattened)
	return filter(keep_fn, flattened)

def abbrRemoveVowels(token):
    return ''.join([l for l in token if l not in vowels])

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
	percentage = float(args.percentage)
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

			for lineno in range(startTestLine, totalLineCount):
				# TODO: if slow, the next line is wasteful since we get a new generator every time
				sep_tokens = [(separator, token) for (separator, token) in getSeparatorAndToken(g, 7, train=False)]
				observations = [token for (separator, token) in sep_tokens]
				separators = [separator for (separator, token) in sep_tokens]
				matchProb.setDirpath(dirpath)
				correctedLine = viterbi(observations, matchProbBuilder.allNames, transProb, matchProb, separators[1:])
				print correctedLine
	

if __name__ == "__main__":
	main()