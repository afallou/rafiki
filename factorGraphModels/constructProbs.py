import re

"""
	Return:
		transProb such that transProb[w0][sep][w1]
"""

class TransitionProbsBuilder:
	MULTI_COMMENT = "\"\"\""
	multi_comment_re = (re.compile('(%s.*?%s)' % 
		(re.escape(MULTI_COMMENT), re.escape(MULTI_COMMENT))))
	COMMENT = "#"
	DEFAULT_3_SEPARATORS = 
	DEFAULT_2_SEPARATORS = [
	 '==', 
	 '+=',
	 '-=',
	 '*=',
	 '/=',
	 '%=',
	 '&=',
	 '|=',
	 '^=',
	 
            '<<=' | '>>=' | '**=' | '//=']
	DEFAULT_1_SEPARATORS = [
	 ' ',
	 '\n', 
	 '\t', 
	 ':', 
	 '.',
	 ',', 
	 '=', 
	 '',
	 '(',
	 ')',
	 '[',
	 ']',
	 '{',
	 '}',
	 ''] 

	# TODO: ideally we'd also strip out string literals 
	# although it seems like this would entail looking at the text 
	# char by char...(and sometimes 2 or 3 at a time, for +=, """ etc.)

	def __init__(separators=DEFAULT_SEPARATORS):
		self.separators = separators
		self.inComment = False
		self.inString = False

	def updateTransitionProbs(dirpath):



	def build():

	
