from flask import Flask, request, render_template, redirect, url_for
import random
import datetime
import json
import os
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

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

# Initialize data
games, lottery_history = load_data()

@app.route('/')
def home():
    return redirect(url_for('suggest_game'))

@app.route('/suggest-game', methods=['GET', 'POST'])
def suggest_game():
    if request.method == 'POST':
        game = request.form['game']
        if game not in games:
            games[game] = 0
            save_data(games, lottery_history)
        return redirect(url_for('suggest_game'))
    
    return render_template('suggest_game.html', games=games)

@app.route('/upvote', methods=['GET', 'POST'])
def upvote():
    if request.method == 'POST':
        game = request.form['game']
        if game in games:
            if request.form['action'] == 'upvote':
                games[game] += 1
            elif request.form['action'] == 'downvote':
                games[game] -= 1
                if games[game] < 0:
                    del games[game]  # Remove the game if its vote count is negative
            save_data(games, lottery_history)
        return redirect(url_for('upvote'))
    
    return render_template('upvote.html', games=games)

@app.route('/lottery', methods=['GET', 'POST'])
def lottery():
    if request.method == 'POST':
        if not games:
            return "No games available for lottery!"

        weighted_games = []
        for game, votes in games.items():
            weighted_games.extend([game] * max(1, votes))
        
        selected_game = random.choice(weighted_games)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lottery_history.append((selected_game, timestamp))
        save_data(games, lottery_history)
        
        return render_template('lottery.html', selected_game=selected_game, lottery_history=lottery_history)
    
    return render_template('lottery.html', selected_game=None, lottery_history=lottery_history)

@app.route('/plays')
def plays():
    response = requests.get('https://boardgamegeek.com/xmlapi2/plays?username=doony')
    root = ET.fromstring(response.content)
    
    plays = []
    for play in root.findall('play'):
        date = play.get('date')
        location = play.get('location')
        game_name = play.find('item').get('name')
        players = []
        for player in play.find('players').findall('player'):
            players.append({
                'name': player.get('name'),
                'score': player.get('score'),
                'win': player.get('win')
            })
        plays.append({
            'date': date,
            'location': location,
            'game_name': game_name,
            'players': players
        })
    
    return render_template('plays.html', plays=plays)

if __name__ == '__main__':
    app.run(debug=True)