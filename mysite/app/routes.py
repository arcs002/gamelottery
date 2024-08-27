from flask import request, render_template, redirect, url_for
from app import app
import random
import datetime
import requests
import xml.etree.ElementTree as ET
from app.models import load_data, save_data, clean_plays_data, GAMES_FILE, HISTORY_FILE

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
    response = requests.get('https://boardgamegeek.com/xmlapi2/plays?username=doony&mindate=2023-01-01')
    root = ET.fromstring(response.content)
    
    plays = []
    
    for play in root.findall('play'):
        date = play.get('date')
        location = play.get('location')
        game_name = play.find('item').get('name')
        players = []
        for player in play.find('players').findall('player'):
            player_name = player.get('name')
            player_score = player.get('score')
            player_win = player.get('win')
            players.append({
                'name': player_name,
                'score': player_score,
                'win': player_win
            })
        plays.append({
            'date': date,
            'location': location,
            'game_name': game_name,
            'players': players
        })
    
    # Clean the plays data
    plays = clean_plays_data(plays)
    
    # Count the wins in the cleaned data
    win_counts = {}
    for play in plays:
        for player in play['players']:
            if player['win'] == "1":
                if player['name'] not in win_counts:
                    win_counts[player['name']] = 0
                win_counts[player['name']] += 1
    
    return render_template('plays.html', plays=plays, win_counts=win_counts)