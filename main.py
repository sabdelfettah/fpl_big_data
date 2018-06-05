from utils import Utils
from seleniumfpl import SeleniumFPL



# initialization
Utils.print_running('Program processing')
selenium_fpl = SeleniumFPL()

players = {}
# looping over clubs
for club_number in range(1, 21):
	selenium_fpl.process_club(club_number)
	selenium_fpl.find_players()
	selenium_fpl.process_players(players)
Utils.write_players_dump(players)
Utils.print_success('Program processing')