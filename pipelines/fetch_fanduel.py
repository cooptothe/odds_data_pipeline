from scrapers.fanduel import scrape_fanduel
from db.insert import connect, insert_game, insert_odds

def run_pipeline():
    games = scrape_fanduel()
    conn = connect()

    for game in games:
        game_id = insert_game(conn, game)
        insert_odds(conn, game_id, game)

    conn.commit()
    conn.close()
    print(f"✅ Inserted {len(games)} games from FanDuel")

if __name__ == "__main__":
    run_pipeline()
