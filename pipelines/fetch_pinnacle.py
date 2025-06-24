from scrapers import pinnacle
from db.insert import connect, find_game, insert_odds

def run():
    print("🚀 Starting Pinnacle pipeline...")
    games = pinnacle.scrape_pinnacle()
    print(f"📦 Fetched {len(games)} Pinnacle games")

    conn = connect()
    inserted = 0

    for game in games:
        game_id = find_game(conn, game)
        if not game_id:
            print(f"⚠️ Skipping unmatched Pinnacle game: {game['away_team']} @ {game['home_team']}")
            continue
        insert_odds(conn, game_id, game, sportsbook="Pinnacle")
        inserted += 1


    conn.commit()
    conn.close()

    print(f"✅ Inserted odds for {inserted} Pinnacle games")

if __name__ == "__main__":
    run()
