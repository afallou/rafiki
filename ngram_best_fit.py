
import collections
import math

SENTENCE_BEGIN = '-BEGIN-'

def sliding(xs, windowSize):
    for i in xrange(1, len(xs) + 1):
        yield xs[max(0, i - windowSize):i]

def removeAll(s, chars):
      return ''.join(filter(lambda c: c not in chars, s))

def alphaOnly(s):
     s = s.replace('-', ' ')
     return filter(lambda c: c.isalpha() or c == ' ', s)

def cleanLine(l):
    return alphaOnly(l.strip().lower())

def words(l):
    return l.split()

############################################################
# Make an n-gram model of words in text

def makeLanguageModels(path,n):
    ngramsCounts = collections.Counter()
    ntotalCounts = collections.Counter()

    def ngramWindow(win):
        assert len(win) in range(1,n+1)
        if len(win) == 1:
            return (SENTENCE_BEGIN, win[0])
        else:
            return tuple(win)

    with open(path, 'r') as f:
        for l in f:
            ws = words(cleanLine(l))
            ngrams = [ngramWindow(x) for x in sliding(ws, n)]
            ngramsCounts.update(ngrams)
            ntotalCounts.update([x[0] for x in ngrams])
    vocab_size  = len(ntotalCounts)
 
    def ngramModel(n_length_list):
        if len(n_length_list) != n:
                raise Exception("Need to input list of elements of length n!")
        word_count = 0
        for i in range(n-1):
            word_count += ntotalCounts[n_length_list[i]]
        return math.log(word_count + vocab_size) - math.log(ngramsCounts[(tuple(n_length_list))] + 1) 

    def ngramFindNextWord(text_input):
        if len(text_input) != n-1:
            print(text_input)
            raise Exception("Need to input list of elements of length n-1!")
        min_cost = float("inf")
        best_fit = ''
        for word in set(ntotalCounts):
            if ngramModel(text_input + [word]) < min_cost:
                min_cost = ngramModel(text_input + [word])
                best_fit = word
        return best_fit

    return ngramFindNextWord


