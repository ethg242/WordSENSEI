from re import split
import math

from utils import *

try:
	if argv[1] == "-v":
		setLogVerbosity(int(argv[2]))
except (IndexError, ValueError):
	pass


# algD: Variant of algA using idf - Inverse Document Frequency
def algD(context, word):
	context = getDistinct(context)
	
	log('Starting "%s" in context %s.' %(word, context), 2)
	
	# Get word senses
	senseURIs = querySenses(word)
	log('Got senses of word: %s.' %(str(senseURIs)), 4)
	
	allAbstracts = {} # { senseURI: [ keywords ] }
	
	# Get all abstracts
	for senseURI in senseURIs:
		allAbstracts[senseURI] = tokenize(queryAbstract(senseURI))
		senseName = senseURI.rsplit("/", 1)[-1]
		log('Got abstract for sense %s.' %(senseName), 3)
	
	documentFreqs = {}
	
	# Loop through all abstracts for the first time: count total and document frequencies
	for senseURI,keywords in allAbstracts.iteritems():
		# Loop through abstract
		for word in getDistinct(keywords):
			# Increment count in total frequencies
			if word not in documentFreqs:
				documentFreqs[word] = 1
			else:
				documentFreqs[word] += 1
	
	wsenses = []
	
	# Loop through all senses a second time: actually check
	for senseURI in senseURIs:
		senseName = senseURI.rsplit("/", 1)[-1]
		
		log('Checking sense "%s".' %(senseName), 3)
		
		keywords = []
		
		# Get idf
		for word in getDistinct(allAbstracts[senseURI]):
			idf = math.log(float(len(senseURIs)) / documentFreqs[word])
			keywords.append( (word, idf) )
		
		log('Got keywords.', 4)
		
		# Remove duplicate terms from the keywords
		keywords = getDistinct(keywords)
		
		# Check keywords, calculate the weight
		weight = 0
		for keyword in keywords:
			if keyword[0] in context:
				weight += keyword[1]
		
		log('Finished checking weights.', 4)
		
		# Catalogue the sense:weight
		wsenses.append( (senseName, weight, senseURI) )
		
		log('Done checking sense at weight %d.' %(weight), 3)
	
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
	
	wsenses = algD(textWords, word)
	
	print
	
	if wsenses:
		best = (None, -1, None)
		# Output sense and weight while finding best sense
		for wsense in wsenses:
			sense, weight = wsense[0], wsense[1]
			if logVerbosity >= 3:
				print sense, ":", weight
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
	startLogging("algD.log")