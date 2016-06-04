#!/usr/bin/env python
# coding: utf-8

from lxml import html # Has to be installed
import codecs
import os.path
import sys
from optparse import OptionParser

HELPTEXT = "%s <options>" % os.path.normpath(sys.argv[0])
LINEART = '=' * 80
LINESEND = '-' * 50
LS = "\r\n"

def getEscapedFilename(aFile):
	res = os.path.normpath(aFile.strip())
	return res

def sortComment(aComment):
	listXpath = aComment.xpath("div/div/span[@class='dateauthor']/text()")
	if len(listXpath) == 0:
		return ''
	else:
		# Asterisk (*) in "format ..." unpacks sequence
		return "{4}{3}{2}{0}{1}".format(*listXpath[0].replace(':',' ').replace('.',' ').split())

def parseFile(aFile):
	cleanFile = getEscapedFilename(aFile)
	inFile = None
	try:
		inFile = open( cleanFile, 'rb' )
	except:
		if inFile:
			inFile.close()
		print sys.exc_info()
		print( "(E) Error parsing file '%s', skipping ..." % cleanFile )
		return
	tree = html.parse(inFile)
	filePath = cleanFile.split('/')
	OPTIONS.outputFile.write( LINEART + LS )
	newStr = "Blog: http://blog.b92.net/".encode('utf-8') + "/".join(filePath[-4:])
	OPTIONS.outputFile.write( newStr.decode('utf-8') + LS )
	
	# find blog date
	blogDates = tree.xpath("//span[@class='date']")
	if len(blogDates) == 1:
		OPTIONS.outputFile.write( "Date: " + blogDates[0].text_content() + LS )
		
	# article
	articles = tree.xpath("//div[contains(@class, 'blog-text')]")
	for article in articles:
		OPTIONS.outputFile.write( LINESEND + LS )
		newStr = ' '.join(article.text_content().split())
		try:
			OPTIONS.outputFile.write( newStr + LS )
		except UnicodeEncodeError:
			OPTIONS.outputFile.write( newStr + LS )
	# Comments
	comments = tree.xpath("//div[contains(@class, 'komentar-outer')]")
	for comment in sorted(comments, key=sortComment):
		newStr = ' '.join(comment[0].text_content().split()).encode('utf-8')
		# Find author within comment
		if newStr.find( OPTIONS.author ) > -1:
			OPTIONS.outputFile.write( LINESEND + LS )
			OPTIONS.outputFile.write( newStr.decode('utf-8') + LS )
	inFile.close()
	

if __name__ == "__main__":
	global OPTIONS
	
	parser = OptionParser(usage=HELPTEXT)
	parser.add_option("-a", "--author", action="store", type="string", dest="author", default=None,
		help="Blog author on B92")
	parser.add_option("-i", "--input-file", action="store", type="string", dest="inputFile", default=None,
		help="Input file containing list of files to search (one per line)")
	parser.add_option("-o", "--output-file", action="store", type="string", dest="outputFile", default='out.txt',
		help="Output file, containing all posts from given author")
	(OPTIONS, args) = parser.parse_args()
	
	# Check number of arguments
	if not OPTIONS.inputFile:
		parser.error( 'Input file must be specified.' )
	if not OPTIONS.author:
		parser.error( 'Blog author must be specified' )
	
	# Open out file for writing
	try:
		OPTIONS.outputFile = codecs.open( OPTIONS.outputFile, "w", 'utf-8' )
	except IOError:
		print( "(E) Unable to open for output, exiting ..." )
		sys.exit(2)
				
	with open( OPTIONS.inputFile, 'r' ) as inputFile:
		inputLines = inputFile.readlines()
		for blogFile in inputLines:
			parseFile( blogFile )
		print( 'Processed %d files' % len(inputLines) )
	
	OPTIONS.outputFile.close()

