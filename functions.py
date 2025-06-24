import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from database import insert_into_matches
from database import insert_into_teams
from constants import team_name_mapping
from constants import month_dict
from datetime import datetime
import time





def normalize_team_name(name_from_soccerway):
        return team_name_mapping.get(name_from_soccerway, name_from_soccerway)


def get_transfermarkt_url(team, league, page):

        url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche"
        params = {'query': team}
        headers = {"User-Agent": "Mozilla/5.0", 
                   "Accept-Language": "en-US,en;q=0.9"}
        respone = requests.get(url=url, params=params, headers=headers)
        soup = BeautifulSoup(respone.content, 'lxml')

        boxes = soup.find_all('div', {'class': 'box'})
        for box in boxes:
                h2 = box.select("h2.content-box-headline")
                if h2:
                        text = h2[0].get_text(strip=True)
                        if "Search results: Clubs" in text:
                                club_box = box
                                break

        all_tr = club_box.find_all('tr', class_=['odd', 'even'])
        for tr in all_tr:
                table = tr.find('table', {'class': 'inline-table'})
                all_a = table.find_all('a')
                if len(all_a) == 2:
                        if all_a[1].get_text(strip=True) == league:
                                overview_back_url = all_a[0]['href']
                                overview_page = f"https://www.transfermarkt.com{overview_back_url}"
                                portrait_page = overview_page.replace('/startseite/', '/datenfakten/')
                                if page == 'overview':
                                        return overview_page
                                elif page == 'portrait':
                                        return portrait_page                 


def connect_with_selenium(team_url, max_tries = 3, delay=5):

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service()

        tries = 0

        while tries < max_tries:

                driver = webdriver.Chrome(service=service, options=options)

                try:
                        driver.get(team_url)
                        wait_page = WebDriverWait(driver, 15)
                        wait_page.until(EC.any_of(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-header__badge-container")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.data-header__info-box"))
                        ))
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        return soup
                
                except Exception as e:
                        tries += 1
                        print(f"[ERROR] Attempt {tries} failed: {e}. Retrying after {delay} seconds...")
                        time.sleep(delay)

                finally:
                        driver.quit()


def get_teams_info(connect, cursor, team, unique_teams:list, league='Premier League', page='overview'):

        team_name = league_level = table_position = None
        table_position = squad_size = foreigners_num = foreigners_percentage = None
        average_age = national_team_players_num = stadium_name = stadium_capacity = current_transfer_record = total_market_value = None

        transfermarket_team_name = normalize_team_name(team)
        team_url = get_transfermarkt_url(transfermarket_team_name, league, page)
        soup = connect_with_selenium(team_url, max_tries=3, delay=5)

        # team_name
        team_name = soup.find("h1", class_="data-header__headline-wrapper")
        team_name = team_name.get_text(strip=True) if team_name else None

        if team_name not in unique_teams:

                # add new team to the list
                unique_teams.append(team_name)
                        
                # league
                league = soup.find("span", {'itemprop': 'affiliation'})
                league = league.get_text(strip=True) if league else None

                # league_level, table_position
                sections1 = soup.find_all('span', {'class': 'data-header__label'})   

                for section in sections1:
                        label = section.get_text(strip=True)
                        if "League level" in label:
                                league_level = label.split(':')[1].strip()
                        if "Table position" in label:
                                table_position = int(label.split(':')[1].strip())

                # Getting some variables ready 
                all_ul = soup.find_all('ul', {'class': 'data-header__items'})
                left_ul = all_ul[0]
                right_ul = all_ul[1]
                all_left_li = left_ul.find_all('li', {'class':'data-header__label'})
                all_right_li = right_ul.find_all('li', {'class':'data-header__label'})

                # squad_size, average_age, foreigners_num, foreigners_percentage
                for left_li in all_left_li:  
                        left_li_text = left_li.get_text(strip=True)
                        if 'Squad size' in left_li_text:
                                squad_size = int(left_li_text.split(':')[1])
                        if 'Average age' in left_li_text:
                                average_age = float(left_li_text.split(':')[1])
                        if 'Foreigners' in left_li_text:
                                foreigners_num = left_li.find('a')
                                foreigners_num = int(foreigners_num.get_text(strip=True)) if foreigners_num else None       
                                foreigners_percentage = left_li.find('span', {'class': "tabellenplatz"})    
                                foreigners_percentage = foreigners_percentage.get_text(strip=True) if foreigners_percentage else None
                                foreigners_percentage = float(re.findall(r'\d+\.?\d*', foreigners_percentage)[0])


                # national_team_players_num, stadium_name, stadium_capacity, current_transfer_record
                for right_li in all_right_li:
                        right_li_text = right_li.get_text(strip=True)
                        if 'National team players' in right_li_text:
                                national_team_players_num = int(right_li_text.split(':')[1])
                        if 'Stadium' in right_li_text:
                                stadium_name = right_li.find('a')
                                stadium_name = stadium_name.get_text(strip=True) if stadium_name else None
                                stadium_capacity = right_li.find('span', {'class': "tabellenplatz"})
                                stadium_capacity = stadium_capacity.get_text(strip=True) if stadium_capacity else None
                                stadium_capacity = int(''.join(c for c in stadium_capacity if c.isdigit()))
                        if 'Current transfer record' in right_li_text:
                                current_transfer_record = right_li_text.split(':')[1]


                # total_market_value
                a = soup.select('a.data-header__market-value-wrapper')[0]
                p_text = a.select("p.data-header__last-update")[0].get_text(strip=True)
                if p_text == "Total market value":
                        texts = a.find_all(text=True)
                        total_market_value = f"{texts[0]}{texts[1]}{texts[2]}"



                insert_into_teams(connect, cursor, team_name, league, league_level,
                                table_position, squad_size, average_age, 
                                foreigners_num, foreigners_percentage, 
                                national_team_players_num, stadium_name, 
                                stadium_capacity, current_transfer_record, total_market_value)
                        
        
        return team_name






def get_url(driver, url, CSS_selector, max_tries = 3, delay = 5):

        tries = 0

        while tries < max_tries:

                try:
                        driver.get(url)
                        wait = WebDriverWait(driver, 15)
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_selector)))
                        break

                except Exception as e:
                        tries += 1
                        print(f"[ERROR] Attempt {tries} failed: {e}. Retrying after {delay} seconds...")
                        time.sleep(delay)


def change_data_format(date, match_year):

        tokens = re.split(" ", date)
        day_number = tokens[1]
        month_abbr = tokens[2]
        month_number = month_dict.get(month_abbr)
        year_number = match_year
        new_form = f"{day_number}/{month_number}/{year_number}"
        new_date = datetime.strptime(new_form, '%d/%m/%Y').date()
        return new_date


def change_time_format(time_str):

        time_obj_24 = datetime.strptime(time_str, "%H:%M")
        hour_12 = time_obj_24.strftime("%I:%M")
        period = time_obj_24.strftime("%p")
        time_12 = datetime.strptime(hour_12, "%I:%M").time()
        return time_12, period
     

def click_current_gameweek(driver):

        soup = BeautifulSoup(driver.page_source, "html.parser")
        spans = soup.find_all('span', class_=['sc-4e4c9eab-2', 'jgDxUJ', 'label', 'sc-35a8f489-1', 'yGBtH'])
        for span in spans:
                span_text = span.get_text(strip = True)
                if re.fullmatch(r"Game week \d+", span_text):
                        current_game_week = span_text
                        wait_current_game_week = WebDriverWait(driver, 10)
                        current_game_week_button = wait_current_game_week.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{current_game_week}')]")))
                        current_game_week_button.click()
                        break  # We did break because there is only one 'span' line that meets the requirements  


def click_a_gameweek_from_list(driver, num:int):
        
        div_id = f'unique_flyout_option_{num}'
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, f'unique_flyout_option_{num}')))
        button = wait.until(EC.element_to_be_clickable((By.ID, div_id)))
        button.click()


def get_gameweek_matches_info(driver, connect, cursor, start_with_match, unique_teams:list, league='Premier League', page='overview'):    
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        all_a = soup.select("a.sc-22ef6ec-0.sc-8b63db7c-2.boVFdS.cFNJqe")
        all_a = all_a[start_with_match:]

        for a in all_a:

                back_url = a.get('href')
                pattern = r"^/matches/\d{4}/\d{2}/\d{2}/england/premier-league/[^/]+/[^/]+/\d+/$"
                if re.fullmatch(pattern, back_url):
                        
                        match_url = f"https://int.soccerway.com{back_url}"
                        driver.get(match_url)
                        wait_page = WebDriverWait(driver, 15)
                        wait_page.until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[role='img']")))
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        ############################# GETTING THE DATA READY #############################
                        # TEAMS NAMES
                        teams_lines = soup.select("h1.sc-4e4c9eab-3.hQjjrj.headline.sc-dcd93ddc-4.jxmSJF")
                        home_team = teams_lines[0].get_text(strip=True)
                        away_team = teams_lines[1].get_text(strip=True)

                        # TEAMS SCORES
                        scores_lines = soup.select("div.sc-4e4c9eab-1.fPbPfi.label.sc-dcd93ddc-6.dEQiwD")
                        home_team_score = int(scores_lines[0].get_text(strip=True))
                        away_team_score = int(scores_lines[1].get_text(strip=True))

                        # STATUS
                        spans = soup.select("span.sc-4e4c9eab-2.bqusqS.label.sc-3fc313b7-2.fdlSrP")                  
                        for span in spans:
                                span_text = span.get_text(strip=True)
                                if span_text.isalpha():
                                        status = span_text

                        # DATE, TIME AND PERIOD
                        datetime_lines = soup.select('span[style="white-space: nowrap;"]')
                        match_date_string = re.search(r"/(\d{4}/\d{2}/\d{2})/", match_url)
                        match_date = datetime.strptime(match_date_string.group(1), "%Y/%m/%d").date()
                        match_time_string = datetime_lines[1].get_text(strip=True)
                        match_time, period = change_time_format(match_time_string)

                        # GAME WEEK NUMBER
                        game_week_line = soup.select("span.sc-4e4c9eab-2.jgDxUJ.label.sc-6edf00b3-1.fCptJZ.more")
                        game_week = game_week_line[0].get_text(strip=True)
                                
                        # CHECK IF TEAMS EXIST IN UNIQUE TEAMS
                        transfermarkt_hometeam_name = get_teams_info(connect, cursor, home_team, unique_teams, league, page)
                        transfermarkt_awayteam_name = get_teams_info(connect, cursor, away_team, unique_teams, league, page)

                        # INSERTING DATA INTO DATABASES
                        insert_into_matches(connect, cursor, transfermarkt_hometeam_name, transfermarkt_awayteam_name, home_team_score, away_team_score, status, match_date, match_time, period, game_week)
                        ############################# GETTING THE DATA READY #############################