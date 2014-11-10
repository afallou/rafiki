import argparse
import sys, os, subprocess
from constructProbs import TransitionProbsBuilder
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
	
	# can make the following option-controlled later if we start looking at other langs
	def isPythonFile(dirpath):
		return dirpath[len(dirpath)-3:len(dirpath)] == ".py"

	args = parser.parse_args()
	dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)
	transProbBuilder = TransitionProbsBuilder()
	for dirpath in dirpaths:
		transProbBuilder.updateTransitionProbs(dirpath)

	transProb = transProbBuilder.build()
	

if __name__ == "__main__":
	main()