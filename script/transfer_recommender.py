# script/transfer_recommender.py

import pandas as pd
import requests
import sys
from datetime import datetime
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.transfer_recommender_config import (
    DATA_SOURCE_PATH, TEAM_ID, BASE_URL, FUTURE_FIXTURES,
    MAX_PRICE_INCREASE, TOP_RECOMMENDATIONS, DISPLAY_COLUMNS_2
)
from config.analyzer_config import FIXTURE_DIFFICULTY

class TransferRecommender:
    def __init__(self, team_id):
        self.team_id = team_id
        self.base_url = BASE_URL
        self.player_data = None
        self.team_data = None
        self.fixtures = None
        self.current_event = None
        self.team_id_to_name = None

    def fetch_data(self):
        try:
            # Load player data from local CSV
            file_path = DATA_SOURCE_PATH.format(datetime.now().strftime("%Y%m%d"))
            self.player_data = pd.read_csv(file_path)
            
            # Create team ID to name mapping
            self.team_id_to_name = dict(zip(self.player_data['team'].unique(), FIXTURE_DIFFICULTY.keys()))
            
            # Fetch team data
            r = requests.get(f"{self.base_url}entry/{self.team_id}/")
            r.raise_for_status()
            self.team_data = r.json()
            
            # Fetch bootstrap-static for events data
            r = requests.get(f"{self.base_url}bootstrap-static/")
            r.raise_for_status()
            events = r.json()['events']
            
            # Determine current or next event
            self.current_event = next((event for event in events if event['is_current']), None)
            if not self.current_event:
                self.current_event = next((event for event in events if event['is_next']), None)
            
            if self.current_event:
                # Fetch picks for the current or next gameweek
                try:
                    r = requests.get(f"{self.base_url}entry/{self.team_id}/event/{self.current_event['id']}/picks/")
                    r.raise_for_status()
                    self.team_picks = r.json()
                except requests.exceptions.RequestException:
                    print("Unable to fetch team picks. The season might not have started yet.")
                    self.team_picks = None
            else:
                print("No current or upcoming gameweek found. The season might be over or hasn't started yet.")
                self.team_picks = None
            
            # Add FDR data to player_data
            self.add_fdr_data()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: Data file not found at {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading data: {e}")
            sys.exit(1)

    def add_fdr_data(self):
        fdr_data = {}
        for team_id, team_name in self.team_id_to_name.items():
            if team_name in FIXTURE_DIFFICULTY:
                fdr_data[team_id] = sum(FIXTURE_DIFFICULTY[team_name][:FUTURE_FIXTURES]) / FUTURE_FIXTURES

        self.player_data['avg_fdr'] = self.player_data['team'].map(fdr_data)

    def calculate_player_score(self, player):
        form = float(player['form']) if player['form'] != '' else 0
        price = player['now_cost'] / 10
        fixture_difficulty = player['avg_fdr']
        
        score = form * 10 - price + (5 - fixture_difficulty)
        return score

    def get_top_players(self):
        self.player_data['score'] = self.player_data.apply(self.calculate_player_score, axis=1)
        top_players = self.player_data.nlargest(TOP_RECOMMENDATIONS, 'score')
        return top_players[DISPLAY_COLUMNS_2 + ['score', 'avg_fdr']]

    def recommend_transfers(self):
        if not self.team_picks or 'picks' not in self.team_picks:
            print("Unable to recommend transfers: No team picks available.")
            return []

        current_squad = [pick['element'] for pick in self.team_picks['picks']]
        recommendations = []

        for position in range(1, 5):  # GK, DEF, MID, FWD
            position_players = self.player_data[self.player_data['element_type'] == position]
            current_position_players = position_players[position_players['id'].isin(current_squad)]
            
            for _, player in current_position_players.iterrows():
                player_score = self.calculate_player_score(player)
                better_players = position_players[
                    (position_players['now_cost'] <= player['now_cost'] + MAX_PRICE_INCREASE) &
                    (position_players['id'] != player['id'])
                ]
                
                for _, candidate in better_players.iterrows():
                    candidate_score = self.calculate_player_score(candidate)
                    if candidate_score > player_score:
                        recommendations.append({
                            'out': player['web_name'],
                            'in': candidate['web_name'],
                            'score_improvement': candidate_score - player_score
                        })
        
        return sorted(recommendations, key=lambda x: x['score_improvement'], reverse=True)[:TOP_RECOMMENDATIONS]

    def run(self):
        self.fetch_data()
        if self.team_data:
            print(f"Team Name: {self.team_data['name']}")
            print(f"Overall Rank: {self.team_data['summary_overall_rank']}")
            print(f"Total Points: {self.team_data['summary_overall_points']}")
            print()

        if self.current_event:
            print(f"Current/Next Gameweek: {self.current_event['name']}")
            print(f"Deadline: {self.current_event['deadline_time']}")
            print()

        recommendations = self.recommend_transfers()
        
        if recommendations:
            print(f"Top {TOP_RECOMMENDATIONS} Transfer Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. Transfer out: {rec['out']}, Transfer in: {rec['in']}")
                print(f"   Score Improvement: {rec['score_improvement']:.2f}")
                print()
        else:
            print("No transfer recommendations available.")
            print("Showing top players based on current form and upcoming fixtures:")
            top_players = self.get_top_players()
            print(top_players.to_string(index=False))

if __name__ == "__main__":
    recommender = TransferRecommender(TEAM_ID)
    recommender.run()