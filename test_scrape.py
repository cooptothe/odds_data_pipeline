from scrapers.draftkings import scrape_draftkings

games = scrape_draftkings()

print(f"Found {len(games)} games")
for game in games[:3]:
    print(game)
