import requests
from config import ODDS_API_KEY

URL = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"

def scrape_pinnacle():
    print("📡 Fetching Pinnacle odds via Odds API...")

    params = {
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "bookmakers": "pinnacle",
        "apiKey": ODDS_API_KEY
    }

    try:
        response = requests.get(URL, params=params)
        response.raise_for_status()
        data = response.json()
        results = []

        for game in data:
            home = game["home_team"]
            away = game["away_team"]
            start = game["commence_time"]

            game_obj = {
                "game_id": game["id"],
                "game_date": start,
                "home_team": home,
                "away_team": away,
                "moneyline_home": None,
                "moneyline_away": None,
                "spread_home": None,
                "spread_away": None,
                "spread_odds_home": None,
                "spread_odds_away": None,
                "total": None,
                "over_odds": None,
                "under_odds": None
            }

            # Safely access Pinnacle markets
            bookmakers = game.get("bookmakers", [])
            if not bookmakers:
                continue

            pinnacle = next((b for b in bookmakers if b["key"] == "pinnacle"), None)
            if not pinnacle:
                continue

            for market in pinnacle.get("markets", []):
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        if outcome["name"] == home:
                            game_obj["moneyline_home"] = outcome["price"]
                        elif outcome["name"] == away:
                            game_obj["moneyline_away"] = outcome["price"]
                elif market["key"] == "spreads":
                    for outcome in market["outcomes"]:
                        if outcome["name"] == home:
                            game_obj["spread_home"] = outcome["point"]
                            game_obj["spread_odds_home"] = outcome["price"]
                        elif outcome["name"] == away:
                            game_obj["spread_away"] = outcome["point"]
                            game_obj["spread_odds_away"] = outcome["price"]
                elif market["key"] == "totals":
                    for outcome in market["outcomes"]:
                        game_obj["total"] = outcome["point"]
                        if outcome["name"] == "Over":
                            game_obj["over_odds"] = outcome["price"]
                        elif outcome["name"] == "Under":
                            game_obj["under_odds"] = outcome["price"]

            results.append(game_obj)

        return results

    except Exception as e:
        print("❌ Error fetching Pinnacle odds:", e)
        return []

# 🧪 Test
if __name__ == "__main__":
    games = scrape_pinnacle()
    print(f"✅ Found {len(games)} Pinnacle games")
    for g in games[:3]:
        print(g)
