from sys import argv
import _mysql

# get the file name from the argument and open it
script, filename = argv

f = open(filename)

for line in f:
	print(line)
	if "POCKET CARDS" in line:
		break