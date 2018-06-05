from utils import Utils
from selenium import webdriver

CONFIGURATION_DRIVER_WAIT_TIMEOUT = 10

FPL_LINK_TEAM = "https://fantasy.premierleague.com/a/statistics/total_points/te_{0}"

MESSAGE_WEB_DRIVER_INITIALIZING = "Initializing web driver"
MESSAGE_WEB_DRIVER_CONFIGURING = "Configuring web driver"
MESSAGE_PROCESSING_CLUB = "Processing club {0}"

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

class SeleniumFPL():

    def __init__(self):
        Utils.print_running(MESSAGE_WEB_DRIVER_INITIALIZING)
        self.driver = webdriver.Chrome()
        Utils.print_success(MESSAGE_WEB_DRIVER_INITIALIZING)
        Utils.print_running(MESSAGE_WEB_DRIVER_CONFIGURING)
        self.driver.implicitly_wait(CONFIGURATION_DRIVER_WAIT_TIMEOUT)
        Utils.print_success(MESSAGE_WEB_DRIVER_CONFIGURING) 

    def process_club(self, club_number):
        Utils.print_running(MESSAGE_PROCESSING_CLUB.format(club_number))
        self.driver.get(FPL_LINK_TEAM.format(club_number))
        Utils.print_success(MESSAGE_PROCESSING_CLUB.format(club_number))

    def find_players(self):
        self.table_players = self.driver.find_element_by_class_name(SELECTOR_TABLE_PLAYERS)
        self.table_players_body = self.table_players.find_element_by_tag_name("tbody")
        self.players_tr_in_current_page = self.table_players_body.find_elements_by_tag_name("tr")

    def process_players(self, players_dict):
        for player in self.players_tr_in_current_page:
            Utils.print_running('Processing a player')
            self.current_player_tds = player.find_elements_by_tag_name("td")
            self.extract_current_player_data()
            self.extract_current_player_extra_data()
            Utils.write_player_data(self.current_player_data)
            players_dict[self.current_player_name] = self.current_player_data
            Utils.print_success('Processing player {0}'.format(self.current_player_data["FULLNAME"]))

    def extract_current_player_data(self):
        self.current_player_data = {}
        data_index = 0
        self.current_player_name = "name"
        self.current_player_details_clickable_element = None
        seasons_details = {}
        last_season = {}
        for player_info in self.current_player_tds:
            if ARRAY_PLAYER_DATA[data_index] == "STATUS":
                pass
            elif ARRAY_PLAYER_DATA[data_index] == "NAME":
                self.current_player_details_clickable_element = player_info.find_element_by_class_name(SELECTOR_PLAYER_NAME)
                self.current_player_name = self.current_player_details_clickable_element.text
                Utils.print_running('Processing player {0}'.format(self.current_player_name))
                self.current_player_data["NAME"] = self.current_player_name
                self.current_player_data["CLUB"] = player_info.find_element_by_class_name(SELECTOR_PLAYER_CLUB).text
                self.current_player_data["POSITION"] = player_info.find_element_by_class_name(SELECTOR_PLAYER_POSITION).text
            elif ARRAY_PLAYER_DATA[data_index] == "PRICE":
                last_season["PRICE"] = Utils.get_price(player_info.text)
            elif ARRAY_PLAYER_DATA[data_index] == "SELECTION":
			    last_season["SELECTION"] = Utils.get_selection(player_info.text)
            else:
                last_season[ARRAY_PLAYER_DATA[data_index]] = player_info.text
            data_index = data_index + 1
	    seasons_details["LAST_SEASON"] = last_season
	    self.current_player_data["SEASONS_DETAILS"] = seasons_details

    def extract_current_player_extra_data(self):
        if self.current_player_details_clickable_element == None:
            print 'No player link details button for', self.current_player_name
            self.current_player_data["FULLNAME"] = "UNKNOWN"
            return
        else:
            self.current_player_details_clickable_element.click()
        # looking for content
        dialog_header = self.driver.find_element_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_HEADER)
        dialog_scroll = self.driver.find_element_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_SCROLL)
        # player data
        full_name_header = dialog_scroll.find_element_by_class_name(SELECTOR_PLAYER_FULLNAME)
        self.current_player_data["FULLNAME"] = full_name_header.text
		# initialize dicts
        seasons_details = self.current_player_data["SEASONS_DETAILS"]
        season_17_18_details = {}
		# current season
		# season game values
        data_index = 0
        for value in dialog_scroll.find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_GAME_VALUES):
            if ARRAY_PLAYER_GAME_VALUES[data_index] == "GW38":
                pass
            elif ARRAY_PLAYER_GAME_VALUES[data_index] == "POINTS":
				season_17_18_details["POINTS"] = Utils.get_points(value.text)
            elif ARRAY_PLAYER_GAME_VALUES[data_index] == "PRICE":
				season_17_18_details["PRICE"] = Utils.get_price(value.text)
            elif ARRAY_PLAYER_GAME_VALUES[data_index] == "SELECTION":
				season_17_18_details["SELECTION"] = Utils.get_selection(value.text)
            else:
				season_17_18_details[ARRAY_PLAYER_GAME_VALUES[data_index]] = value.text
            data_index = data_index + 1
		# season fantasy values
        data_index = 0
        for value in dialog_scroll.find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_FANTASY_VALUES):
			season_17_18_details[ARRAY_PLAYER_FANTASY_VALUES[data_index]] = value.text
			data_index = data_index + 1
		# tables
        table_details = dialog_scroll.find_elements_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_TABLE)
		# this season details
        table_details_body = table_details[0].find_element_by_tag_name("tbody")
        game_weeks = {}
        for player_game_info in table_details_body.find_elements_by_tag_name("tr"):
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
					game_week_info[ARRAY_PLAYER_DETAILS[data_index]] = Utils.get_price(game_info.text)
				else:
					game_week_info[ARRAY_PLAYER_DETAILS[data_index]] = game_info.text
				data_index = data_index + 1
			game_weeks[game_week] = game_week_info
        season_17_18_details["GAME_WEEKS"] = game_weeks
        seasons_details["2017/18"] = season_17_18_details
		# old seasons details
        table_details_body = table_details[1].find_element_by_tag_name("tbody")
        for old_season in table_details_body.find_elements_by_tag_name("tr"):
			data_index = 0
			season = {}
			season_name = "?"
			for season_info in old_season.find_elements_by_tag_name("td"):
				if ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index] == "SEASON":
					season_name = season_info.text
					season["SEASON"] = season_info.text
				elif ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index] == "PRICE":
					season[ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index]] = Utils.get_price(season_info.text)
				else:
					season[ARRAY_PLAYER_OLD_SEASONS_DETAILS[data_index]] = season_info.text
				data_index = data_index + 1
			if season_name == '2017/18':
				seasons_details["LAST_SEASON_GLOBAL"] = season
			else:
				seasons_details[season_name] = season
        self.current_player_data["SEASONS_DETAILS"] = seasons_details
        close_button = dialog_header.find_element_by_class_name(SELECTOR_DIALOG_PLAYER_DETAILS_CLOSE_BUTTON)
        close_button.click()