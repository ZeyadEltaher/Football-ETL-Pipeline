import re





def create_table_matches(connect, cursor):
        
        query_create_matches = '''
        CREATE TABLE IF NOT EXISTS matches (
                match_id INT AUTO_INCREMENT PRIMARY KEY,
                home_team VARCHAR(50),
                away_team VARCHAR(50),
                home_team_score INT,
                away_team_score INT,
                status VARCHAR(25),
                match_date DATE,
                match_time TIME,
                period VARCHAR(2),
                game_week VARCHAR(25)
        );
        '''
        cursor.execute(query_create_matches)
        connect.commit()



def create_table_teams(connect, cursor):

        query_create_teams = '''
        CREATE TABLE IF NOT EXISTS teams (
                team_id INT AUTO_INCREMENT PRIMARY KEY,
                team_name VARCHAR(50),
                league VARCHAR(50),
                league_level VARCHAR(50),
                table_position INT,
                squad_size INT,
                average_age DOUBLE,
                foreigners_num INT,
                foreigners_percentage DOUBLE,
                national_team_players_num INT,
                stadium_name VARCHAR(50),
                stadium_capacity INT,
                current_transfer_record VARCHAR(50),
                total_market_value VARCHAR(20)
        );      
        '''
        cursor.execute(query_create_teams)
        connect.commit()



def get_unique_teams(cursor):

        query_select_unique = "SELECT DISTINCT team_name FROM teams;"
        cursor.execute(query_select_unique)
        rows = cursor.fetchall()
        if rows:
                teams = [row[0] for row in rows if row[0] is not None]
                return teams

        else:
                teams = []
                return teams
        


def get_last_game_week(cursor):
        
        query_last_game_week = '''
        SELECT game_week FROM matches
        ORDER BY match_id DESC
        LIMIT 1;
        '''
        cursor.execute(query_last_game_week)
        last_game_week = cursor.fetchall()

        if last_game_week:
                last_game_week = last_game_week[0][0]
                last_game_week_num = int(re.split(" ", last_game_week)[2])
                last_game_week_index = last_game_week_num - 1
                return last_game_week, last_game_week_num, last_game_week_index
        
        else:
                return None, None, None
                  


def get_lastweek_games_length(cursor, last_game_week_num):

        query_lastweek_games_length = '''
        SELECT COUNT(*) FROM matches
        WHERE game_week = 'Game week %s';
        '''
        cursor.execute(query_lastweek_games_length, (last_game_week_num,))
        last_game_week_length = cursor.fetchall()[0][0]
        return last_game_week_length

