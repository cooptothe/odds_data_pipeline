from scrapers import draftkings
from db.insert import connect, find_or_create_game, insert_draftkings_odds, insert_odds

def run():
    print("🚀 Starting DraftKings pipeline...")
    games = draftkings.scrape_draftkings()
    print(f"📦 Fetched {len(games)} games")

    conn = connect()
    inserted = 0

    for game in games:
        game_id = find_or_create_game(conn, game)
        insert_odds(conn, game_id, game, sportsbook="DraftKings")
        inserted += 1

    conn.commit()
    conn.close()

    print(f"✅ Inserted odds for {inserted} DraftKings games")

if __name__ == "__main__":
    run()
