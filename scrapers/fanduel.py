import requests

FANDUEL_URL = "https://sportsbook.fanduel.com/cache/psmg/UK/en/filters/baseball/mlb.json"

def fetch_fanduel_mlb_odds():
    try:
        response = requests.get(FANDUEL_URL)
        response.raise_for_status()
        data = response.json()

        events = data.get("events", [])
        results = []

        for event in events:
            home = event.get("homeTeamName")
            away = event.get("awayTeamName")
            date = event.get("eventDate")
            display_group = event.get("displayGroup", {})
            markets = display_group.get("markets", [])

            def get_price(outcome):
                return outcome.get("price", {}).get("american") if outcome else None

            def find_outcome(market, label):
                return next((o for o in market.get("outcomes", []) if o.get("label") == label or o.get("team") == label), None)

            moneyline = next((m for m in markets if m.get("marketType") == "MONEYLINE"), {})
            spread = next((m for m in markets if m.get("marketType") == "SPREAD"), {})
            total = next((m for m in markets if m.get("marketType") == "TOTAL_POINTS"), {})

            result = {
                "game_date": date,
                "home_team": home,
                "away_team": away,
                "moneyline_home": get_price(find_outcome(moneyline, home)),
                "moneyline_away": get_price(find_outcome(moneyline, away)),
                "spread_home": find_outcome(spread, home).get("handicap") if find_outcome(spread, home) else None,
                "spread_away": find_outcome(spread, away).get("handicap") if find_outcome(spread, away) else None,
                "spread_odds_home": get_price(find_outcome(spread, home)),
                "spread_odds_away": get_price(find_outcome(spread, away)),
                "total": find_outcome(total, "Over").get("handicap") if find_outcome(total, "Over") else None,
                "over_odds": get_price(find_outcome(total, "Over")),
                "under_odds": get_price(find_outcome(total, "Under")),
            }

            results.append(result)

        return results

    except Exception as e:
        print(f"Error fetching FanDuel odds: {e}")
        return []

# 🧪 Quick test
if __name__ == "__main__":
    odds = fetch_fanduel_mlb_odds()
    for game in odds[:3]:  # just print first 3 for brevity
        print(game)
