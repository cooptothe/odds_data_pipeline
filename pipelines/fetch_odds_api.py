
from scrapers.odds_api_scraper import fetch_odds_for_sport, parse_game
from db.insert import connect, insert_game, insert_odds

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

def run():
    conn = connect()

    for sport_key in SPORT_KEYS:
        games = fetch_odds_for_sport(sport_key)
        for game_json in games:
            game_obj, odds_list = parse_game(game_json)
            game_id = insert_game(conn, game_obj)
            insert_odds(conn, game_id, odds_list)

    conn.close()

if __name__ == "__main__":
    run()
