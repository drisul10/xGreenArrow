# script/transfer_preseason_recommender.py

import pandas as pd
import numpy as np
import sys
from datetime import datetime
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.transfer_recommender_config import (
    DATA_SOURCE_PATH, TEAM_ID, POSITION_MAP, MAX_PRICES,
    TOP_N_PLAYERS, DISPLAY_COLUMNS, FUTURE_FIXTURES
)
from config.analyzer_config import FIXTURE_DIFFICULTY

class TransferPreseasonRecommender:
    def __init__(self, team_id):
        self.team_id = team_id
        self.data = self.load_data()
        self.team_id_to_name = self.create_team_mapping()
        self.add_fdr_data()

    def load_data(self):
        try:
            file_path = DATA_SOURCE_PATH.format(datetime.now().strftime("%Y%m%d"))
            data = pd.read_csv(file_path)
            return data
        except FileNotFoundError:
            print(f"Error: Data file not found at {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading data: {e}")
            sys.exit(1)

    def create_team_mapping(self):
        unique_teams = self.data['team'].unique()
        team_names = list(FIXTURE_DIFFICULTY.keys())
        return dict(zip(unique_teams, team_names))

    def add_fdr_data(self):
        fdr_data = {}
        for team_id, team_name in self.team_id_to_name.items():
            if team_name in FIXTURE_DIFFICULTY:
                fdr_data[team_id] = np.mean(FIXTURE_DIFFICULTY[team_name][:FUTURE_FIXTURES])

        self.data['avg_fdr'] = self.data['team'].map(fdr_data)
        self.data['team_name'] = self.data['team'].map(self.team_id_to_name)

    def get_player_recommendations(self, position, max_price):
        position_players = self.data[
            (self.data['element_type'] == position) &
            (self.data['now_cost'] <= max_price * 10)
        ].copy()

        position_players['now_cost'] = position_players['now_cost'] / 10
        position_players['value'] = position_players['total_points'] / position_players['now_cost']
        
        # Adjust value based on FDR (lower FDR is better)
        position_players['adjusted_value'] = position_players['value'] * (6 - position_players['avg_fdr'])
        
        top_players = position_players.nlargest(TOP_N_PLAYERS, 'adjusted_value')
        
        display_cols = DISPLAY_COLUMNS.copy()
        display_cols[display_cols.index('team')] = 'team_name'  # Replace 'team' with 'team_name' in display
        
        print(f"\nTop {TOP_N_PLAYERS} {POSITION_MAP[position]} recommendations (max price £{max_price}m):")
        print(top_players[display_cols].to_string(index=False))

    def run(self):
        print("FPL Pre-Season Recommendations")
        print("==============================")
        
        for position, max_price in MAX_PRICES.items():
            self.get_player_recommendations(position, max_price)

        print("\nNote: These recommendations are based on last season's performance, current prices, and fixture difficulty.")
        print(f"The 'avg_fdr' column shows the average difficulty of the next {FUTURE_FIXTURES} fixtures.")
        print("Consider team transfers and pre-season form when making your final decisions.")

if __name__ == "__main__":
    recommender = TransferPreseasonRecommender(TEAM_ID)
    recommender.run()