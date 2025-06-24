import os
import time
import mysql.connector
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functions import get_url
from functions import click_current_gameweek
from functions import click_a_gameweek_from_list
from functions import get_gameweek_matches_info
from queries import create_table_matches
from queries import create_table_teams
from queries import get_unique_teams
from queries import get_last_game_week
from queries import get_lastweek_games_length



# Load environment variables and connect to MySQL
load_dotenv()
connect = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
)
cursor = connect.cursor()

# Create required tables if they don't exist
create_table_matches(connect, cursor)
create_table_teams(connect, cursor)

# Fetch existing unique teams from database to avoid duplicates
unique_teams = get_unique_teams(cursor)

# Get details of the last processed game week
last_game_week, last_game_week_num, last_game_week_index = get_last_game_week(cursor)
last_game_week_length = get_lastweek_games_length(cursor, last_game_week_num)

# Flags for tracking game week state
case_1 = case_2 = case_3 = False



print("\n=========== Last Game Week Info ===========")
print(f"Last Game Week Name   : {last_game_week}")
print(f"Last Game Week Number : {last_game_week_num}")
print(f"Last Game Week Index  : {last_game_week_index}")
print(f"Last Game Week Length : {last_game_week_length}")
print("===========================================\n")



# ================================================ Determine where to start ================================================#

if last_game_week is None and last_game_week_index is None and last_game_week_length == 0 :  # NEXT WEEK STARTS FROM SCRATCH

        case_1 = True
        print("WE ARE IN CASE 1")
        #================================#
        start_from_scratch = True
        start_with_the_first_match = True
        start_at_somepoint = False
        #================================#
        next_game_week = "Game week 1"
        next_game_week_num = 1
        next_game_week_index = 0
        next_match_index = 0
        

elif last_game_week is not None and 37 >= last_game_week_index >= 0 and 10 > last_game_week_length > 0 :  # LAST WEEK STOPPED AT SOMEPOINT
        
        case_2 = True
        print("WE ARE IN CASE 2")
        #================================#
        start_from_scratch = False
        start_with_the_first_match = False
        start_at_somepoint = True
        #================================#
        next_game_week = last_game_week
        next_game_week_num = last_game_week_num
        next_game_week_index = last_game_week_index
        next_match_num = last_game_week_length + 1
        next_match_index = next_match_num - 1
        

elif last_game_week is not None and 37 >= last_game_week_index >= 0 and last_game_week_length == 10 :  # LAST WEEK HAS ALREADY ENDED
        
        case_3 = True
        print("WE ARE IN CASE 3")
        #================================#
        start_from_scratch = False
        start_with_the_first_match = True
        start_at_somepoint = False
        #================================#
        next_game_week = f"Game week {last_game_week_num + 1}"
        next_game_week_num = last_game_week_num + 1
        next_game_week_index = next_game_week_num - 1
        next_match_index = 0

# ==================================================================================================================================#



print("\n=========== Next Game Week Info ===========")
print(f"Next Game Week Name   : {next_game_week}")
print(f"Next Game Week Number : {next_game_week_num}")
print(f"Next Game Week Index  : {next_game_week_index}")
print(f"Next Match Number     : {next_match_num}")
print(f"Next Match Index      : {next_match_index}")
print("===========================================\n")




# Get the access of premier league url
season = [2024, 2025]
premier_league_url = f"https://int.soccerway.com/national/england/premier-league/{season[0]}{season[1]}/regular-season/r81780/"
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)




# Handle cookie consent pop-up
max_tries, tries, delay = 3, 0, 5
while tries < max_tries:
        try: 
                driver.get(premier_league_url)
                wait_cookies = WebDriverWait(driver=driver, timeout=10)
                cookies_button = wait_cookies.until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'Consent')]")))
                cookies_button.click()
                break
        except Exception as e:
                tries += 1
                print(f"[ERROR] Attempt {tries} failed: {e}. Retrying after {delay} seconds...")
                time.sleep(delay)





# ================== Start looping through Game Weeks ====================

for num in range(next_game_week_index,38):

        #==================== STARTING THE PROCCESS =====================#
        click_current_gameweek(driver)
        click_a_gameweek_from_list(driver, num)
        get_gameweek_matches_info(driver, connect, cursor, next_match_index, unique_teams, 'Premier League', 'overview')
        get_url(driver, premier_league_url, "div[data-testid='virtuoso-item-list']", max_tries = 3, delay = 5)
        #======================= RESET THE START ========================#
        next_match_index = 0
        #======================== PROCCESS ENDED ========================#

# ========================================================================



# DRIVER QUITTING
driver.quit()
