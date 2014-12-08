from constructProbs import getSeparatorAndToken, TransitionProbsBuilder, MatchProbsBuilder
from HMMModel import AbbrOperation
from solveHMM import viterbi, legacy_viterbi  
import tokenize
import unittest
import io

class TestConstructProbs(unittest.TestCase):
    
    def setUp(self):
        pass
 
    def test_new_viterbi(self):
        test_contents = "class Foo:\n\tdef bar(self):\n\t\treturn \"baz\"\n"
        test_contents += test_contents
        test_contents += test_contents
        train_contents = "class Foo:\n\tdef bar(self):\n\t\treturn \"baz\"\n"
        f = open("test","w")  
        contents = test_contents + train_contents
        f.write(test_contents + train_contents)
        f.close()

        percentage = 0.75 
        abbrCallable = AbbrOperation(0)# no abbreviation
        transProbBuilder = TransitionProbsBuilder(percentage)
        matchProbBuilder = MatchProbsBuilder(abbrCallable, percentage)

        transProbBuilder.updateTransitionProbs("test")
        matchProbBuilder.updateMatchProbsTrainingData("test") 
        transProb = transProbBuilder.build(len(matchProbBuilder.allNames))
        matchProb = matchProbBuilder.build()
        matchProb.setDirpath("test")
        g = tokenize.generate_tokens(io.BytesIO(contents).readline)
        for lineno in range(1,5):
            lst = [pair for pair in getSeparatorAndToken(g, lineno, train=False)][:-1]
            seps = [sep for (sep, tok) in lst]
            toks = [tok for (sep, tok) in lst]
            vit = viterbi(toks, matchProbBuilder.allNames, transProb, matchProb, seps[1:], False, 5)
            lvit = legacy_viterbi(toks, matchProbBuilder.allNames, transProb, matchProb, seps[1:], False)
            self.assertIn(lvit[0], vit)

if __name__ == '__main__':
    unittest.main()
