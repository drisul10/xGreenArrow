# script/data_analyzer.py
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from config.analyzer_config import TOP_N_PLAYERS, DISPLAY_COLUMNS, DATA_FILE_FORMAT, FIXTURE_DIFFICULTY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set default gameweek to 1 (start of the season)
DEFAULT_GAMEWEEK = 1

def load_data():
    filename = DATA_FILE_FORMAT.format(datetime.now().strftime("%Y%m%d"))
    full_path = os.path.join(parent_dir, filename)
    
    if not os.path.exists(full_path):
        logging.error(f"Data file not found: {full_path}")
        sys.exit(1)
    
    df = pd.read_csv(full_path)
    
    # Change team value to team name
    team_mapping = pd.read_csv(os.path.join(parent_dir, 'data_source/team_mapping.csv'))
    df = df.merge(team_mapping[['id', 'name']], left_on='team', right_on='id', how='left')
    
    # Update team column with name, if available
    if 'name' in df.columns:
        df['team'] = df['name'].combine_first(df['team'])
    
    # Drop unnecessary columns if they exist
    columns_to_drop = ['id', 'name']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    
    return df

def calculate_avg_next_5_fixture_difficulty(team, current_gameweek):
    if team not in FIXTURE_DIFFICULTY:
        return None
    
    start_index = current_gameweek - 1  # -1 because list indices start at 0
    end_index = min(start_index + 5, 38)  # Ensure we don't go beyond the last gameweek
    
    next_5_fixtures = FIXTURE_DIFFICULTY[team][start_index:end_index]
    return np.mean(next_5_fixtures)

def add_fixture_difficulty(df, current_gameweek):
    df['avg_next_5_fixture_difficulty'] = df['team'].apply(lambda x: calculate_avg_next_5_fixture_difficulty(x, current_gameweek))
    return df

def basic_stats(df):
    print(f"\nMost {TOP_N_PLAYERS} expensive players:")
    print(df.nlargest(TOP_N_PLAYERS, 'now_cost')[DISPLAY_COLUMNS + ['avg_next_5_fixture_difficulty']])
    
    print(f"\nHighest {TOP_N_PLAYERS} scoring players:")
    print(df.nlargest(TOP_N_PLAYERS, 'total_points')[DISPLAY_COLUMNS + ['avg_next_5_fixture_difficulty']])

def price_vs_points_analysis(df):
    correlation = df['now_cost'].corr(df['total_points'])
    print(f"\nCorrelation between price and total points: {correlation:.2f}")
    
    print(f"\nTop {TOP_N_PLAYERS} players by price-performance ratio:")
    df['price_performance'] = df['total_points'] / df['now_cost']
    print(df.nlargest(TOP_N_PLAYERS, 'price_performance')[DISPLAY_COLUMNS + ['price_performance', 'avg_next_5_fixture_difficulty']])

def best_value_players(df):
    df['value'] = df['total_points'] / df['now_cost']
    print(f"\nBest {TOP_N_PLAYERS} value players:")
    print(df.nlargest(TOP_N_PLAYERS, 'value')[DISPLAY_COLUMNS + ['value', 'avg_next_5_fixture_difficulty']])

def analyze_fixture_difficulty(current_gameweek):
    print(f"\nFixture Difficulty Analysis for next 5 games (Current Gameweek: {current_gameweek}):")
    for team in FIXTURE_DIFFICULTY:
        avg_fdr = calculate_avg_next_5_fixture_difficulty(team, current_gameweek)
        start_index = current_gameweek - 1
        end_index = min(start_index + 5, 38)
        next_5_fixtures = FIXTURE_DIFFICULTY[team][start_index:end_index]
        print(f"{team}: {next_5_fixtures} (Avg: {avg_fdr:.2f})")
    
    print("\nTeams with Easiest Fixtures (Lowest Avg FDR):")
    sorted_teams = sorted(FIXTURE_DIFFICULTY.keys(), key=lambda x: calculate_avg_next_5_fixture_difficulty(x, current_gameweek))
    for team in sorted_teams[:5]:
        avg_fdr = calculate_avg_next_5_fixture_difficulty(team, current_gameweek)
        print(f"{team}: (Avg: {avg_fdr:.2f})")
    
    print("\nTeams with Hardest Fixtures (Highest Avg FDR):")
    for team in sorted_teams[-5:]:
        avg_fdr = calculate_avg_next_5_fixture_difficulty(team, current_gameweek)
        print(f"{team}: (Avg: {avg_fdr:.2f})")

if __name__ == "__main__":
    df = load_data()
    current_gameweek = DEFAULT_GAMEWEEK
    
    print(f"Analyzing data for Gameweek: {current_gameweek}")
    
    df = add_fixture_difficulty(df, current_gameweek)
    
    basic_stats(df)
    price_vs_points_analysis(df)
    best_value_players(df)
    analyze_fixture_difficulty(current_gameweek)