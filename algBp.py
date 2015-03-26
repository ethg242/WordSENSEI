from re import split
import math

from utils import *

try:
	if argv[1] == "-v":
		setLogVerbosity(int(argv[2]))
except (IndexError, ValueError):
	pass


# algBp: Variant of algB using adjusted tf
def algBp(context, word):
	context = getDistinct(context)
	
	log('Starting "%s" in context %s.' %(word, context), 2)
	
	# Get word senses
	senseURIs = querySenses(word)
	log('Got senses of word: %s.' %(str(senseURIs)), 4)
	
	wsenses = []
	
	# Check each sense
	for senseURI in senseURIs:
		senseName = senseURI.rsplit("/", 1)[-1]
		
		log('Checking sense "%s".' %(senseName), 3)
		
		# Construct list of keywords to search
		keywords = tokenize(queryAbstract(senseURI))
		
		log('Got keywords.', 4)
		
		# Remove duplicate terms from the keywords
		keywords = getDistinct(keywords)
		
		# Check keywords, calculate the weight
		weight = 0
		for keyword in keywords:
			if keyword in context:
				weight += 1
		
		totalKeywords = len(keywords)
		
		adjTf = 0
		# As long as weight isn't 0*, divide weight by the total number of keywords to get adjusted weight
		#     *signifying no keywords or just no matches; either way adjTf should be 0 as per above
		if weight != 0:
			adjTf = weight / float(totalKeywords) * math.log(totalKeywords)
		
		log('Finished checking weights.', 4)
		
		# Catalogue the sense:weight
		wsenses.append( (senseName, adjTf, senseURI) )
		
		log('Done checking sense at weight %.4f (%d/%d).' %(adjTf, weight, totalKeywords), 3)
	
	return wsenses


# Enter interactive session if run directly
if __name__ == "__main__":
	startLogging()
	
	# Get inputs
	text = raw_input("Enter a text: ")
	word = raw_input("Enter a word in that text: ")
	
	print
	
	# Format input text
	textWords = split("\W+", text.lower())
	
	wsenses = algBp(textWords, word)
	
	print
	
	if wsenses:
		best = (None, -1, None)
		# Output sense and weight while finding best sense
		for wsense in wsenses:
			sense, weight = wsense[0], wsense[1]
			if logVerbosity >= 3:
				print "%s:%.2f%%" %(sense, weight*100)
			if weight >= best[1]:
				best = wsense
		
		# Output best sense
		print
		log("Best sense: %s at %.8f" %(best[0], best[1]), 2)
		print "\n---\n"
		
		raw_input("Press Enter for additional information...")
		
		print "\nAbstract:"
		try:
			print queryAbstract(best[2])
		except UnicodeEncodeError:
			print "Your console does not support Unicode."
		
		print "\nFetching image..."
		
		imgURL = queryImage(best[2])
		
		try:
			from webbrowser import open
			open(imgURL)
		except TypeError:
			print "Image not available."
		
	else:
		print "Word not found."
else:
	startLogging("algBp.log")