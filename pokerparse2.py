''' 
This file parses through all of the text files in each hand history directory and organizes the
gathered data correctly to input it into MySQL localhost database

This is the file for inserting data into database Poker2, the one with the better and updated design.
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
from helpers import *
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
HANDFAILED = False # boolean for whether the current hand has an error in it 
# this specifies the website that the hands are from, because each
# website stores the hand histories differently
WEBSITE = "ABS"
# list of directories to parse
dirs = []
ABS100PATH = "handhistories/ABS100NL/" # text files that failed: NONE   
ABS200PATH = "handhistories/ABS200NL/" # text files that failed: NONE
ABS400PATH = "handhistories/ABS400NL/" # text files that failed: NONE
ABS600PATH = "handhistories/ABS600NL/" # text files that failed: NONE
dirs.append(ABS100PATH)
dirs.append(ABS200PATH)
dirs.append(ABS400PATH)
dirs.append(ABS600PATH)
dirs.append("handhistories/FTP50NL/") # text files that failed: 1109, 1111, 1113, 1455
dirs.append("handhistories/FTP400NL/") # text files that failed: 1048, 1415
dirs.append("handhistories/FTP600NL/") # text files that failed:
dirs.append("handhistories/ONG50NL/") # text files that failed:
dirs.append("handhistories/ONG200NL/") # text files that failed:
dirs.append("handhistories/ONG400NL/") # text files that failed:
dirs.append("handhistories/ONG600NL/") # text files that failed:
dirs.append("handhistories/ONG1000NL/") # text files that failed:
dirs.append("handhistories/PS25NL/") # text files that failed:
dirs.append("handhistories/PS50NL/") # text files that failed:
dirs.append("handhistories/PS100NL/") # text files that failed:
dirs.append("handhistories/PS200NL/") # text files that failed:
dirs.append("handhistories/PS400NL/") # text files that failed:
dirs.append("handhistories/PS600NL/") # text files that failed:
dirs.append("handhistories/PTY25NL/") # text files that failed:
dirs.append("handhistories/PTY100NL/")# text files that failed:
dirs.append("handhistories/PTY200NL/")# text files that failed:
dirs.append("handhistories/PTY400NL/")# text files that failed:
dirs.append("handhistories/PTY600NL/")# text files that failed:

# if statement for making sure certain websites only go through the proper directories


# connect to the database
DB = mysql.connector.connect(user='root',password='root',host='localhost',database='Poker2',
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
    WEBSITE = website
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
        #print "string is: " + s

        # ends the hand
        # not sure if need to change something here for other sites
        if getShowdownKeyword(WEBSITE) in s or (WEBSITE == "FTP" and "wins" in s):
            currentlocation = SHOWDOWN
        #print "currentlocation = " + str(currentlocation)
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
                query = ("REPLACE INTO hands "
                    "(hand_id, big_blind, num_players, dealer, flop, turn, river, flop_group_id, seat1,"
                    "seat1_position, seat1_starting_amount, seat1_cards," 
                    "seat1_preflop_action, seat1_flop_action, seat1_turn_action, seat1_river_action," 
                    "seat1_profit, seat1_cards_group_id, seat2, seat2_position, seat2_starting_amount," 
                    "seat2_cards, seat2_preflop_action, seat2_flop_action, seat2_turn_action, seat2_river_action," 
                    "seat2_profit, seat2_cards_group_id, seat3, seat3_position, seat3_starting_amount,"
                    "seat3_cards, seat3_preflop_action, seat3_flop_action, seat3_turn_action, seat3_river_action," 
                    "seat3_profit, seat3_cards_group_id, seat4, seat4_position, seat4_starting_amount,"
                    "seat4_cards, seat4_preflop_action, seat4_flop_action, seat4_turn_action, seat4_river_action," 
                    "seat4_profit, seat4_cards_group_id, seat5, seat5_position, seat5_starting_amount,"
                    "seat5_cards, seat5_preflop_action, seat5_flop_action, seat5_turn_action, seat5_river_action," 
                    "seat5_profit, seat5_cards_group_id, seat6, seat6_position, seat6_starting_amount,"
                    "seat6_cards, seat6_preflop_action, seat6_flop_action, seat6_turn_action, seat6_river_action," 
                    "seat6_profit, seat6_cards_group_id, seat7, seat7_position, seat7_starting_amount,"
                    "seat7_cards, seat7_preflop_action, seat7_flop_action, seat7_turn_action, seat7_river_action," 
                    "seat7_profit, seat7_cards_group_id, seat8, seat8_position, seat8_starting_amount,"
                    "seat8_cards, seat8_preflop_action, seat8_flop_action, seat8_turn_action, seat8_river_action," 
                    "seat8_profit, seat8_cards_group_id, seat9, seat9_position, seat9_starting_amount,"
                    "seat9_cards, seat9_preflop_action, seat9_flop_action, seat9_turn_action, seat9_river_action," 
                    "seat9_profit, seat9_cards_group_id) " 
                    "VALUES (%(hand_id)s, %(big_blind)s, %(num_players)s, %(dealer)s, %(flop)s,"
                    "%(turn)s, %(river)s, %(flop_group_id)s, %(seatone)s, %(seatone_position)s," 
                    "%(seatone_starting_amount)s, %(seatone_cards)s, %(seatone_preflop_action)s," 
                    "%(seatone_flop_action)s, %(seatone_turn_action)s, %(seatone_river_action)s,"
                    "%(seatone_profit)s, %(seatone_cards_group_id)s, %(seattwo)s, %(seattwo_position)s," 
                    "%(seattwo_starting_amount)s, %(seattwo_cards)s, %(seattwo_preflop_action)s,"
                    "%(seattwo_flop_action)s, %(seattwo_turn_action)s, %(seattwo_river_action)s," 
                    "%(seattwo_profit)s, %(seattwo_cards_group_id)s, %(seatthree)s, %(seatthree_position)s, %(seatthree_starting_amount)s," 
                    "%(seatthree_cards)s, %(seatthree_preflop_action)s, %(seatthree_flop_action)s, %(seatthree_turn_action)s," 
                    "%(seatthree_river_action)s, %(seatthree_profit)s, %(seatthree_cards_group_id)s,"
                    "%(seatfour)s, %(seatfour_position)s, %(seatfour_starting_amount)s,"
                    "%(seatfour_cards)s, %(seatfour_preflop_action)s, %(seatfour_flop_action)s," 
                    "%(seatfour_turn_action)s, %(seatfour_river_action)s, %(seatfour_profit)s,"
                    "%(seatfour_cards_group_id)s, %(seatfive)s, %(seatfive_position)s,"
                    "%(seatfive_starting_amount)s, %(seatfive_cards)s, %(seatfive_preflop_action)s," 
                    "%(seatfive_flop_action)s, %(seatfive_turn_action)s, %(seatfive_river_action)s,"
                    "%(seatfive_profit)s, %(seatfive_cards_group_id)s, %(seatsix)s,"
                    "%(seatsix_position)s, %(seatsix_starting_amount)s,"
                    "%(seatsix_cards)s, %(seatsix_preflop_action)s, %(seatsix_flop_action)s, %(seatsix_turn_action)s,"
                    "%(seatsix_river_action)s, %(seatsix_profit)s, %(seatsix_cards_group_id)s,"
                    "%(seatseven)s, %(seatseven_position)s, %(seatseven_starting_amount)s, %(seatseven_cards)s," 
                    "%(seatseven_preflop_action)s, %(seatseven_flop_action)s,"
                    "%(seatseven_turn_action)s, %(seatseven_river_action)s, %(seatseven_profit)s,"
                    "%(seatseven_cards_group_id)s, %(seateight)s, %(seateight_position)s, %(seateight_starting_amount)s," 
                    "%(seateight_preflop_action)s, %(seateight_flop_action)s,"
                    "%(seateight_turn_action)s, %(seateight_river_action)s, %(seateight_profit)s,"
                    "%(seateight_profit)s, %(seateight_cards_group_id)s, %(seatnine)s, %(seatnine_position)s," 
                    "%(seatnine_starting_amount)s, %(seatnine_cards)s," "%(seatnine_preflop_action)s," 
                    "%(seatnine_flop_action)s, %(seatnine_turn_action)s,"
                    "%(seatnine_river_action)s, %(seatnine_profit)s, %(seatnine_cards_group_id)s)")
    
                # anything that is a float or int needs to be a number, like 0.0 
                # remember this for queries
                seatsToInsert = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                positionsList = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                startingAmountsList = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
                preflopActionsList = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                holeCardsList = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                flopActionsList = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                turnActionsList = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                riverActionsList = ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"]
                profitList = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

                counter = 0
                for i in range(1,10):
                    # in a try except because seats is not always of length 9, but be careful
                    # because this may fail to catch errors 
                    try:
                        index = seats[i-1]
                        #print "index = " + str(index)
                        seatsToInsert[index-1] = usernames[i-1]
                        positionsList[index-1] = getPosition(counter,numplayers)
                        startingAmountsList[index-1] = startingamounts[i-1]
                        holeCardsList[index-1] = cards[i-1]
                        preflopActionsList[index-1] = preflopActions[i-1]
                        flopActionsList[index-1] = flopActions[i-1]
                        turnActionsList[index-1] = turnActions[i-1]
                        riverActionsList[index-1] = riverActions[i-1]
                        profitList[index-1] = (-1*amountLost[i-1])
                    except:
                        pass
                    counter += 1
                
                # for i in range(0,len(flopActionsList)):
                #     print flopActionsList[i]

                NA = "N/A"

                queryData = {
                    'hand_id': handId,
                    'big_blind': bigBlind,
                    'num_players': numplayers,
                    'dealer': dealer,
                    'flop': flop,
                    'turn': turn,
                    'river': river,
                    'flop_group_id': 'N/A',
                    'seatone': seatsToInsert[0],
                    'seatone_position': positionsList[0],
                    'seatone_starting_amount': startingAmountsList[0],
                    'seatone_cards': holeCardsList[0],
                    'seatone_preflop_action': preflopActionsList[0],
                    'seatone_flop_action': flopActionsList[0],
                    'seatone_turn_action': turnActionsList[0],
                    'seatone_river_action': riverActionsList[0],
                    'seatone_profit': profitList[0],
                    'seatone_cards_group_id': "",
                    'seattwo': seatsToInsert[1],
                    'seattwo_position': positionsList[1],
                    'seattwo_starting_amount': startingAmountsList[1],
                    'seattwo_cards': holeCardsList[1],
                    'seattwo_preflop_action': preflopActionsList[1],
                    'seattwo_flop_action': flopActionsList[1],
                    'seattwo_turn_action': turnActionsList[1],
                    'seattwo_river_action': riverActionsList[1],
                    'seattwo_profit': profitList[1],
                    'seattwo_cards_group_id': "",
                    'seatthree': seatsToInsert[2],
                    'seatthree_position': positionsList[2],
                    'seatthree_starting_amount': startingAmountsList[2],
                    'seatthree_cards': holeCardsList[2],
                    'seatthree_preflop_action': preflopActionsList[2],
                    'seatthree_flop_action': flopActionsList[2],
                    'seatthree_turn_action': turnActionsList[2],
                    'seatthree_river_action': riverActionsList[2],
                    'seatthree_profit': profitList[2],
                    'seatthree_cards_group_id': "",
                    'seatfour': seatsToInsert[3],
                    'seatfour_position': positionsList[3],
                    'seatfour_starting_amount': startingAmountsList[3],
                    'seatfour_cards': holeCardsList[3],
                    'seatfour_preflop_action': preflopActionsList[3],
                    'seatfour_flop_action': flopActionsList[3],
                    'seatfour_turn_action': turnActionsList[3],
                    'seatfour_river_action': riverActionsList[3],
                    'seatfour_profit': profitList[3],
                    'seatfour_cards_group_id': "",
                    'seatfive': seatsToInsert[4],
                    'seatfive_position': positionsList[4],
                    'seatfive_starting_amount': startingAmountsList[4],
                    'seatfive_cards': holeCardsList[4],
                    'seatfive_preflop_action': preflopActionsList[4],
                    'seatfive_flop_action': flopActionsList[4],
                    'seatfive_turn_action': turnActionsList[4],
                    'seatfive_river_action': riverActionsList[4],
                    'seatfive_profit': profitList[4],
                    'seatfive_cards_group_id': "",
                    'seatsix': seatsToInsert[5],
                    'seatsix_position': positionsList[5],
                    'seatsix_starting_amount': startingAmountsList[5],
                    'seatsix_cards': holeCardsList[5],
                    'seatsix_preflop_action': preflopActionsList[5],
                    'seatsix_flop_action': flopActionsList[5],
                    'seatsix_turn_action': turnActionsList[5],
                    'seatsix_river_action': riverActionsList[5],
                    'seatsix_profit': profitList[5],
                    'seatsix_cards_group_id': "",
                    'seatseven': seatsToInsert[6],
                    'seatseven_position': positionsList[6],
                    'seatseven_starting_amount': startingAmountsList[6],
                    'seatseven_cards': holeCardsList[6],
                    'seatseven_preflop_action': preflopActionsList[6],
                    'seatseven_flop_action': flopActionsList[6],
                    'seatseven_turn_action': turnActionsList[6],
                    'seatseven_river_action': riverActionsList[6],
                    'seatseven_profit': profitList[6],
                    'seatseven_cards_group_id': "",
                    'seateight': seatsToInsert[7],
                    'seateight_position': positionsList[7],
                    'seateight_starting_amount': startingAmountsList[7],
                    'seateight_cards': holeCardsList[7],
                    'seateight_preflop_action': preflopActionsList[7],
                    'seateight_flop_action': flopActionsList[7],
                    'seateight_turn_action': turnActionsList[7],
                    'seateight_river_action': riverActionsList[7],
                    'seateight_profit': profitList[7],
                    'seateight_cards_group_id': "",
                    'seatnine': seatsToInsert[8],
                    'seatnine_position': positionsList[8],
                    'seatnine_starting_amount': startingAmountsList[8],
                    'seatnine_cards': holeCardsList[8],
                    'seatnine_preflop_action': preflopActionsList[8],
                    'seatnine_flop_action': flopActionsList[8],
                    'seatnine_turn_action': turnActionsList[8],
                    'seatnine_river_action': riverActionsList[8],
                    'seatnine_profit': profitList[8],
                    'seatnine_cards_group_id': "",
                }

                # print queryData

                try:
                    cursor.execute(query,queryData)
                except:
                    print "query failed"

                # insert into players
                for username in usernames:
                    playersQuery = ("INSERT IGNORE INTO players "
                                   "(USER_ID) "
                                   "VALUES (%(username)s)")

                    playersQueryData = {
                        'username': username,
                    }

                    cursor.execute(playersQuery,playersQueryData)

                # only commit if HANDFAILED == FALSE
                #print HANDFAILED
                if not HANDFAILED:
                    DB.commit()

            # now reset handfailed to false
            HANDFAILED = False

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
            #     break
            # print "Starting New Hand"
            numHands += 1
            handId = getHandId(WEBSITE,s)

            

            # can just get the big blind from the directory
            #print "stake = " + str(stake)
            bigBlind = int(stake*100)
            #print "big blind = " + str(bigBlind)
            #print "hand id = " + handId
            if handId in BROKENHANDSLIST:
                currentlocation = SKIP
        # store broken handIds in list, if it's in this list, try except until new hand id is found
        # if handId == "#16405529160":
        #         print s
        if buttonCondition(WEBSITE,s): # gets dealer's seat
            dealer = getButton(WEBSITE,s)
        if usernameCondition(WEBSITE,s) and currentlocation != SKIP and currentlocation != SHOWDOWN: 
            # gets the seats
            # print "string " + s + " is inside usernameCondition"
            seats.append(int(s[5]))
            # gets the username for the player
            index = s.find("-") 
            if index == -1:
                index = s.find(":")
            username = s[index + 2: index + 24]

           
            usernames.append(username)

            # gets starting chips for each player
            # if dollar is not found, it means the hand history is broken
            # - this may not work for PS, check it
            # print s
            dollar = s.find("$")
            if dollar == -1:
                currentlocation = SKIP
            else:
                if "," in s and "sitting out" not in s:
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
                #print money 
                try:
                    money = float(money)
                except:
                    print "hand failed1"
                    HANDFAILED = True
                # print money
                startingamounts.append(money)

                # increment the number of players
                numplayers += 1
                # add to amount lost
                amountLost.append(0.0)
        # will have to double check antes for other sites
        try:
            if handId == "26262277666":
                print amountLost[0]
        except:
            pass
        if "Ante" in s and "Stage" not in s:
            username = s[0:22]
            dollar = s.find("$")
            amount = float(s[dollar+1:len(s)])
            try:
                position = usernames.index(username)
                amountLost[position] += amount
            except:
                #print "failed ante"
                pass
        # gets the small blind and big blind
        if "Posts" in s or "posts" in s:
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
                #print "amount 1 = " + str(amount)
                if "dead" in s:
                    if WEBSITE == "PTY" and stopIndex == -1:
                        stopIndex = s2.find("]")
                    amount = removeCommas(s[dollar+1:dollar+1+stopIndex])
                else:
                    if stopIndex == -1:
                        if WEBSITE == "PTY":
                            stopIndex = s2.find("]")
                            amount = removeCommas(s[dollar+1:dollar+1+stopIndex])
                        else:
                            amount = removeCommas(s[dollar+1:])
                    else:
                        amount = removeCommas(s[dollar+1:dollar+1+stopIndex])
                #print "amount 2 = " + str(amount)
                if "adds" not in s:
                    amountLost[position] += amount
            except:
                #print "failed posts"
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
                    if dollar != -1 and "returned" not in s and "collected" not in s: #this means a call or raise was made 
                        s2 = s[dollar+1:]
                        if WEBSITE == "FTP" or WEBSITE == "PTY" or ("raises" not in s and "Raises" not in s):
                            space = s2.find(" ")
                             # if space not found, money goes until end of line
                            if space == -1:
                                space = len(s) - dollar - 1
                            amount = removeCommas(s[dollar+1:dollar+1+space])
                        else:
                            dollar2 = s2.find("$")
                            space = s2.find(" ")
                             # if space not found, money goes until end of line
                            if space == -1:
                                space = len(s) - dollar - dollar2 - 1
                            amount = removeCommas(s[dollar+dollar2+2:dollar+dollar2+2+space])
                        if "adds" not in s:
                            amountLost[position] += amount 
                except:
                    #print "failed preflop"
                    pass
            else:
                # get the flop
               #print "in flop else, currentlocation = " + str(currentlocation) + " line is: " + s
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
                    if dollar != -1 and "returned" not in s and "collected" not in s: #this means a call or raise was made 
                        s2 = s[dollar+1:]
                        if WEBSITE == "FTP" or WEBSITE == "PTY" or ("raises" not in s and "Raises" not in s):
                            space = s2.find(" ")
                             # if space not found, money goes until end of line
                            if space == -1:
                                space = len(s) - dollar - 1
                            amount = removeCommas(s[dollar+1:dollar+1+space])
                        else:
                            dollar2 = s2.find("$")
                            space = s2.find(" ")
                             # if space not found, money goes until end of line
                            if space == -1:
                                space = len(s) - dollar - dollar2 - 1
                            amount = removeCommas(s[dollar+dollar2+2:dollar+dollar2+2+space])
                        if "adds" not in s:
                            amountLost[position] += amount 
                except:
                    #print "failed flop"
                    pass
            else:
                currentlocation = TURN
                rightBracket = s.find("]")
                s2 = s[rightBracket+1:]
                leftBracket = s2.find("[")
                rightBracket2 = s2.find("]")
                turn = s[leftBracket+2+rightBracket:rightBracket+rightBracket2+1]
                if WEBSITE == "ONG" or WEBSITE == "PTY":
                    leftBracket = s.find("[")
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
                action = s[dash+1:len(s)]
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
                    if dollar != -1 and "returned" not in s and "collected" not in s: #this means a call or raise was made 
                        s2 = s[dollar+1:]
                        if WEBSITE == "FTP" or WEBSITE == "PTY" or ("raises" not in s and "Raises" not in s):
                            space = s2.find(" ")
                             # if space not found, money goes until end of line
                            if space == -1:
                                space = len(s) - dollar - 1
                            amount = removeCommas(s[dollar+1:dollar+1+space])
                        else:
                            dollar2 = s2.find("$")
                            space = s2.find(" ")
                             # if space not found, money goes until end of line
                            if space == -1:
                                space = len(s) - dollar - dollar2 - 1
                            amount = removeCommas(s[dollar+dollar2+2:dollar+dollar2+2+space])
                        if "adds" not in s:
                            amountLost[position] += amount
                        if handId == "59937802670":
                            print "position = " + str(position)  
                            print "amountLost[position] = " + str(amountLost[position])
                            print "amount = " + str(amount)
                    if handId == "26262274180":
                        print "turn action = " + turnActions[position]
                except:
                    #print "failed turn"
                    pass
            else:
                currentlocation = RIVER
                rightBracket = s.find("]")
                s2 = s[rightBracket+1:]
                leftBracket = s2.find("[")
                rightBracket2 = s2.find("]")
                river = s[leftBracket+2+rightBracket:rightBracket+rightBracket2+1]
                if WEBSITE == "ONG" or WEBSITE == "PTY":
                    leftBracket = s.find("[")
                    river = s[leftBracket+1:rightBracket]
                # print "after river, river is " + river
        # get the river actions and store them correctly
        if currentlocation == RIVER and getRiverKeyword(WEBSITE) not in s:
            if WEBSITE == "PTY" and ("shows" in s or "show" in s):
                currentlocation = SHOWDOWN
            else:
                if getShowdownKeyword(WEBSITE) not in s:
                    username = s[0:22]
                    if WEBSITE == "ABS":
                        dash = s.find("-")
                    else:
                        dash = s.find(" ")
                    action = s[dash+1:len(s)]
                    
                    try:
                        position = usernames.index(username)
                        # since multiple actions can be taken need to append the string
                        if riverActions[position] == "N/A":
                            riverActions[position] = action
                        else:
                            temp = riverActions[position]
                            temp2 = temp + " " 
                            if action.find("$") != -1 or "folds" in action or "checks" in action:
                                if handId == "26262271782":
                                    print action 
                                    # break
                                riverActions[position] = temp2 + str(action)
                        dollar = s.find("$")
                        if dollar != -1 and "returned" not in s and "collected" not in s: #this means a call or raise was made 
                            s2 = s[dollar+1:]
                            if WEBSITE == "FTP" or WEBSITE == "PTY" or ("raises" not in s and "Raises" not in s):
                                space = s2.find(" ")
                                 # if space not found, money goes until end of line
                                if space == -1:
                                    space = len(s) - dollar - 1
                                amount = removeCommas(s[dollar+1:dollar+1+space])
                            else:
                                dollar2 = s2.find("$")
                                space = s2.find(" ")
                                 # if space not found, money goes until end of line
                                if space == -1:
                                    space = len(s) - dollar - dollar2 - 1
                                    amount = removeCommas(s[dollar+dollar2+2:dollar+dollar2+2+space])
                            if "adds" not in s:
                                amountLost[position] += amount 
                    except:
                        #print "failed river"
                        pass
                else:
                    currentlocation = SHOWDOWN
        # get the showdown and find the profits made
        if currentlocation == SHOWDOWN and getShowdownKeyword(WEBSITE) not in s:
            if getCollectsKeyword(WEBSITE) in s and WEBSITE != "PTY":
                # print s
                
                # if website is ONG, find the second $
                if WEBSITE == "ONG":
                    dollar = s[20:].find("$")
                    s2 = s[dollar+21:]
                else:
                    dollar = s.find("$")
                    s2 = s[dollar+1:]
                space = s2.find(" ")
                if WEBSITE == "ONG" or WEBSITE == "FTP":
                    space = s2.find(")")
                try:
                    if WEBSITE == "ONG":
                        amountWon = removeCommas(s[dollar+21:dollar+21+space])
                    else: 
                        amountWon = removeCommas(s[dollar+1:dollar+1+space])
                except:
                    print "hand failed2"
                    HANDFAILED = True
                username = s[0:22]
                if WEBSITE == "ONG":
                    y = s.find("y")
                    username = s[y+2:y+24]
                try:
                    position = usernames.index(username)
                    if handId == "#16405527740":
                            print "position = " + str(position)  
                            print "amountLost[position] = " + str(amountLost[position])
                            print "amount = " + str(amount)
                    if "adds" not in s:
                        amountLost[position] -= amountWon
                except:
                    #print "failed2"
                    pass
        # if at any point there is a "returned" or SHOW DOWN hand is over
        if ("returned" in s or "collected" in s) or (WEBSITE == "PTY" and "wins" in s) and "has" not in s and currentlocation != SKIP:
            if handId == "26262277666":
                print "returned"
            username = s[0:22]
            dollar = s.find("$")
            s2 = s[dollar+1:]
            space = s2.find(" ")
            rightParentheses = s.find(")")
            if WEBSITE == "FTP":
                username = s[-24:-2]
                rightParentheses = space + dollar + 1
            if WEBSITE == "PS" or WEBSITE == "PTY":
                rightParentheses = space + dollar + 1
            try:
                amountReturned = removeCommas(s[dollar+1:rightParentheses])
            except:
                #print "hand failed3"
                HANDFAILED = True
            try:
                position = usernames.index(username)
                if handId == "26262277666":
                    print username
                if handId == "26262277666":
                    print position
                if "adds" not in s:
                    amountLost[position] -= amountReturned
            except:    
                #print "failed returning amount"
                pass
            # end the hand by setting currentlocation to showdown
            currentlocation = SHOWDOWN
        # get the cards
        if WEBSITE != "ONG" and ("Shows" in s or "shows" in s or "show" in s):
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
    # gets the number of files in directory
    length = len([name for name in os.listdir(dr) if os.path.isfile(os.path.join(dr,name))])
    # if counter == 0:
    #     start = 326 # pass ABS 100NL
    # if counter == 1:
    #     start = 239
    #print start
    # if counter > 0:

    # get the big blind
    index = dr.find("N")
    ongIndex = dr[index+1:].find("N")
    # print dr
    # print ongIndex
    try:
        if ongIndex != -1:
            WEBSITE = "ONG"
            stake = float(dr[ongIndex-3+index+1:ongIndex+index+1])
        else:
            stake = float(dr[index-3:index])
            WEBSITE = dr[index-6:index-3]
    except:
        if ongIndex != -1:
            stake = float(dr[ongIndex-2+index+1:ongIndex+index+1])
        else:
            stake = float(dr[index-2:index])
            WEBSITE = dr[index-5:index-2]
        
    # print WEBSITE
    # print stake
    stake = stake/100.0

    # how many directories to go through
    # if counter == 1:
    #     break 

    # because FTP50NL and other sites have oddly numbered files?
    if counter == 4:
        length = 1470
    if counter == 5:
        length = 1538
    if counter == 7:
        length = 1922
    if counter == 8:
        length = 1784
    if counter == 12:
        length = 4943
    if counter == 14:
        length = 1341
    if counter == 19:
        length = 2199
    if counter == 20:
        length = 1901
    if counter == 21:
        length = 1001

    if counter >= 0:
        for i in range(1,length+1):
            # if condition since some file numbers are skipped
            if counter >= 0 and counter <= 3 or (counter == 4 and (i == 1 or i >= 10 and i <= 14 or i >= 100 and i <= 147 or i >= 1000)) or (counter == 5 and (i >=1 and i <= 5 or i >= 10 and i <= 53 or i >= 100 and i <= 537 or i >= 1000)) or (counter == 7 and (i == 1 or i >= 10 and i<= 19 or i >= 100 and i <= 192 or i >= 1000)) or (counter == 8 and (i >= 1 and i <= 5 or i >= 10 and i <= 55 or i >= 100 and i <= 557 or i >= 1000)) or (counter == 12 and (i >= 1 and i <= 4 or i >= 10 and i <= 49 or i >= 100 and i <= 493 or i >= 1000)) or (counter == 14 and (i >= 1000 or i <= 853)) or (counter == 19 and (i <= 2 or i >= 10 and i <= 22 or i >= 100 and i <= 220 or i >= 1000)) or (counter == 20 and (i >= 1 and i <= 7 or i >= 10 and i <= 77 or i >= 100 and i <= 769 or i >= 1000)) or (counter == 21 and (i >= 1 and i <= 7 or i >= 10 and i <= 77 or i >= 100 and i <= 777 or i >= 1000)) or counter == 6 or counter >= 9 and counter <= 11 or counter == 13 or counter >= 14 and counter <= 18 or counter == 22:
                print "Running files in directory " + dr + " file #" + str(i)

                dirString = "abs"
                if WEBSITE == "FTP":
                    dirString = "ftp"
                if WEBSITE == "PTY":
                    dirString = "pty"
                if WEBSITE == "ONG":
                    dirString = "ong"
                if WEBSITE == "PS":
                    dirString = "ps"

                # to run without try except
                #parseText(dr+dirString+" NLH handhq_"+str(i)+"-OBFUSCATED.txt",WEBSITE,stake)

                try:
                     parseText(dr+dirString+" NLH handhq_"+str(i)+"-OBFUSCATED.txt",WEBSITE,stake)
                except:
                     print "dir failed: " + dr + " file failed: " + str(i)
    counter += 1
 # close connection

 # run a single file for testing, get the file name from the argument and open it
# script, filename = argv
# parseText(filename,"PTY",100)

DB.close() 
        
    
