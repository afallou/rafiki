import random

# Randomly select nwords in test_data list and predict the following word
def modelRandomTesting(test_data, model, nwords=10000, n=2):
    # test_data: test text, as a list of word
    # model: ngram model
    # nwords: number of randomly selected words
    # n: ngram length
    positive_count = 0
    selected_words = random.sample(xrange(len(test_data)), nwords)
    for i in xrange(nwords):
        ngram_begin = []
        for j in xrange(n - 1):
            index = selected_words[i] + j
            ngram_begin.append(test_data[index])
        prediction = model(ngram_begin)
        truth = test_data[i + n - 1]
        if truth == prediction:
            positive_count += 1
    success_rate = positive_count / nwords
    print "Success rate:", success_rate
    return success_rate

