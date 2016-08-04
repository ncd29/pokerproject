import sys
sys.path.insert(0,'../') # moves directory back one for testing
from pokerparse import *
from helpers import * 
""" Testing file for pokerparse.py and helpers.py """
# CURRENTLY PASSES

def testParseText():
	file1 = "../handhistories/ABS200NL/abs NLH handhq_1-OBFUSCATED.txt"
	parseText(file1)

# add more tests 
def testRemoveCommas():
	s1 = "123"
	s2 = "1,234.32"
	if removeCommas(s1) != 123.0:
		print "removeCommas failed"
		return 0
	if removeCommas(s2) != 1234.32:
		print "removeCommas failed"
		return 0
	return 1

def testGetPosition():
	p1 = getPosition(0,4)
	p2 = getPosition(1,5)
	p3 = getPosition(2,6)
	p4 = getPosition(4,7)
	p5 = getPosition(7,9)
	if p1 != "D" or p2 != "SB" or p3 != "BB" or p4 != "UTG+1" or p5 != "HJ":
		print "getPosition failed"
		return 0
	return 1

def main():
	print "Starting Tests"

	correct = 0
	totalTests = 2

	correct += testRemoveCommas()
	correct += testGetPosition()
	testParseText()

	print "Passed " + str(correct) + " out of " + str(totalTests) + " tests."

# start script with a call to main
main()