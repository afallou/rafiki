from constructProbs import getSeparatorAndToken
import tokenize
import unittest
import io

class TestConstructProbs(unittest.TestCase):
    

    def setUp(self):
        pass

    def test_get_short_sequence(self):
        contents = "a b"
        g = tokenize.generate_tokens(io.BytesIO(contents).readline)
        results = [pair for pair in getSeparatorAndToken(g, 1, train=False)]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], None)
        self.assertEqual(results[0][1].getName(), 'a')
        self.assertEqual(results[1][0], ' ')
        self.assertEqual(results[1][1].getName(), 'b')

    def test_get_long_sequence(self):
        pass # broken test
        # f = open("celery_small_test/gevent.py")
        # contents = f.read()
        # g = tokenize.generate_tokens(io.BytesIO(contents).readline)
        # for lineno in xrange(1,100):
         #    results = [pair for pair in getSeparatorAndToken(g, lineno, train=False)]
          #   print results
        # self.assertEqual(len(results), 3)


if __name__ == '__main__':
    unittest.main()
