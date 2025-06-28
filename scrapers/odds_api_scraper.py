# scrapers/odds_api_scraper.py
import requests
from config import ODDS_API_KEY
from utils.teams import normalize_team
from math import isfinite


ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4/sports"

# Books
SHARP_BOOKS = ["pinnacle", "bookmaker", "circa", "prophetx"]
RECREATIONAL_BOOKS = ["draftkings", "fanduel", "espnbet", "caesars", "fanatics"]
ALL_BOOKS = SHARP_BOOKS + RECREATIONAL_BOOKS

MARKETS = "h2h,spreads,totals"  # Supported markets

def decimal_to_american(decimal_odds):
    if not decimal_odds or not isfinite(decimal_odds):
        return None
    if decimal_odds <= 1.0:
        return None  # Invalid or placeholder line
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100 + 0.5)
    else:
        return int(-100 / (decimal_odds - 1) + 0.5)

def decimal_to_implied_prob(decimal_odds):
    return round(1 / decimal_odds, 4) if decimal_odds and decimal_odds > 1 else None

def parse_game(game_json):
    game_id = game_json["id"]
    sport_key = game_json["sport_key"]
    home_team = normalize_team(game_json["home_team"])
    away_team = normalize_team(game_json["away_team"])
    game_date = game_json["commence_time"]
    status = game_json.get("status", "upcoming")

    game_obj = {
        "id": game_id,
        "sport_key": sport_key,
        "game_date": game_date,
        "home_team": home_team,
        "away_team": away_team,
        "status": status
    }

    odds_list = []
    for bookmaker in game_json.get("bookmakers", []):
        sportsbook = bookmaker["key"]

        for market in bookmaker.get("markets", []):
            market_key = market["key"]

            for outcome in market.get("outcomes", []):
                outcome_name = outcome.get("name")
                decimal_price = outcome.get("price")

                if not outcome_name or not decimal_price or decimal_price <= 1.0:
                    continue  # Skip invalid or placeholder odds

                american_price = decimal_to_american(decimal_price)
                implied_prob = decimal_to_implied_prob(decimal_price)
                point = outcome.get("point")

                # Determine side
                if market_key == "h2h":
                    if outcome_name == home_team:
                        side = "home"
                    elif outcome_name == away_team:
                        side = "away"
                    else:
                        continue
                elif market_key == "spreads":
                    side = "home" if outcome_name == home_team else "away"
                elif market_key == "totals":
                    side = outcome_name.lower()
                else:
                    continue  # Ignore unknown market type

                odds_list.append({
                    "sportsbook": sportsbook,
                    "market": market_key,
                    "side": side,
                    "decimal_price": decimal_price,
                    "price": american_price,
                    "implied_prob": implied_prob,
                    "point": point
                })


    return game_obj, odds_list


def fetch_odds_for_sport(sport_key: str, region: str = "us", markets: str = MARKETS):
    print(f"📡 Fetching odds for sport: {sport_key}")
    
    url = f"{ODDS_API_BASE_URL}/{sport_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": region,
        "markets": markets,
        "bookmakers": ",".join(ALL_BOOKS)
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        games = response.json()
        print(f"✅ Retrieved {len(games)} games for {sport_key}")
        return games
    except Exception as e:
        print(f"❌ Error fetching odds for {sport_key}:", e)
        return []

if __name__ == "__main__":
    test_sports = [
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

    # for sport_key in test_sports:
    #     games = fetch_odds_for_sport(sport_key)
    #     if games:
    #         print(f"🧪 Sample: {games[0]['home_team']} vs {games[0]['away_team']}")