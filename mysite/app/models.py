import json
import os

# File paths for JSON storage
GAMES_FILE = 'games.json'
HISTORY_FILE = 'history.json'

# Load data from JSON files
def load_data():
    if os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, 'r') as file:
            games = json.load(file)
    else:
        games = {}

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            lottery_history = json.load(file)
    else:
        lottery_history = []

    return games, lottery_history

# Save data to JSON files
def save_data(games, lottery_history):
    with open(GAMES_FILE, 'w') as file:
        json.dump(games, file)

    with open(HISTORY_FILE, 'w') as file:
        json.dump(lottery_history, file)

# Clean plays data
def clean_plays_data(plays):
    valid_players = {"Cassiano", "Gustavo Pichiteli", "Alexandre C."}
    cleaned_plays = []
    
    for play in plays:
        if any(player['name'] in valid_players for player in play['players']):
            cleaned_plays.append(play)
    
    return cleaned_plays