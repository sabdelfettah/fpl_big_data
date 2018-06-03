import requests, time, json
from selenium import webdriver
from bs4 import BeautifulSoup

FPL_LINK = "https://fantasy.premierleague.com/a/statistics/total_points"

SELECTOR_TABLE_PLAYERS = "ism-table--el"
SELECTOR_PLAYER_NAME = "ism-table--el__name"
SELECTOR_PLAYER_CLUB = "ism-table--el__strong"
SELECTOR_PLAYER_POSITION = "ism-table--el__pos"
SELECTOR_PLAYER_FULLNAME = "ism-eiw-heading"
SELECTOR_LINK_TO_PLAYER_DETAILS = "ismjs-show-element"
SELECTOR_DIALOG_PLAYER_DETAILS_HEADER = "ism-dialog__header"
SELECTOR_DIALOG_PLAYER_DETAILS_SCROLL = "ism-dialog__scroll"
SELECTOR_DIALOG_PLAYER_DETAILS_GAME_VALUES = "ism-horizontal-data-list--basic__value"
SELECTOR_DIALOG_PLAYER_DETAILS_FANTASY_VALUES = "ism-horizontal-data-list--fantasy__value"
SELECTOR_DIALOG_PLAYER_DETAILS_TABLE = "ism-table"
SELECTOR_DIALOG_PLAYER_DETAILS_CLOSE_BUTTON = "ism-icon--close"

ARRAY_PLAYER_DATA = ["STATUS", "NAME", "PRICE", "SELECTION", "FORM", "POINTS"]
ARRAY_PLAYER_GAME_VALUES = ["FORM", "GW38", "POINTS", "PRICE", "SELECTION"]
ARRAY_PLAYER_FANTASY_VALUES = ["INFLUENCE", "CREATIVITY", "THREAT", "ICT_INDEX"]
ARRAY_PLAYER_DETAILS = ["GAME_WEEK", "OPP", "POINTS", "MINUTES_PLAYED", "GOALS_SCORED", "ASSISTS", "CLEAN_SHEETS", "GOALS_CONCEDED", "OWN_GOALS", "PINALTIES_SAVED", "PINALTIES_MISSED", "YELLOW_CARDS", "RED_CARDS", "SAVED", "BONUS", "BONUS_POINTS_SYSTEM", "INFLUENCE", "CREATIVITY", "THREAT", "ICT_INDEX", "NET_TRANSFERT", "SELECTED_BY", "PRICE"]
ARRAY_PLAYER_OLD_SEASONS_DETAILS = ["SEASON", "POINTS", "MINUTES_PLAYED", "GOALS_SCORED", "ASSISTS", "CLEAN_SHEETS", "GOALS_CONCEDED", "OWN_GOALS", "PINALTIES_SAVED", "PINALTIES_MISSED", "YELLOW_CARDS", "RED_CARDS", "SAVED", "BONUS", "BONUS_POINTS_SYSTEM", "INFLUENCE", "CREATIVITY", "THREAT", "ICT_INDEX", "PRICE"]

def getPrice(rawValue):
	return rawValue[1:]

def getPoints(rawValue):
	return rawValue.replace('pts', '')

def getSelection(rawValue):
	return rawValue.replace('%', '')

def extractPlayerDetails(driver, currentPlayer, playerLinkDetails):
	if playerLinkDetails == None:
		print 'not player link details button for', currentPlayer
	else:
		playerLinkDetails.click()
		# wait for header presence
		dialogHeader = []
		while len(dialogHeader) == 0:
			dialogHeader = driver.find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_HEADER)
			if len(dialogHeader) == 0:
				time.sleep(0.5)
		# looking for content
		dialogScroll = []
		while len(dialogScroll) == 0:
			dialogScroll = driver.find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_SCROLL)
			if len(dialogScroll) == 0:
				time.sleep(0.5)
		# player data
		fullName = dialogScroll[0].find_elements_by_class_name(SELECTOR_PLAYER_FULLNAME)
		currentPlayer["FULLNAME"] = fullName[0].text
		# initialize dicts
		seasons_details = currentPlayer["SEASONS_DETAILS"]
		season_17_18_details = {}
		# current season
		# season game values
		dataIndex = 0
		for value in dialogScroll[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_GAME_VALUES):
			if ARRAY_PLAYER_GAME_VALUES[dataIndex] == "GW38":
				pass
			elif ARRAY_PLAYER_GAME_VALUES[dataIndex] == "POINTS":
				season_17_18_details["POINTS"] = getPoints(value.text)
			elif ARRAY_PLAYER_GAME_VALUES[dataIndex] == "PRICE":
				season_17_18_details["PRICE"] = getPrice(value.text)
			elif ARRAY_PLAYER_GAME_VALUES[dataIndex] == "SELECTION":
				season_17_18_details["SELECTION"] = getSelection(value.text)
			else:
				season_17_18_details[ARRAY_PLAYER_GAME_VALUES[dataIndex]] = value.text
			dataIndex = dataIndex + 1
		# season fantasy values
		dataIndex = 0
		for value in dialogScroll[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_FANTASY_VALUES):
			season_17_18_details[ARRAY_PLAYER_FANTASY_VALUES[dataIndex]] = value.text
			dataIndex = dataIndex + 1
		# tables
		tableDetails = dialogScroll[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_TABLE)
		# this season details
		tableDetailsBody = tableDetails[0].find_elements_by_tag_name("tbody")
		gameWeeks = {}
		for playerGameInfo in tableDetailsBody[0].find_elements_by_tag_name("tr"):
			dataIndex = 0
			gameWeekInfo = {}
			gameWeek = "?"
			for gameInfo in playerGameInfo.find_elements_by_tag_name("td"):
				if ARRAY_PLAYER_DETAILS[dataIndex] == "GAME_WEEK":
					gameWeek = gameInfo.text
					gameWeekInfo["GAME_WEEK"] = gameInfo.text
				elif ARRAY_PLAYER_DETAILS[dataIndex] == "OPP":
					pass
				elif ARRAY_PLAYER_DETAILS[dataIndex] == "PRICE":
					gameWeekInfo[ARRAY_PLAYER_DETAILS[dataIndex]] = getPrice(gameInfo.text)
				else:
					gameWeekInfo[ARRAY_PLAYER_DETAILS[dataIndex]] = gameInfo.text
				dataIndex = dataIndex + 1
			gameWeeks[gameWeek] = gameWeekInfo
		season_17_18_details["GAME_WEEKS"] = gameWeeks
		seasons_details["2017/18"] = season_17_18_details
		# old seasons details
		tableDetailsBody = tableDetails[1].find_elements_by_tag_name("tbody")
		for oldSeason in tableDetailsBody[0].find_elements_by_tag_name("tr"):
			dataIndex = 0
			season = {}
			seasonName = "?"
			for seasonInfo in oldSeason.find_elements_by_tag_name("td"):
				if ARRAY_PLAYER_OLD_SEASONS_DETAILS[dataIndex] == "SEASON":
					seasonName = seasonInfo.text
					season["SEASON"] = seasonInfo.text
				elif ARRAY_PLAYER_OLD_SEASONS_DETAILS[dataIndex] == "PRICE":
					season[ARRAY_PLAYER_OLD_SEASONS_DETAILS[dataIndex]] = getPrice(seasonInfo.text)
				else:
					season[ARRAY_PLAYER_OLD_SEASONS_DETAILS[dataIndex]] = seasonInfo.text
				dataIndex = dataIndex + 1
			seasons_details[seasonName] = season
		currentPlayer["SEASONS_DETAILS"] = seasons_details
		closeButton = dialogHeader[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_CLOSE_BUTTON)
		if len(closeButton) > 0:
			closeButton[0].click()

def extractPlayerInfo(currentPlayerGolbalData):
	currentPlayer = {}
	dataIndex = 0
	name = "name"
	playerLinkDetails = None
	seasons_details = {}
	last_season = {}
	for playerInfo in currentPlayerGolbalData:
		if ARRAY_PLAYER_DATA[dataIndex] == "STATUS":
			pass
		elif ARRAY_PLAYER_DATA[dataIndex] == "NAME":
			playerLinkDetails = playerInfo.find_element_by_class_name(SELECTOR_PLAYER_NAME)
			name = playerLinkDetails.text
			currentPlayer["NAME"] = name
			currentPlayer["CLUB"] = playerInfo.find_element_by_class_name(SELECTOR_PLAYER_CLUB).text
			currentPlayer["POSITION"] = playerInfo.find_element_by_class_name(SELECTOR_PLAYER_POSITION).text
		elif ARRAY_PLAYER_DATA[dataIndex] == "PRICE":
			last_season["PRICE"] = getPrice(playerInfo.text)
		elif ARRAY_PLAYER_DATA[dataIndex] == "SELECTION":
			last_season["SELECTION"] = getSelection(playerInfo.text)
		else:
			last_season[ARRAY_PLAYER_DATA[dataIndex]] = playerInfo.text
		dataIndex = dataIndex + 1
	seasons_details["LAST_SEASON"] = last_season
	currentPlayer["SEASONS_DETAILS"] = seasons_details
	return name, currentPlayer, playerLinkDetails

def getPlayerInfo(driver, playersInCurrentPage, players, playersLinks):
	for player in playersInCurrentPage:
		print 'Processing a player ...'
		currentPlayerGolbalData = player.find_elements_by_tag_name("td")
		name, currentPlayer, playerLinkDetails = extractPlayerInfo(currentPlayerGolbalData)
		extractPlayerDetails(driver, currentPlayer, playerLinkDetails)
		filePlayer = open('dumps/player_' + currentPlayer["FULLNAME"].replace(' ', '_') + '.json', 'w')
		filePlayer.write(json.dumps(currentPlayer))
		filePlayer.close()
		players[name] = currentPlayer
		print 'Player', currentPlayer["FULLNAME"], 'processed'


# initialization
print 'Program start'
driver = webdriver.Chrome()
players = {}
clubNumber = 1
# look for table that contains player data
for clubNumber in range(20):
	print 'Processing club', clubNumber + 1, '...'
	driver.get(FPL_LINK + '/te_' + str(clubNumber + 1))
	table = []
	while len(table) == 0:
		table = driver.find_elements_by_class_name(SELECTOR_TABLE_PLAYERS)
		if len(table) == 0:
			time.sleep(0.5)
	tableBody = table[0].find_elements_by_tag_name("tbody")
	playersInCurrentPage = tableBody[0].find_elements_by_tag_name("tr")
	playersLinks = {}
	getPlayerInfo(driver, playersInCurrentPage, players, playersLinks)
filePlayers = open('dumps/players_dump.json', 'w')
filePlayers.write(json.dumps(players))
filePlayers.close()
print 'Program end'