# config/transfer_recommender_config.py

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# API base URL
BASE_URL = "https://fantasy.premierleague.com/api/"

# Data source path
DATA_SOURCE_PATH = os.path.join(BASE_DIR, 'data_source', 'fpl_data_{}.csv')

# Team ID for analysis
TEAM_ID = 4193107

# Position mapping
POSITION_MAP = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}

# Maximum prices for each position
MAX_PRICES = {
    1: 5.5,  # Goalkeepers
    2: 6.0,  # Defenders
    3: 8.0,  # Midfielders
    4: 9.0   # Forwards
}

# Number of top players to recommend
TOP_N_PLAYERS = 10

# Columns to display in recommendations
DISPLAY_COLUMNS = ['web_name', 'team', 'now_cost', 'total_points', 'points_per_game', 'value', 'avg_fdr']

# Columns to display in player data
DISPLAY_COLUMNS_2 = ['web_name', 'team', 'now_cost', 'total_points', 'points_per_game', 'form']

# Number of future fixtures to consider for FDR
FUTURE_FIXTURES = 5

# Maximum price increase for transfer recommendations
MAX_PRICE_INCREASE = 5  # 0.5m

# Number of top recommendations to show
TOP_RECOMMENDATIONS = 20

# FDR color mapping
FDR_COLORS = {
    1: 'dark green',
    2: 'light green',
    3: 'gray',
    4: 'pink',
    5: 'red'
}