import argparse
import sys, os
from constructProbs import TransitionProbsBuilder, MatchProbsBuilder, abbrRemoveVowels
import itertools

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
		'percentage', help='percentage of each file (at end) to be used to testing')
	
	# can make the following option-controlled later if we start looking at other langs
	def isPythonFile(dirpath):
		return dirpath[len(dirpath)-3:len(dirpath)] == ".py"

	args = parser.parse_args()
	dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)
	percentTest = float(args.percentage)
	transProbBuilder = TransitionProbsBuilder(percentage)
	matchProbBuilder = MatchProbsBuilder(percentage)
	for dirpath in dirpaths:
		transProbBuilder.updateTransitionProbs(dirpath)
		matchProbBuilder.updateMatchProbsTrainingData(dirpath, abbrRemoveVowels)

	transProb = transProbBuilder.build()
	matchProb = matchProbBuilder.build()

	for dirpath in dirpaths:
		# TODO 
		corrected_line = viterbi(obs, states, trans_p, emit_p, transitions_per_timestep)
	

if __name__ == "__main__":
	main()