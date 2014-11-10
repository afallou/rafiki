import argparse
import sys, os, subprocess
from constructProbs import TransitionProbsBuilder

"""
	Return a list of filenames 
"""
def getDirpaths(root, keep_fn=lambda x: True):
	return filter(keep_fn, [dirpath for dirpath, _, _ in os.walk(root)])

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
   	print transProb

if __name__ == "__main__":
	main()