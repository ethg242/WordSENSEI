from sys import argv
from re import split
from time import sleep
from urllib2 import HTTPError
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

logVerbosity = 3    # Default: 3
					# 0 - No logging
					# 1 - Warnings/problems only
					# 2 - Breakpoints
					# 3 - Informative
					# 4 - All operations

logFile = None
interactiveMode = False

def startLogging(file=False):
	if file:
		global logFile
		logFile = open(file, "a")
	else:
		global interactiveMode
		interactiveMode = True

def setLogVerbosity(verbosity):
	global logVerbosity
	logVerbosity = verbosity

def log(msg, verbosity=4):
	if verbosity <= logVerbosity:
		if interactiveMode:
			print msg
		else:
			logFile.write("[%d] %s\n" %(verbosity, msg) )

def getDistinct(l):
	distinct = []
	for i in l:
		if i != "" and i not in distinct:
			distinct.append(i)
	return distinct

def tokenize(text):
	return split("\W+", text.lower())

def querySenses(word):
	sparql.setQuery("""
		PREFIX dbo: <http://dbpedia.org/ontology/>

		SELECT ?disambiguation WHERE {
			{ <http://dbpedia.org/resource/%(w)s_(disambiguation)> dbo:wikiPageDisambiguates ?disambiguation . }
			UNION
			{ <http://dbpedia.org/resource/%(w)s> dbo:wikiPageDisambiguates ?disambiguation . }
		}
	""" %{"w":word.title()} )
	
	results = None
	retries = 0
	while results == None and retries < 5:
		try:
			results = sparql.query()
		except HTTPError:
			sleep(30)
			log("Got an HTTP Error while querying for senses. Retrying in 30 seconds.", 1)
			retries += 1
	
	results = results.convert()
	
	senses = []
	for result in results["results"]["bindings"]:
		disamb = result["disambiguation"]["value"]
		senses.append(disamb)
	return senses

def queryAbstract(uri):
	sparql.setQuery("""
		PREFIX dbo: <http://dbpedia.org/ontology/>

		SELECT ?abstract WHERE {
			<%s> dbo:abstract ?abstract .
			FILTER(langMatches(lang(?abstract), "en")) .
		}
	""" %(uri) )
	
	results = None
	retries = 0
	while results == None and retries < 5:
		try:
			results = sparql.query()
		except HTTPError:
			sleep(30)
			log("Got an HTTP Error while querying for the abstract. Retrying in 30 seconds.", 2)
			retries += 1
	
	results = results.convert()
	
	try:
		abstract = results["results"]["bindings"][0]["abstract"]["value"]
	except IndexError:
		abstract = ""
	return abstract

def queryImage(uri):
	sparql.setQuery("""
		PREFIX foaf: <http://xmlns.com/foaf/0.1/>

		SELECT ?depiction WHERE {
			<%s> foaf:depiction ?depiction .
		}
	""" %(uri) )
	
	results = None
	retries = 0
	while results == None and retries < 5:
		try:
			results = sparql.query()
		except HTTPError:
			sleep(30)
			log("Got an HTTP Error while querying for images. Retrying in 30 seconds.", 4)
			retries += 1
	
	results = results.convert()
	
	try:
		image = results["results"]["bindings"][0]["depiction"]["value"]
	except IndexError:
		image = None
	return image

def queryInLinkCount(uri):
	sparql.setQuery("""
		PREFIX dbo: <http://dbpedia.org/ontology/>

		SELECT ?inlinkcount WHERE {
			<%s> dbo:wikiPageInLinkCount ?inlinkcount .
		}
	""" %(uri) )
	
	results = None
	retries = 0
	while results == None and retries < 5:
		try:
			results = sparql.query()
		except HTTPError:
			sleep(30)
			log("Got an HTTP Error while querying for images. Retrying in 30 seconds.", 4)
			retries += 1
	
	results = results.convert()
	
	try:
		inLinkCount = results["results"]["bindings"][0]["inlinkcount"]["value"]
	except IndexError:
		inLinkCount = None
	return inLinkCount
