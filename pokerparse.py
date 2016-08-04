''' 
This file parses through all of the text files in each hand history directory and organizes the
gathered data correctly to input it into MySQL localhost database
'''
# DONEZO:
# - ABS done except for noted files

# TODO:
# - make it so that it will run through all files in all directories
#   - or one directory at a time
# - FTP and other sites have different ways of storing text files, fix it
# - bug on hand_id 3017238460 all in on turn, but river not stored,
#   - might be because I move to showdown right away if someone is all in
# - not sure what to do about IPN because text file structure is complicated
# - add stake as parameter when calling function - get from file name
# - test other websites, script done, but will probably have to debug a few things


# Differences for other websites as compared to ABS directories
# *** FTP ***
# - preflop starts with HOLE CARDS instead of POCKET CARDS
# - new hand starts with Full Tilt Poker Game instead of Stage
# - dealer is specified after the seats and is referred to as "button" instead
# - raises are specified by total amount 
#   - instead of "raises $3 to $3, simply raises to $3"
# - there is no "SHOW DOWN", winner is declared right after the River
# *** IPN ***
# - pretty much everything
# *** ONG ***
# - new hand starts with "History for hand ..."
# - stakes info is in line 3, button line 4, players in round 5
# - says "dealing pocket cards, flop etc." instead of just POCKET CARDS
# - HANDS ARE SHOWN for winner even when no showdown, shown after summary
# - end of hand declared
# *** PS ***
# - differences are similar to FTP except for the last 3 bullets
# *** PTY ***
# - a lot of subtle differences, especially in terms of spacing

from sys import argv
import helpers
import mysql.connector
import os

# CONSTANTS
PREFLOP = 1
FLOP = 2
TURN = 3
RIVER = 4
SHOWDOWN = 5
SKIP = 6
BROKENHANDSLIST = ['3064055628','3064056406','3067576442']
# this specifies the website that the hands are from, because each
# website stores the hand histories differently
WEBSITE = "ABS"
# list of directories to parse
dirs = []
ABS100PATH = "handhistories/ABS100NL/" # text files that broke: 238  
ABS200PATH = "handhistories/ABS200NL/" # TODO: 54, 245, 246
ABS400PATH = "handhistories/ABS400NL/" # TODO 33,137
ABS600PATH = "handhistories/ABS600NL/" # DONE
dirs.append(ABS100PATH)
dirs.append(ABS200PATH)
dirs.append(ABS400PATH)
dirs.append(ABS600PATH)

# connect to the database
DB = mysql.connector.connect(user='root',password='root',host='localhost',database='Poker',
    unix_socket="/Applications/MAMP/tmp/mysql/mysql.sock")

""" 
main function that parses the text files and inserts into the database
@param: filename - the file to parse
@param: website - the specification as a string of which website the hands 
are from, because each hand history files are different 
@param: stake - the limits of the files
"""
def parseText(filename,website,stake):
    f = open(filename)
    # TODO: handle all the website specific things here 
    seats = []
    usernames = []
    startingamounts = []
    amountLost = []

    # stores the current location (preflop,flop,turn,river) of the hand
    # if hand history has not reached that part yet, 0
    currentlocation = 0

    # number of players that were dealt in hand
    numplayers = 0

    # stores all the actions
    preflopActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
    flopActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
    turnActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
    riverActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]

    cards = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
    flop = ""
    turn = ""
    river = ""
    numHands = 0
    for line in f:
        # string of line
        s = str(line)
        # print s

        # ends the hand
        # not sure if need to change something here for other sites
        if getShowdownKeyword(WEBSITE) in s:
            currentlocation = SHOWDOWN
        # hardcode to avoid double counting won amount in PS
        if WEBSITE == "PS" and "Rake" in s:
            currentlocation = SKIP
        # checks if this is the first line of a hand 
        # gets big blind amount and handid
        # new hand, clear data structures
        if getNewHandKeyword(WEBSITE,s):
            # for i in range(0,numplayers):
            #     print "user " + str(usernames[i]) + " sat in seat " + str(seats[i]) + " ,started with " + str(startingamounts[i]) + " and won " + str(-1*amountLost[i]) 
            # TODO: add SQL insert statements
            cursor = DB.cursor()

            # insert into hands table
            if numHands > 0:
                # insert ignore so it doesn't fail on duplicates
                query = ("INSERT IGNORE INTO hands "
                    "(hand_id, big_blind, num_players, seat_1,seat_2,seat_3,seat_4,seat_5,seat_6,seat_7,seat_8,seat_9,dealer,flop,turn,river) "
                    "VALUES (%(hand_id)s, %(big_blind)s, %(num_players)s, %(seat_one)s, %(seat_two)s, %(seat_three)s, %(seat_four)s, %(seat_five)s, %(seat_six)s, %(seat_seven)s, %(seat_eight)s, %(seat_nine)s, %(dealer)s, %(flop)s, %(turn)s, %(river)s)")
                seatsToInsert = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                for i in range(1,10):
                    # in a try except because seats is not always of length 9, but be careful
                    # because this may fail to catch errors 
                    try:
                        index = seats[i-1]
                        seatsToInsert[index-1] = usernames[i-1]
                    except:
                        pass
 
                queryData = {
                    'hand_id': handId,
                    'big_blind': bigBlind,
                    'num_players': numplayers,
                    'seat_one': seatsToInsert[0],
                    'seat_two': seatsToInsert[1],
                    'seat_three': seatsToInsert[2],
                    'seat_four': seatsToInsert[3],
                    'seat_five': seatsToInsert[4],
                    'seat_six': seatsToInsert[5],
                    'seat_seven': seatsToInsert[6],
                    'seat_eight': seatsToInsert[7],
                    'seat_nine': seatsToInsert[8],
                    'dealer': dealer,
                    'flop': flop,
                    'turn': turn,
                    'river': river,
                }

                cursor.execute(query,queryData)

                # TODO: insert into hand_action
                counter = 0
                for i in range(1,10):
                    try:
                        # if this fails, no one in this seat
                        seat = seats[i-1]
                        position = getPosition(counter,numplayers)
                        startingAmount = startingamounts[i-1]
                        holeCards = cards[i-1]
                        preflopAction = preflopActions[i-1]
                        flopAction = flopActions[i-1]
                        turnAction = turnActions[i-1]
                        riverAction = riverActions[i-1]
                        profit = (-1*amountLost[i-1])

                        actionsQuery = ("INSERT INTO hand_action "
                                        "(hand_id,seat,position,starting_amount,cards,preflop_action,flop_action,turn_action,river_action,profit) "
                                        "VALUES (%(hand_id)s, %(seat)s, %(position)s, %(starting_amount)s, %(cards)s, %(preflop_action)s, %(flop_action)s, %(turn_action)s, %(river_action)s, %(profit)s)")
                        
                        actionsQueryData = {
                            'hand_id': handId,
                            'seat': seat,
                            'position': position,
                            'starting_amount': startingAmount,
                            'cards': holeCards,
                            'preflop_action': preflopAction,
                            'flop_action': flopAction,
                            'turn_action': turnAction,
                            'river_action': riverAction,
                            'profit': profit,
                        }

                        cursor.execute(actionsQuery,actionsQueryData)
                    except:
                        pass
                        # print "Query failed"
                    counter += 1

                # TODO: insert into players
                for username in usernames:
                    playersQuery = ("INSERT IGNORE INTO players "
                                   "(USER_ID) "
                                   "VALUES (%(username)s)")

                    playersQueryData = {
                        'username': username,
                    }

                    cursor.execute(playersQuery,playersQueryData)

                DB.commit()

            # reset data structures
            seats = []
            usernames = []
            startingamounts = []
            amountLost = [] # positive means won, negative means lost
            currentlocation = 0
            numplayers = 0
            preflopActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
            flopActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
            turnActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
            riverActions = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
            cards = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
            flop = ""
            turn = "" 
            river = ""

            # if statement for how many hands/insert to print for testing
            # if numHands == 11:
              #  break
            # print "Starting New Hand"
            numHands += 1
            handId = getHandId(WEBSITE,s)
            # can just get the big blind from the directory
            bigBlind = float(stake/100)
        if handId in BROKENHANDSLIST:
            currentlocation = SKIP
        # store broken handIds in list, if it's in this list, try except until new hand id is found
        if buttonCondition(WEBSITE,s): # gets dealer's seat
            dealer = getButton(WEBSITE,s)
        if usernameCondition(WEBSITE,s) and (currentlocation != SKIP or WEBSITE == "PS") and currentlocation != SHOWDOWN: 
            # gets the seats
            seats.append(int(s[5]))
            # gets the username for the player
            index = s.find("-") 
            if index == -1:
                index = s.find(":")
            username = s[index + 2: index + 24]
            usernames.append(username)

            # gets starting chips for each player
            dollar = s.find("$")
            # this means money > 1000
            # print s
            if "," in s:
                money = removeCommas(s[dollar+1:dollar+9])
            else:
                money = s[dollar + 1: dollar + 7]
                if money.find(".") == -1:
                    money = money[:3]
                    try:
                        if float(money) < 100:
                            money = money[:2]
                    except:
                        money = money[:1]
                money = removeEndSpaces(money)
            # print money 
            money = float(money)
            # print money
            startingamounts.append(money)

            # increment the number of players
            numplayers += 1
            # add to amount lost
            amountLost.append(0.0)
        # will have to double check antes for other sites
        if "Ante" in s and "Stage" not in s:
            username = s[0:22]
            dollar = s.find("$")
            amount = float(s[dollar+1:len(s)])
            try:
                position = usernames.index(username)
                amountLost[position] += amount
            except:
                pass
        # gets the small blind and big blind
        if "Posts" in s:
            username = s[0:22]
            # need to do this if a player posts big blind but wasn't actually in 
            # the hand, doesn't factor into losses
            try:
                position = usernames.index(username)
                dollar = s.find("$")
                s2 = s[dollar+1:]
                # the index to stop after the dollar sign
                stopIndex = s2.find(" ")
                if WEBSITE == "ONG":
                    stopIndex = s2.find(")")
                if "dead" in s:
                    amount = removeCommas(s[dollar+1:dollar+1+stopIndex])
                else:
                    if stopIndex == -1:
                        amount = removeCommas(s[dollar+1:])
                    else:
                        amount = removeCommas(s[dollar+1:dollar+1+stopIndex])
                    # print amount
                amountLost[position] += amount
            except:
                pass
        if getPreflopKeyword(WEBSITE) in s:
            currentlocation = PREFLOP
        # get the preflop actions and store them correctly
        if currentlocation == PREFLOP and getPreflopKeyword(WEBSITE) not in s:
            # print "preflop"
            if getFlopKeyword(WEBSITE) not in s:
                username = s[0:22]
                if WEBSITE == "ABS":
                    dash = s.find("-")
                else:
                    dash = s.find(" ")
                action = s[dash+1:len(s)]
                try:
                    position = usernames.index(username)
                    # since multiple actions can be taken need to append the string
                    if preflopActions[position] == "N/A":
                        preflopActions[position] = action
                    else:
                        temp = preflopActions[position]
                        temp2 = temp + " "
                        # extra checks for FTP text files
                        if action.find("$") != -1 or "folds" in action or "checks" in action:
                            preflopActions[position] = temp2 + str(action)
                    dollar = s.find("$")
                    if dollar != -1 and "returned" not in s: #this means a call or raise was made 
                        dollar = s.find("$")
                        s2 = s[dollar+1:]
                        space = s2.find(" ")
                        # if space not found, money goes until end of line
                        if space == -1:
                            space = len(s) - dollar - 1
                        amount = removeCommas(s[dollar+1:dollar+1+space])
                        amountLost[position] += amount 
                except:
                    pass
            else:
                # get the flop
                currentlocation = FLOP
                leftBracket = s.find("[")
                rightBracket = s.find("]")
                flop = s[leftBracket+1:rightBracket]
                # print "after flop, flop is " + flop
        # get the flop actions and store them correctly
        if currentlocation == FLOP and getFlopKeyword(WEBSITE) not in s:
            if getTurnKeyword(WEBSITE) not in s:
                username = s[0:22]
                if WEBSITE == "ABS":
                    dash = s.find("-")
                else:
                    dash = s.find(" ")
                action = s[dash+1:len(s)]
                try:
                    position = usernames.index(username)
                    # since multiple actions can be taken need to append the string
                    if flopActions[position] == "N/A":
                        flopActions[position] = action
                    else:
                        temp = flopActions[position]
                        temp2 = temp + " " 
                        if action.find("$") != -1 or "folds" in action or "checks" in action:
                            flopActions[position] = temp2 + str(action)
                    dollar = s.find("$")
                    if dollar != -1 and "returned" not in s: #this means a call or raise was made 
                        s2 = s[dollar+1:]
                        space = s2.find(" ")
                         # if space not found, money goes until end of line
                        if space == -1:
                            space = len(s) - dollar - 1
                        amount = removeCommas(s[dollar+1:dollar+1+space])
                        amountLost[position] += amount 
                except:
                    pass
            else:
                currentlocation = TURN
                rightBracket = s.find("]")
                s2 = s[rightBracket+1:]
                leftBracket = s2.find("[")
                rightBracket2 = s2.find("]")
                turn = s[leftBracket+2+rightBracket:rightBracket+rightBracket2+1]
                if WEBSITE == "ONG" or WEBSITE == "PTY":
                    turn = s[leftBracket+1:rightBracket]
                # print "after turn, turn is " + turn
        # get the turn actions and store them correctly
        if currentlocation == TURN and getTurnKeyword(WEBSITE) not in s:
            if getRiverKeyword(WEBSITE) not in s:
                username = s[0:22]
                if WEBSITE == "ABS":
                    dash = s.find("-")
                else:
                    dash = s.find(" ")
                try:
                    position = usernames.index(username)
                    # since multiple actions can be taken need to append the string
                    if turnActions[position] == "N/A":
                        turnActions[position] = action
                    else:
                        temp = turnActions[position]
                        temp2 = temp + " " 
                        if action.find("$") != -1 or "folds" in action or "checks" in action:
                            turnActions[position] = temp2 + str(action)
                    dollar = s.find("$")
                    if dollar != -1 and "returned" not in s: #this means a call or raise was made 
                        s2 = s[dollar+1:]
                        space = s2.find(" ")
                         # if space not found, money goes until end of line
                        if space == -1:
                            space = len(s) - dollar - 1
                        amount = removeCommas(s[dollar+1:dollar+1+space])
                        amountLost[position] += amount 
                except:
                    pass
            else:
                currentlocation = RIVER
                rightBracket = s.find("]")
                s2 = s[rightBracket+1:]
                leftBracket = s2.find("[")
                rightBracket2 = s2.find("]")
                river = s[leftBracket+2+rightBracket:rightBracket+rightBracket2+1]
                if WEBSITE == "ONG" or WEBSITE == "PTY":
                    river = s[leftBracket+1:rightBracket]
                # print "after river, river is " + river
        # get the river actions and store them correctly
        if currentlocation == RIVER and getRiverKeyword(WEBSITE) not in s:
            if WEBSITE == "PTY" and "shows" in s:
                currentlocation = SHOWDOWN
            else:
                if getShowdownKeyword(WEBSITE) not in s:
                    username = s[0:22]
                    if WEBSITE == "ABS":
                        dash = s.find("-")
                    else:
                        dash = s.find(" ")
                    try:
                        position = usernames.index(username)
                        # since multiple actions can be taken need to append the string
                        if riverActions[position] == "N/A":
                            riverActions[position] = action
                        else:
                            temp = riverActions[position]
                            temp2 = temp + " " 
                            if action.find("$") != -1 or "folds" in action or "checks" in action:
                                riverActions[position] = temp2 + str(action)
                        dollar = s.find("$")
                        if dollar != -1 and "returned" not in s: #this means a call or raise was made 
                            s2 = s[dollar+1:]
                            space = s2.find(" ")
                             # if space not found, money goes until end of line
                            if space == -1:
                                space = len(s) - dollar - 1
                            amount = removeCommas(s[dollar+1:dollar+1+space])
                            amountLost[position] += amount
                    except:
                        pass
                else:
                    currentlocation = SHOWDOWN
        # get the showdown and find the profits made
        if currentlocation == SHOWDOWN and getShowdownKeyword(WEBSITE) not in s:
            if getCollectsKeyword(WEBSITE) in s:

                dollar = s.find("$")
                # if website is ONG, find the second $
                if WEBSITE == "ONG":
                    dollar = s[20:].find("$")
                s2 = s[dollar+1:]
                space = s2.find(" ")
                if WEBSITE == "ONG" or WEBSITE == "FTP":
                    space = ")"
                amountWon = removeCommas(s[dollar+1:dollar+1+space])
                username = s[0:22]
                if WEBSITE == "ONG":
                    y = s.find("y")
                    username = s[y+2:y+24]
                try:
                    position = usernames.index(username)
                    amountLost[position] -= amountWon
                except:
                    pass
        # if at any point there is a "returned" or SHOW DOWN hand is over
        if "returned" in s:
            #print "returned"
            username = s[0:22]
            dollar = s.find("$")
            s2 = s[dollar+1:]
            space = s2.find(" ")
            rightParentheses = s.find(")")
            if WEBSITE == "FTP":
                username = s[-22:]
                rightParentheses = space + dollar + 1
            amountReturned = removeCommas(s[dollar+1:rightParentheses])
            try:
                position = usernames.index(username)
                amountLost[position] -= amountReturned
            except:
                pass
            # end the hand by setting currentlocation to showdown
            currentlocation = SHOWDOWN
        # get the cards
        if WEBSITE != "ONG" and "Shows" in s:
            username = s[0:22]
            leftBracket = s.find("[")
            rightBracket = s.find("]")
            showdownCards = s[leftBracket+1:rightBracket]
            try:
                position = usernames.index(username)
                cards[position] = showdownCards  
            except:
                pass 
        # get the cards if ongames
        if website == "ONG" and "net" in s:
            leftBracket = s.find("[")
            if leftBracket != -1:
                rightBracket = s.find("]")
                showdownCards = s[leftBracket+1:rightBracket]
                colon = s.find(":")
                username = s[colon+2:colon+24]
                try: 
                    position = usernames.index(username)
                    cards[position] = showdownCards  
                except:
                    pass 

# Start the main script
# ERRORS: last error at ABS100NL - 238
counter = 0
for dr in dirs:
    #print "counter = " + str(counter)
    start = 1
    length = len([name for name in os.listdir(dr) if os.path.isfile(os.path.join(dr,name))])
    # if counter == 0:
    #     start = 326 # pass ABS 100NL
    if counter == 1:
        start = 239
    #print start
    if counter > 0:
        for i in range(1,length+1):
            print i
            try:
                parseText(dr+"abs NLH handhq_"+str(i)+"-OBFUSCATED.txt")
            except:
                print "dir failed: " + str(counter) + " file failed: " + str(i)
    counter += 1
 # close connection

 # run a single file for testing, get the file name from the argument and open it
# script, filename = argv

# parseText(filename)

DB.close() 
        
    
