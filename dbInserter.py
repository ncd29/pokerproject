""" This file is for giving hands already in the database
a flop group_id and a group_id for each players hole cards 
if they are not 'N/A'.  If the criteria for these conditions 
is not met, an 'N/A' is inserted.  """

import mysql.connector
import unicodedata
# TODOS: hand_action part is done and ready to test on full data set
# - hands part is now done too and is ready to test on full data set
# - WAIT to run this until db is reformattted or all data uploaded

# connect to the database
DB = mysql.connector.connect(user='root',password='root',host='localhost',database='Poker2',
    unix_socket="/Applications/MAMP/tmp/mysql/mysql.sock")

# helper functions

""" Removes the whitespace and commas of a string and returns a string without the whitespace """
def removeWhitespaceAndCommas(s):
	if len(s) == 0:
		return s
	if s[0] == " " or s[0] == ",":
		return str(removeWhitespaceAndCommas(s[1:]))
	else:
		return s[0] + str(removeWhitespaceAndCommas(s[1:]))

# end helper functions

# insert into the card group_ids based on the players cards
def insertCards():
	print "starting queries"
	cursor = DB.cursor(buffered = True)

	query1 = "SELECT * FROM hands WHERE num_players = 6"

	cursor.execute(query1)

	print "query 1 done"

	query2 =  ("SELECT hand_id,seat1_cards,seat2_cards,seat3_cards,seat4_cards,seat5_cards,seat6_cards,"
	"seat7_cards,seat8_cards,seat9_cards FROM hands")

	cursor.execute(query)

	print "query 2 done"

	counter = 0
	for (hand_id,seat1_cards,seat2_cards,seat3_cards,seat4_cards,seat5_cards,seat6_cards,seat7_cards,seat8_cards,seat9_cards) in cursor:
		print "for"
		# after this cards will be in format 'RsRs' i.e. 'QdJh'
		cardsList = []
		cardsList.append(seat1_cards)
		cardsList.append(seat2_cards)
		cardsList.append(seat3_cards)
		cardsList.append(seat4_cards)
		cardsList.append(seat5_cards)
		cardsList.append(seat6_cards)
		cardsList.append(seat7_cards)
		cardsList.append(seat8_cards)
		cardsList.append(seat9_cards)
		# loop through cards to add to card group id
		for i in range(0,len(cardsList)):
			# if cards are longer than  , skip because it means there is bad data
			if len(cardsList[i] < 9):
				oldCards = cardsList[i]
				print cards
				print str(cards)[2:-1]
				cards = removeWhitespaceAndCommas(str(cardsList[i]))
				print cards
				HIGHPAIR = False
				MIDPAIR = False
				LOWPAIR = False
				BROADWAY = False
				SC = False # suited connectors - only 45s - 109s
				# check for pairs
				c = cards[0]
				if c == cards[2]:
					if c == 'Q' or c == 'K' or c == 'A':
						HIGHPAIR = True
					elif c == 'J' or c == 'T' or c == '9' or c == '8' or c == '7':
						MIDPAIR = True
					else:
						LOWPAIR = True
				# check for broadway
				else:
					try:
						i = int(c)
					except:
						if c != 'T':
							try:
								i2 = int(cards[2])
							except:
								if cards[2] != 'T':
									BROADWAY = True
					# check for SC
					try:
						i = int(c)
						i2 = int(cards[2])
						if cards[1] == cards[3] and (i + 1 == i2 or i - 1 == i2):
							SC = True
					except:
						if cards == '9' and c == 'T' or c == '9' and cards[2] == 'T':
							SC = True

				# update group_id column in hand_action
				string = "UPDATE hands SET seat" + str(i) + "_cards_group_id"
				update = (string + " = %(group_id)s WHERE seat" + str(i) + "_cards = %(cards)s AND hand_id = %(hand_id)s")

				cursor2 = DB.cursor()

				data = ""

				if HIGHPAIR:
					data = "BPS"
				if MIDPAIR:
					data = "MPS"
				if LOWPAIR:
					data = "SPS"
				# suited connectors get priority over broadway
				if BROADWAY:
					data = "BRD"
				if SC:
					data = "SCT"

				updateData = {
					'group_id': data,
					'cards': oldCards,
					'hand_id': hand_id,
				}

				try:
					cursor2.execute(update,updateData)
				except:
					print "query failed"

				DB.commit()

				# test a certain number of inserts
				# if counter > 10:
				# 	break
				counter = counter + 1

# start the insertion - hand action
insertCards()

# function for insertion of flop_id into hands table
def insertHands():
	query =  "SELECT hand_id,flop FROM hands WHERE flop <> %(na)s"

	cursor = DB.cursor(buffered = True)

	queryData = {
		'na': "N/A",
	}

	cursor.execute(query,queryData)

	counter = 0
	for (hand_id,flop) in cursor:
		flop = removeWhitespaceAndCommas(str(flop))
		# if flop is not empty
		if len(flop) > 1:
			print flop
			# check if all suits are the same
			PAIRED = False
			RAINBOW = False
			MONOTONE = False
			print flop[5]
			if flop[1] == flop[3] and flop[3] == flop[5]:
				MONOTONE = True
			if flop[0] == flop[2] or flop[0] == flop[4] or flop[2] == flop[4]:
				PAIRED = True
			if flop[1] != flop[3] and flop[3] != flop[5] and flop[1] != flop[5]:
				RAINBOW = True

			# insert into database
			update = ("UPDATE hands SET flop_group_id = %(group_id)s WHERE hand_id = %(hand_id)s")

			cursor2 = DB.cursor()

			data = ""

			if PAIRED:
				data = data + "PRD"
			if MONOTONE:
				data = data + "MON"
			if RAINBOW:
				if data == "":
					data = "RBW"
				else:
					data = data + "," + "RBW"

			updateData = {
				'group_id': data,
				'hand_id': hand_id,
			}

			try:
				cursor2.execute(update,updateData)
			except:
				print "query failed"

			DB.commit()

		# test a certain number of inserts
		# if counter > 10:
		# 	break
		counter = counter + 1

# start the insertion - hands
insertHands()