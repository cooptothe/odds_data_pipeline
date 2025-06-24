import requests
from utils.teams import normalize_team

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
}

# helper function to parse odds
# DraftKings uses a special format for negative odds, e.g. "−150" instead
def parse_odds(odds_str):
    return int(odds_str.replace("−", "-"))


DK_URL = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusla/v1/leagues/84240"

def scrape_draftkings():
    print("📡 Fetching DraftKings MLB odds...")
    try:
        res = requests.get(DK_URL, headers=HEADERS)
        res.raise_for_status()
        data = res.json()

        events = {e["id"]: e for e in data["events"]}

        markets_by_event = {}
        for market in data["markets"]:
            eid = market["eventId"]
            if eid not in markets_by_event:
                markets_by_event[eid] = {}
            markets_by_event[eid][market["name"]] = market["id"]

        # Group selections by marketId
        selections_by_market = {}
        for s in data["selections"]:
            mid = s["marketId"]
            if mid not in selections_by_market:
                selections_by_market[mid] = []
            selections_by_market[mid].append(s)

        results = []

        for event_id, event in events.items():
            participants = {p["venueRole"]: p["name"] for p in event["participants"]}
            home = participants.get("Home")
            away = participants.get("Away")
            start = event["startEventDate"]
            event_markets = markets_by_event.get(event_id, {})

            game = {
                "game_id": event_id,
                "game_date": start,
                "home_team": normalize_team(home),
                "away_team": normalize_team(away),
                "moneyline_home": None,
                "moneyline_away": None,
                "run_line_home": None,
                "run_line_away": None,
                "run_line_odds_home": None,
                "run_line_odds_away": None,
                "total": None,
                "over_odds": None,
                "under_odds": None
            }

            # Moneyline
            ml_market_id = event_markets.get("Moneyline")
            if ml_market_id:
                for s in selections_by_market.get(ml_market_id, []):
                    odds = s["displayOdds"]["american"]
                    if s["outcomeType"] == "Home":
                        game["moneyline_home"] = parse_odds(odds)
                    elif s["outcomeType"] == "Away":
                        game["moneyline_away"] = parse_odds(odds)

            # Run Line (Spread)
            rl_market_id = event_markets.get("Run Line")
            if rl_market_id:
                for s in selections_by_market.get(rl_market_id, []):
                    odds = s["displayOdds"]["american"]
                    points = s.get("points")
                    if s["outcomeType"] == "Home":
                        game["run_line_home"] = float(points)
                        game["run_line_odds_home"] = parse_odds(odds)
                    elif s["outcomeType"] == "Away":
                        game["run_line_away"] = float(points)
                        game["run_line_odds_away"] = parse_odds(odds)

            # Total
            total_market_id = event_markets.get("Total")
            if total_market_id:
                for s in selections_by_market.get(total_market_id, []):
                    odds = s["displayOdds"]["american"]
                    points = s.get("points")
                    if s["outcomeType"] == "Over":
                        game["total"] = float(points)
                        game["over_odds"] = parse_odds(odds)
                    elif s["outcomeType"] == "Under":
                        game["under_odds"] = parse_odds(odds)

            results.append(game)

        return results

    except Exception as e:
        print("❌ Error during DraftKings scrape:", e)
        return []

# 🧪 Test run
if __name__ == "__main__":
    games = scrape_draftkings()
    print(f"✅ Found {len(games)} games")
    for g in games[:3]:
        print(g)
