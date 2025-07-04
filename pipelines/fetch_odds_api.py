import argparse
from scrapers.odds_api_scraper import fetch_odds_for_sport, parse_game
from db.insert import connect, insert_game, insert_odds

# CLI argument
parser = argparse.ArgumentParser()
parser.add_argument("--sport", type=str, required=True, help="Sport key to fetch (e.g. baseball_mlb)")
args = parser.parse_args()



SPORT_KEYS = [
        "baseball_mlb",
        "basketball_nba",
        "basketball_wnba",                 # WNBA (NBA is offseason)
        "americanfootball_nfl",            # NFL
        "americanfootball_ncaaf",          # College Football
        "mma_mixed_martial_arts",          # UFC / MMA
        "boxing_boxing",                   # Boxing
        "hockey_nhl",                      # NHL
        "soccer_epl",                      # Premier League
        "soccer_usa_mls",                  # MLS
        "soccer_italy_serie_a",            # Serie A
        "soccer_germany_bundesliga",       # Bundesliga
        "soccer_france_ligue_one",         # Ligue 1
        "soccer_mexico_ligamx",            # Liga MX
        "tennis_atp_wimbledon",            # Wimbledon ATP
        "tennis_wta_wimbledon"             # Wimbledon WTA
]

def cleanup_old_games(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM games WHERE game_date < NOW() - INTERVAL '1 day'")
    conn.commit()


def run(sport_key):
    conn = connect()
    # 🔥 Clean up old/stale games before fetching new ones
    cleanup_old_games(conn)
    games = fetch_odds_for_sport(sport_key)

    for game_json in games:
        game_obj, odds_list = parse_game(game_json)
        game_id = insert_game(conn, game_obj)
        insert_odds(conn, game_id, odds_list)

    conn.close()

if __name__ == "__main__":
    run(args.sport)