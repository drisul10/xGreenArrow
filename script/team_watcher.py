# script/team_watcher.py

import os
import sys
import requests
from datetime import datetime

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.team_watcher_config import BASE_URL, TEAM_ID

class TeamWatcher:
    def __init__(self, team_id):
        self.team_id = team_id
        self.base_url = BASE_URL

    def get_team_data(self):
        url = f"{self.base_url}entry/{self.team_id}/"
        return self._make_request(url, "team data")

    def get_team_history(self):
        url = f"{self.base_url}entry/{self.team_id}/history/"
        return self._make_request(url, "team history")

    def get_current_gameweek_picks(self):
        bootstrap_url = f"{self.base_url}bootstrap-static/"
        bootstrap_data = self._make_request(bootstrap_url, "bootstrap static data")
        if not bootstrap_data:
            return None
        
        current_gameweek = next((event['id'] for event in bootstrap_data['events'] if event['is_current']), None)
        if not current_gameweek:
            print("No current gameweek found. The season might not have started or might be between gameweeks.")
            return None

        url = f"{self.base_url}entry/{self.team_id}/event/{current_gameweek}/picks/"
        return self._make_request(url, "current gameweek picks")

    def _make_request(self, url, data_type):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                print(f"Error 404: {data_type} not found. Please check if the team ID is correct.")
            else:
                print(f"HTTP error occurred while fetching {data_type}: {http_err}")
        except Exception as err:
            print(f"An error occurred while fetching {data_type}: {err}")
        return None

def main():
    watcher = TeamWatcher(TEAM_ID)
    
    team_data = watcher.get_team_data()
    if team_data:
        print(f"Team name: {team_data['name']}")
        print(f"Overall rank: {team_data['summary_overall_rank']}")
        print(f"Total points: {team_data['summary_overall_points']}")

    team_history = watcher.get_team_history()
    if team_history:
        print("\nSeason History:")
        for season in team_history['past']:
            print(f"Season {season['season_name']}: Rank {season['rank']}, Points {season['total_points']}")

    current_picks = watcher.get_current_gameweek_picks()
    if current_picks:
        print("\nCurrent Gameweek Picks:")
        for pick in current_picks['picks']:
            print(f"Player ID: {pick['element']}, Position: {pick['position']}")

if __name__ == "__main__":
    main()