import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.url_config import BASE_URL, ENDPOINTS
import requests
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FPLDataFetcher:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()

    def fetch_data(self):
        try:
            response = self.session.get(f"{self.base_url}{ENDPOINTS['bootstrap_static']}")
            response.raise_for_status()
            data = response.json()
           
            players = pd.DataFrame(data['elements'])
            teams = pd.DataFrame(data['teams'])
            players = players.merge(teams[['id', 'name']], left_on='team', right_on='id', suffixes=('', '_team'))
           
            relevant_columns = [
                'id', 'web_name', 'team', 'name_team', 'element_type', 'selected_by_percent',
                'now_cost', 'minutes', 'goals_scored', 'assists', 'clean_sheets',
                'goals_conceded', 'own_goals', 'penalties_saved', 'penalties_missed',
                'yellow_cards', 'red_cards', 'saves', 'bonus', 'bps', 'influence',
                'creativity', 'threat', 'ict_index', 'form', 'points_per_game',
                'total_points'
            ]
            players_cleaned = players[players.columns.intersection(relevant_columns)].copy()
           
            players_cleaned.loc[:, 'now_cost'] = players_cleaned['now_cost'] / 10
           
            return players_cleaned, data['events']
        except requests.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            return None, None

    def save_data(self):
        players_data, events_data = self.fetch_data()
        if players_data is not None:
            filename = os.path.join(parent_dir, f'data_source/fpl_data_{datetime.now().strftime("%Y%m%d")}.csv')
            players_data.to_csv(filename, index=False)
            logging.info(f"Data updated and saved to {filename}")
           
            print(f"Number of players: {len(players_data)}")
            print(f"Columns: {', '.join(players_data.columns)}")
           
            next_deadline = next((event['deadline_time'] for event in events_data if not event['finished']), None)
            if next_deadline:
                print(f"\nNext deadline: {next_deadline}")
        else:
            logging.error("Failed to fetch data")

if __name__ == "__main__":
    fetcher = FPLDataFetcher()
    fetcher.save_data()