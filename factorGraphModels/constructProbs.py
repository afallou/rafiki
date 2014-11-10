import re
import token
import tokenize
import io



class NormalizingDict:
  """
  	Warning: incomplete dict interface! May fix later
  """
  def __init__(self, python_dict={}, sum_fn=sum):
  	self.sum_fn = sum_fn
    self.store = python_dict
  
  def __setitem__(self, key, value):
  	# values should be floats if you didn't provide a special sum_fn
    self.store[key] = value

  def __getitem__(self, key):
  	return self.store[key] / self.sum_fn(self.store.values())

  def __contains__(self, key):
  	return key in self.store

"""
	Return:
		transProb such that transProb[w0][sep][w1] gives you the count 
"""
class TransitionProbsBuilder:
 	# we're going to treat every thing other than name, string, number as a separator

 	def __init__():
 		self.transProb = {}

	def updateTransitionProbs(dirpath):
		with open(dirpath,'r') as f:
    		content=f.read()
			g = tokenize.generate_tokens(io.BytesIO(content).readline) 
			prev_non_sep_tok = None
			prev_sep = None # this is the separator that comes after prev_non_sep_tok
			for toknum, tokval, _, _, _  in g:
				# we see a token that is not a separator
				if toknum != token.NAME and toknum != token.NUMBER and toknum != token.STRING:
					if prev_non_sep_tok != None and prev_sep != None:
						if prev_non_sep_tok in self.transProb:
							if prev_sep in self.transProb[prev_non_sep_tok]:
								if toknum in self.transProb[prev_non_sep_tok][prev_sep]:
									self.transProb[prev_non_sep_tok][prev_sep][toknum] +=1
								else:
									self.transProb[prev_non_sep_tok][prev_sep][toknum] = 1
							else:
								self.transProb[prev_non_sep_tok][prev_sep] = NormalizingDict({toknum: 1})

						else:
							self.transProb[prev_non_sep_tok] = {prev_sep: NormalizingDict({toknum: 1})}
					prev_non_sep_tok = toknum 
					prev_sep = None
				else: # we see a token that is a separator 
					if prev_non_sep_tok != None:
						prev_sep = toknum # can we have two separators in a row? in that case we'll take the last, which may not be the right thing to do....

	def build():
		return self.transProb 


	
