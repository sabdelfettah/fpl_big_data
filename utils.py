import json


class Utils():

    @staticmethod
    def get_price(raw_value):
	    return raw_value[1:]

    @staticmethod
    def get_points(raw_value):
	    return raw_value.replace('pts', '')

    @staticmethod
    def get_selection(raw_value):
	    return raw_value.replace('%', '')
    
    @staticmethod
    def write_player_data(player_data):
        file_name = 'dumps/player_' + player_data["FULLNAME"].replace(' ', '_') + '.json'
        file_player = open(file_name, 'w')
        file_player.write(json.dumps(player_data))
        file_player.close()

    @staticmethod
    def write_players_dump(players_dict):
        file_player = open('dumps/players_dump.json', 'w')
        file_player.write(json.dumps(players_dict))
        file_player.close()

    @staticmethod
    def jamString(text, length_to_have):
        while len(text) < length_to_have:
            text = text + ' '
        return text

    @staticmethod
    def print_running(message):
        print message + '...'

    @staticmethod
    def print_success(message):
        print Utils.jamString(message, 46) + '[OK]'