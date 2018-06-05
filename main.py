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

def getPrice(raw_value):
	return raw_value[1:]

def getPoints(raw_value):
	return raw_value.replace('pts', '')

def getSelection(raw_value):
	return raw_value.replace('%', '')

def extractPlayerDetails(driver, current_player, player_link_details):
	if player_link_details == None:
		print 'not player link details button for', current_player
	else:
		player_link_details.click()
		# wait for header presence
		dialog_header = []
		while len(dialog_header) == 0:
			dialog_header = driver.find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_HEADER)
			if len(dialog_header) == 0:
				time.sleep(0.5)
		# looking for content
		dialog_scroll = []
		while len(dialog_scroll) == 0:
			dialog_scroll = driver.find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_SCROLL)
			if len(dialog_scroll) == 0:
				time.sleep(0.5)
		# player data
		full_name = dialog_scroll[0].find_elements_by_class_name(SELECTOR_PLAYER_FULLNAME)
		current_player["FULLNAME"] = full_name[0].text
		# initialize dicts
		seasons_details = current_player["SEASONS_DETAILS"]
		season_17_18_details = {}
		# current season
		# season game values
		data_index = 0
		for value in dialog_scroll[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_GAME_VALUES):
			if ARRAY_PLAYER_GAME_VALUES[data_index] == "GW38":
				pass
			elif ARRAY_PLAYER_GAME_VALUES[data_index] == "POINTS":
				season_17_18_details["POINTS"] = getPoints(value.text)
			elif ARRAY_PLAYER_GAME_VALUES[data_index] == "PRICE":
				season_17_18_details["PRICE"] = getPrice(value.text)
			elif ARRAY_PLAYER_GAME_VALUES[data_index] == "SELECTION":
				season_17_18_details["SELECTION"] = getSelection(value.text)
			else:
				season_17_18_details[ARRAY_PLAYER_GAME_VALUES[data_index]] = value.text
			data_index = data_index + 1
		# season fantasy values
		data_index = 0
		for value in dialog_scroll[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_FANTASY_VALUES):
			season_17_18_details[ARRAY_PLAYER_FANTASY_VALUES[data_index]] = value.text
			data_index = data_index + 1
		# tables
		table_details = dialog_scroll[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_TABLE)
		# this season details
		table_details_body = table_details[0].find_elements_by_tag_name("tbody")
		game_weeks = {}
		for player_game_info in table_details_body[0].find_elements_by_tag_name("tr"):
			data_index = 0
			game_week_info = {}
			game_week = "?"
			for game_info in player_game_info.find_elements_by_tag_name("td"):
				if ARRAY_PLAYER_DETAILS[data_index] == "GAME_WEEK":
					game_week = game_info.text
					game_week_info["GAME_WEEK"] = game_info.text
				elif ARRAY_PLAYER_DETAILS[data_index] == "OPP":
					pass
				elif ARRAY_PLAYER_DETAILS[data_index] == "PRICE":
					game_week_info[ARRAY_PLAYER_DETAILS[data_index]] = getPrice(game_info.text)
				else:
					game_week_info[ARRAY_PLAYER_DETAILS[data_index]] = game_info.text
				data_index = data_index + 1
			game_weeks[game_week] = game_week_info
		season_17_18_details["GAME_WEEKS"] = game_weeks
		seasons_details["2017/18"] = season_17_18_details
		# old seasons details
		table_details_body = table_details[1].find_elements_by_tag_name("tbody")
		for old_season in table_details_body[0].find_elements_by_tag_name("tr"):
			data_index = 0
			season = {}
			season_name = "?"
			for season_info in old_season.find_elements_by_tag_name("td"):
				if ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index] == "SEASON":
					season_name = season_info.text
					season["SEASON"] = season_info.text
				elif ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index] == "PRICE":
					season[ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index]] = getPrice(season_info.text)
				else:
					season[ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index]] = season_info.text
				data_index = data_index + 1
			if season_name == '2017/18':
				seasons_details["LAST_SEASON_GLOBAL"] = season
			else:
				seasons_details[season_name] = season
		current_player["SEASONS_DETAILS"] = seasons_details
		close_button = dialog_header[0].find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_CLOSE_BUTTON)
		if len(close_button) > 0:
			close_button[0].click()

def extractPlayerInfo(current_player_global_data):
	current_player = {}
	data_index = 0
	name = "name"
	player_link_details = None
	seasons_details = {}
	last_season = {}
	for player_info in current_player_global_data:
		if ARRAY_PLAYER_DATA[data_index] == "STATUS":
			pass
		elif ARRAY_PLAYER_DATA[data_index] == "NAME":
			player_link_details = player_info.find_element_by_class_name(SELECTOR_PLAYER_NAME)
			name = player_link_details.text
			current_player["NAME"] = name
			current_player["CLUB"] = player_info.find_element_by_class_name(SELECTOR_PLAYER_CLUB).text
			current_player["POSITION"] = player_info.find_element_by_class_name(SELECTOR_PLAYER_POSITION).text
		elif ARRAY_PLAYER_DATA[data_index] == "PRICE":
			last_season["PRICE"] = getPrice(player_info.text)
		elif ARRAY_PLAYER_DATA[data_index] == "SELECTION":
			last_season["SELECTION"] = getSelection(player_info.text)
		else:
			last_season[ARRAY_PLAYER_DATA[data_index]] = player_info.text
		data_index = data_index + 1
	seasons_details["LAST_SEASON"] = last_season
	current_player["SEASONS_DETAILS"] = seasons_details
	return name, current_player, player_link_details

def getPlayerInfo(driver, players_in_current_page, players, players_links):
	for player in players_in_current_page:
		print 'Processing a player ...'
		current_player_global_data = player.find_elements_by_tag_name("td")
		name, current_player, player_link_details = extractPlayerInfo(current_player_global_data)
		extractPlayerDetails(driver, current_player, player_link_details)
		file_player = open('dumps/player_' + current_player["FULLNAME"].replace(' ', '_') + '.json', 'w')
		file_player.write(json.dumps(current_player))
		file_player.close()
		players[name] = current_player
		print 'Player', current_player["FULLNAME"], 'processed'


# initialization
print 'Program start'
driver = webdriver.Chrome()
players = {}
club_number = 1
# look for table that contains player data
for club_number in range(20):
	print 'Processing club', club_number + 1, '...'
	driver.get(FPL_LINK + '/te_' + str(club_number + 1))
	table = []
	while len(table) == 0:
		table = driver.find_elements_by_class_name(SELECTOR_TABLE_PLAYERS)
		if len(table) == 0:
			time.sleep(0.5)
	table_body = table[0].find_elements_by_tag_name("tbody")
	players_in_current_page = table_body[0].find_elements_by_tag_name("tr")
	players_links = {}
	getPlayerInfo(driver, players_in_current_page, players, players_links)
file_players = open('dumps/players_dump.json', 'w')
file_players.write(json.dumps(players))
file_players.close()
print 'Program end'