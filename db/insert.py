import psycopg2
from config import DB_CONFIG

def connect():
    return psycopg2.connect(**DB_CONFIG)

def insert_game(conn, game_obj):
    with conn.cursor() as cur:
        # Ensure sport exists and get sport_id
        cur.execute("""
            INSERT INTO sports (key, title)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET title = EXCLUDED.title
            RETURNING id
        """, (game_obj["sport_key"], game_obj["sport_key"].split("_")[-1].upper()))
        sport_id = cur.fetchone()[0]

        # Insert game if it doesn't exist
        cur.execute("""
            INSERT INTO games (id, sport_id, game_date, home_team, away_team, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            game_obj["id"], sport_id, game_obj["game_date"],
            game_obj["home_team"], game_obj["away_team"], game_obj["status"]
        ))

        conn.commit()
        return game_obj["id"]

def insert_odds(conn, game_id, odds_list):
    with conn.cursor() as cur:
        for odds in odds_list:
            cur.execute("""
                INSERT INTO odds (
                    game_id, sportsbook, market, side,
                    price, decimal_price, implied_prob, point
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                game_id,
                odds["sportsbook"], odds["market"], odds["side"],
                odds["price"], odds["decimal_price"],
                odds["implied_prob"], odds["point"]
            ))
        conn.commit()
