from flask import Flask, request, render_template, redirect, url_for
import random
import datetime

app = Flask(__name__)

# In-memory database (dictionary) to store games and their votes
games = {}

# List to store the history of lotteries
lottery_history = []

@app.route('/')
def home():
    return redirect(url_for('suggest_game'))

@app.route('/suggest-game', methods=['GET', 'POST'])
def suggest_game():
    if request.method == 'POST':
        game = request.form['game']
        if game not in games:
            games[game] = 0
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

        return render_template('lottery.html', selected_game=selected_game, lottery_history=lottery_history)

    return render_template('lottery.html', selected_game=None, lottery_history=lottery_history)

if __name__ == '__main__':
    app.run(debug=True)