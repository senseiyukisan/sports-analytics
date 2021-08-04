import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

# Read in data
players = pd.read_csv("data/players.csv")
clubs = pd.read_csv("data/clubs.csv")
appearances = pd.read_csv("data/appearances.csv")
games = pd.read_csv("data/games.csv")

# Create list of top league ids
top_league_ids = ["GB1", "ES1", "L1", "IT1", "FR1"]

# Filter on top leagues (England, Spain, Germany, Italy, France)
# Add column league_id, initialize with None
players["league_id"] = None
for ind, row in players.iterrows():
    club_id = row["club_id"]
    # Use club_id to find the league_id from clubs dataframe
    mask = clubs['club_id'] == club_id
    club = clubs[mask].reset_index()
    try:
        league_id = club["league_id"][0]
    except:
        pass
    players.at[ind, "league_id"] = league_id

players = players[players["league_id"].isin(top_league_ids)]
clubs = clubs[clubs["league_id"].isin(top_league_ids)]
appearances = appearances[appearances["league_id"].isin(top_league_ids)]
games = games[games["league_code"].isin(top_league_ids)]

###############
### players ###
###############

# Add column market_value, initialize with 0
players["market_value"] = 0

# Fix headers
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

# Scrape market_value from transfermarkt.de
for ind, row in tqdm(players.iterrows()):
    try:
        url = row["url"]
        request_response = requests.get(url, headers=headers)
        
        # Parse request_response into beautifulsoup object
        html_content = BeautifulSoup(request_response.content, 'html.parser')
        
        # The find_all () method is able to return all tags that meet restrictions within parentheses
        market_value_html = html_content.find_all("div", {"class": "dataMarktwert"})[0]

        market_value = market_value_html.text.split("£")[1].split(" ")[0].strip('\t\r\n')

        if market_value.endswith("m"):
            market_value = float(market_value.split("m")[0]) * 1000000
        else:
            market_value = float(market_value.split("Th.")[0]) * 1000
        
        players.at[ind, "market_value"] = market_value
        
    except:
        pass

# Feature Engineering: Initialize new columns
players["games"] = 0
players["minutes_played"] = 0
players["goals"] = 0
players["assists"] = 0
players["wins"] = 0
players["draws"] = 0
players["losses"] = 0
players["yellow_cards"] = 0
players["red_cards"] = 0
players["age"] = None

# current_date will be chosen as the production date of data  
current_date = "2021-06-08"
current_date = datetime.strptime(current_date, "%Y-%m-%d")

def calc_age(date_of_birth, current_date):
    """
        Calculates the age based on birth date and current date
    """
    try:
        date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
    except:
        return None
    return current_date.year - date_of_birth.year - ((current_date.month, current_date.day) < (date_of_birth.month, date_of_birth.day))

# Fill column age
for ind, row in players.iterrows():
    age = calc_age(row["date_of_birth"], current_date)
    players.at[ind, "age"] = age

# Fill sub_position column for Goalkeepers
players.loc[players['position'] == "Goalkeeper", "sub_position"] = "Goalkeeper"

# Add and fill club_name column 
players["club_name"] = None
for ind, row in players.iterrows():
    pretty_name = clubs.loc[clubs["club_id"] == row["club_id"], "pretty_name"].item()
    players.at[ind, "club_name"] = pretty_name

# Create grouped dataframe object to get sum of minutes played, goals scored, assists provied, yellow and red cards received
# for each player during the season
player_stats = appearances[["player_id", "minutes_played", "goals", "assists", "yellow_cards", "red_cards"]].groupby("player_id").sum()

# Create grouped dataframe object to get the number of games for each player during the season
game_stats = appearances[["player_id", "game_id"]].groupby("player_id").count()

# Fill those columns 
for ind, row in players.iterrows():
    player_id = row["player_id"]
    try:
        players.at[ind, "minutes_played"] = player_stats.loc[player_id]["minutes_played"]
        players.at[ind, "goals"] = player_stats.loc[player_id]["goals"]
        players.at[ind, "assists"] = player_stats.loc[player_id]["assists"]
        players.at[ind, "yellow_cards"] = player_stats.loc[player_id]["yellow_cards"]
        players.at[ind, "red_cards"] = player_stats.loc[player_id]["red_cards"]
        players.at[ind, "games"] = game_stats.loc[player_id]["game_id"]
    except:
        pass

# Create grouped dataframe object to get a list of every game appearance for each player
player_games = appearances[["player_id", "game_id", "player_club_id"]] \
        .groupby(["player_id", "player_club_id"])["game_id"] \
        .apply(list).reset_index(name='games') 

# Create a dictionary containing information about each players game outcomes if they played at least 1 minute in that game
results_dict = {}
for ind, row in player_games.iterrows():
    player_id = row["player_id"]
    results_dict[player_id] = {"wins": 0, "draws": 0, "losses": 0}
    for game_played in row["games"]:
        mask = games['game_id'] == game_played
        game = games[mask]

        home_goals = int(game["home_club_goals"])
        away_goals = int(game["away_club_goals"])

        if home_goals > away_goals:
            result = "home"
        elif home_goals < away_goals:
            result = "away"
        else:
            result = "draw"
        
        if row["player_club_id"] == int(game["home_club_id"]):
            if result == "home":
                results_dict[player_id]["wins"] += 1
            elif result == "away":
                results_dict[player_id]["losses"] += 1
            else:
                results_dict[player_id]["draws"] += 1
        elif row["player_club_id"] == int(game["away_club_id"]):
            if result == "home":
                results_dict[player_id]["losses"] += 1
            elif result == "away":
                results_dict[player_id]["wins"] += 1
            else:
                results_dict[player_id]["draws"] += 1
        else:
            print(f"player_club_id: {row['player_club_id']}\nhome_club_id: {game['home_club_id']}\naway_club_id: {game['away_club_id']}")

# Fill all columns using the results_dict
for ind, row in players.iterrows():
    player_id = row["player_id"]
    try:
        players.at[ind, "wins"] = results_dict[player_id]["wins"]
        players.at[ind, "draws"] = results_dict[player_id]["draws"]
        players.at[ind, "losses"] = results_dict[player_id]["losses"]
    except:
        pass

#############
### clubs ###
#############

# Sum up market values for each team
market_values_clubs = players[["club_id", "market_value"]].groupby(["club_id"], as_index=False).sum()

# Create dictionary {club_id: market_value}
market_values_clubs_dict = dict(zip(market_values_clubs["club_id"], market_values_clubs["market_value"]))

# Add column market_value, initialize with 0
clubs["market_value"] = 0
for ind, row in clubs.iterrows():
    club_id = row["club_id"]
    clubs.at[ind, "market_value"] = market_values_clubs_dict[club_id]

###################
### appearances ###
###################

# Create dictionary {player_id: market_value}
market_values_players_dict = dict(zip(players["player_id"], players["market_value"]))

# Add column weighted_market_value, initialize with 0
appearances["weighted_market_value"] = 0 

# Depending on how many minutes a player is on the pitch we can calculate a weighted market value for each team appearance
# For instance if a player is on the pitch the whole game (90 minutes) his weighted market value will be the same as his 
# general market value. If on the other hand the player only plays 45 minutes his weighted market value will only be half
# of his general market value for this particular appearance. This way we can calculate a weighted market value for each team
# in a match. 
for ind, row in appearances.iterrows():
    player_market_value = market_values_players_dict[row["player_id"]]
    player_weighted_market_value = player_market_value * (row["minutes_played"]/90)
    appearances.at[ind, "weighted_market_value"] = player_weighted_market_value

#############
### games ###
#############

# Add and fill home_club_name and away_club_name columns
games["home_club_name"] = None
games["away_club_name"] = None
for ind, row in games.iterrows():
    home_pretty_name = clubs.loc[clubs["club_id"] == row["home_club_id"], "pretty_name"].item()
    away_pretty_name = clubs.loc[clubs["club_id"] == row["away_club_id"], "pretty_name"].item()

    games.at[ind, "home_club_name"] = home_pretty_name
    games.at[ind, "away_club_name"] = away_pretty_name

# Add columns market_value_home and market_value_away, initialize with 0
games["market_value_home"] = 0
games["market_value_away"] = 0
for ind, row in games.iterrows():
    home_club_id = row["home_club_id"]
    away_club_id = row["away_club_id"]
    games.at[ind, "market_value_home"] = market_values_clubs_dict[home_club_id]
    games.at[ind, "market_value_away"] = market_values_clubs_dict[away_club_id]

# Create a grouped dataframe object to get the weighted market value for each player and each game
appearances_weighted_market_value = appearances[["game_id", "player_club_id", "weighted_market_value"]].groupby(["game_id", "player_club_id"], as_index=False).sum()

# Add columns weighted_market_value_home and weighted_market_value_away, initialize with 0
games["weighted_market_value_home"] = 0
games["weighted_market_value_away"] = 0
for ind, row in games.iterrows():
    # For each game find all players individual weighted market value 
    weighted_market_values = appearances_weighted_market_value[appearances_weighted_market_value["game_id"] == row["game_id"]][["player_club_id", "weighted_market_value"]]
    weighted_market_values_dict = dict(zip(weighted_market_values["player_club_id"], weighted_market_values["weighted_market_value"]))
    home_club_id = row["home_club_id"]
    away_club_id = row["away_club_id"]
    games.at[ind, "weighted_market_value_home"] = weighted_market_values_dict[home_club_id]
    games.at[ind, "weighted_market_value_away"] = weighted_market_values_dict[away_club_id]

# Create CSV files 
players.to_csv("data/players_updated.csv", index=False)
clubs.to_csv("data/clubs_updated.csv", index=False)
games.to_csv("data/games_updated.csv", index=False)
appearances.to_csv("data/appearances_updated.csv", index=False)