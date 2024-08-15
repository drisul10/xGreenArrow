import requests
import pandas as pd
import sys
from datetime import datetime

class Diagnostics:
    def __init__(self, team_id):
        self.team_id = team_id
        self.base_url = "https://fantasy.premierleague.com/api/"

    def fetch_general_data(self):
        try:
            r = requests.get(f"{self.base_url}bootstrap-static/")
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching general FPL data: {e}")
            return None

    def fetch_team_data(self):
        try:
            r = requests.get(f"{self.base_url}entry/{self.team_id}/")
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching team data: {e}")
            return None

    def run_diagnostics(self):
        print("Running FPL Diagnostics...")
        print(f"Checking for team ID: {self.team_id}")
        
        general_data = self.fetch_general_data()
        if not general_data:
            print("Unable to fetch general FPL data. The API might be down or the structure might have changed.")
            return

        print("\nGeneral FPL Information:")
        print(f"Total Players: {len(general_data['elements'])}")
        print(f"Total Teams: {len(general_data['teams'])}")
        
        current_event = next((event for event in general_data['events'] if event['is_current']), None)
        next_event = next((event for event in general_data['events'] if event['is_next']), None)
        
        if current_event:
            print(f"\nCurrent Gameweek: {current_event['name']}")
            print(f"Deadline: {current_event['deadline_time']}")
        elif next_event:
            print(f"\nNext Gameweek: {next_event['name']}")
            print(f"Deadline: {next_event['deadline_time']}")
        else:
            print("\nNo current or upcoming gameweek found. The season might be over or hasn't started yet.")

        team_data = self.fetch_team_data()
        if team_data:
            print(f"\nTeam Information for ID {self.team_id}:")
            print(f"Team Name: {team_data['name']}")
            print(f"Overall Rank: {team_data['summary_overall_rank']}")
            print(f"Total Points: {team_data['summary_overall_points']}")
        else:
            print(f"\nUnable to fetch data for team ID {self.team_id}.")
            print("This could be because:")
            print("1. The team ID is incorrect.")
            print("2. The team hasn't been created for the new season yet.")
            print("3. The API structure has changed.")

if __name__ == "__main__":
    team_id = 4193107
    diagnostics = Diagnostics(team_id)
    diagnostics.run_diagnostics()