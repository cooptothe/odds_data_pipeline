import psycopg2
from config import DB_CONFIG

def connect():
    return psycopg2.connect(**DB_CONFIG)

def insert_game(conn, game):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO games (game_date, home_team, away_team)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (game["game_date"], game["home_team"], game["away_team"]))
        return cur.fetchone()[0]

def find_or_create_game(conn, game):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id FROM games
            WHERE home_team = %s AND away_team = %s AND DATE(game_date) = DATE(%s)
        """, (game["home_team"], game["away_team"], game["game_date"]))
        row = cur.fetchone()

        if row:
            return row[0]
        return insert_game(conn, game)

def insert_odds(conn, game_id, game, sportsbook="FanDuel"):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO odds (
                game_id, sportsbook, moneyline_home, moneyline_away,
                spread_home, spread_away, spread_odds_home, spread_odds_away,
                total, over_odds, under_odds
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            game_id, sportsbook,
            game["moneyline_home"], game["moneyline_away"],
            game["spread_home"], game["spread_away"],
            game["spread_odds_home"], game["spread_odds_away"],
            game["total"], game["over_odds"], game["under_odds"]
        ))
