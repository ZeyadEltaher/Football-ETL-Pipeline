def insert_into_matches(connect, cursor, home_team, away_team, home_team_score, away_team_score, status, match_date, match_time, period, game_week):

        matches_query_insert = '''
        INSERT INTO matches (home_team, away_team, home_team_score, away_team_score, status, match_date, match_time, period, game_week)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(matches_query_insert, (home_team, away_team, home_team_score, away_team_score, status, match_date, match_time, period, game_week))
        connect.commit()



def insert_into_teams(connect, cursor, team_name, league, league_level,
                                       table_position, squad_size, average_age, 
                                       foreigners_num, foreigners_percentage, 
                                       national_team_players_num, stadium_name, 
                                       stadium_capacity, current_transfer_record, total_market_value):
        
        query_insert = '''
        INSERT INTO teams (team_name, league, league_level, 
                           table_position, squad_size, average_age, 
                           foreigners_num, foreigners_percentage, 
                           national_team_players_num, stadium_name, 
                           stadium_capacity, current_transfer_record, total_market_value)    
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query_insert, (team_name, league, league_level, 
                                      table_position, squad_size, average_age, 
                                      foreigners_num, foreigners_percentage, 
                                      national_team_players_num, stadium_name, 
                                      stadium_capacity, current_transfer_record, total_market_value))
        connect.commit()