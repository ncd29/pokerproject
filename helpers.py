""" Helper functions file for pokerparse.py """

# start helper functions
"""
unless x is a number or a '.' return the string up until that character
@param - s: the string 
not sure if needed
"""
def removeEndSpaces(s):
    for x in s:
        if x != "0" and x!= "1" and  x != "2" and    x != "3"  and x != "4" and x != "5" and x!= "6"  and x != "7"    and x != "8"    and x != "9" and x!= ".":
            index = s.find(x)
            s = s[0:index]
    return s 

"""
removes the commas that are placed in the text file for numbers larger than 1000
assume input is a number
@param - s: the string with a comma in it, to be converted to float
returns - a float representing the money amount
"""
def removeCommas(s):
    comma = s.find(",")
    if comma == -1:
        return float(s)
    else:
        beforeComma = s[:comma]
        afterComma = s[comma+1:]
        try:
            retVal = float(beforeComma+afterComma)
        except:
            retVal = float(beforeComma+afterComma[:3])
        return retVal
"""
gets the position (BB,UTG,HJ, etc.) give the number of players and the counter from button
@param - counter: number of positions from button 0 = button
@param - n: number of players in the hand
the position described as a string
"""
def getPosition(counter,n):
    if n == 2:
        if counter == 0:
            return "D/SB"
        else:
            return "BB"
    else:
        if counter == 0:
            return "D"
        elif counter == 1:
            return "SB"
        elif counter == 2:
            return "BB"
        else:
            if n == 4:
                return "CU"
            elif n == 5:
                if counter == 3:
                    return "HJ"
                else:
                    return "CU"
            elif n == 6:
                if counter == 3:
                    return "UTG"
                elif counter == 4:
                    return "HJ"
                else:
                    return "CU"
            elif n == 7:
                if counter == 3:
                    return "UTG"
                elif counter == 4:
                    return "UTG+1"
                elif counter == 5:
                    return "HJ"
                else:
                    return "CU"
            elif n == 8:
                if counter == 3:
                    return "UTG"
                elif counter == 4:
                    return "UTG+1"
                elif counter == 5:
                    return "UTG+2"
                elif counter == 6:
                    return "HJ"
                else:
                    return "CU"
            else:
                if counter == 3:
                    return "UTG"
                elif counter == 4:
                    return "UTG+1"
                elif counter == 5:
                    return "UTG+2"
                elif counter == 6:
                    return "UTG+3"
                elif counter == 7:
                    return "HJ"
                else:
                    return "CU"

""" 
returns the keyword used by this website to specify which 
keyword to use to determine when preflop starts, i.e. HOLE CARDS
@param: website
"""
def getPreflopKeyword(website):
    keyword = ""
    if website == "ABS":
        keyword = "* POCKET CARDS *"
    if website == "FTP":
        keyword = "HOLE CARDS"
    if website == "ONG":
        keyword = "pocket cards"
    if website == "PTY":
        keyword = "down cards"
    if website == "PS":
        keyword = "HOLE CARDS"
    return keyword

""" 
returns the keyword used by this website to specify which 
keyword to use to determine when flop starts, i.e. HOLE CARDS
@param: website
"""
def getFlopKeyword(website):
    keyword = ""
    if website == "ONG":
        keyword = "flop"
    elif website == "PTY":
        keyword = "Flop"
    else:
        keyword = "FLOP"
    return keyword

""" 
returns the keyword used by this website to specify which 
keyword to use to determine when turn starts, i.e. HOLE CARDS
@param: website
"""
def getTurnKeyword(website):
    keyword = ""
    if website == "ONG":
        keyword = "turn"
    elif website == "PTY":
        keyword = "Turn"
    else:
        keyword = "TURN"
    return keyword

""" 
returns the keyword used by this website to specify which 
keyword to use to determine when river starts, i.e. HOLE CARDS
@param: website
"""
def getRiverKeyword(website):
    keyword = ""
    if website == "ONG":
        keyword = "river"
    elif website == "PTY":
        keyword = "River"
    else:
        keyword = "RIVER"
    return keyword

def getShowdownKeyword(website):
    if website == "ONG":
        return "Summary"
    elif website == "FTP" or website == "PS":
        return "SUMMARY"
    elif website == "PTY":
        return "wins"
    else:
        return "SHOW DOWN"

def getCollectsKeyword(website):
    if website == "ABS":
        return "Collects"
    if website == "PS":
        return "collected"
    if website == "PTY" or website == "FTP":
        return "wins"
    if website == "ONG":
        return "won"

""" 
given a string and website returns true or false 
to determine if a new hand has started and if it is
time to insert into database
@param: website
@param: s - the string
"""
def getNewHandKeyword(website,s):
    if website == "ABS":
        return s[0:5] == "Stage"
    if website == "FTP":
        return s[0:4] == "Full"
    if website == "ONG":
        return s[6:13] == "History"
    if website == "PTY":
        return s[0:4] == "Game"
    if website == "PS":
        return s[0:5] == "Poker"

"""
given the website and a line, returns the hand id for that website
@param: website
@param: s 
"""
def getHandId(website,s):
    handId = ""
    if website == "ABS" or website == "FTP" or website == "PS":
        pound = s.find("#") 
        colon = s.find(":") # make sure this finds the first colon
        handId = s[pound + 1: colon]
    if website == "ONG":
        subStr = s[5:]
        R = subStr.find("R")
        star = subStr.find("*")
        handId = subStr[R:star-1]
    if website == "PTY":
        pound = s.find("#")
        letterS = s.find("s")
        handId = s[pound:letterS-1]
    return handId

"""
Returns true if the given conditions are correct for getting the button from the text
"""
def buttonCondition(website,s):
    if website == "ABS" or website == "PS":
        return s[0:5] == "Table"
    if website == "FTP":
        return s[4:10] == "button"
    if website == "ONG":
        return s[0:6] == "Button"
    if website == "PTY":
        return s[14:20] == "button"

"""
Returns the seat number of the dealer using the correct method
"""
def getButton(website,s):
    button = " "
    if website == "ABS" or website == "FTP" or website == "PS":
        pound = s.find("#")
        button = s[pound+1:pound+2]
    if website == "ONG":
        button = s[13:]
    if website == "PTY":
        button = s[5]
    return button

"""
Returns true if conditions are met for finding a username in this line
"""
def usernameCondition(website,s):
    if website == "ABS":
        return s[0:4] == "Seat" and s.find("-") != -1 and s.find(":") == -1
    else:
        return s[0:4] == "Seat" and s.find(":") != -1








