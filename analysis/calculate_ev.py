import psycopg2
from config import DB_CONFIG
from utils.ev import no_vig_prob, expected_value, decimal_to_american, kelly_fraction
from datetime import datetime
import pytz
import argparse
# import subprocess
# print("🔄 Running odds ingestion pipeline...")
# subprocess.run(["python", "-m", "pipelines.fetch_odds_api"])

parser = argparse.ArgumentParser()
parser.add_argument("--bankroll", type=float, default=100, help="Bankroll amount for Kelly staking")
args = parser.parse_args()
bankroll = args.bankroll



SHARP_BOOKS = ["pinnacle", "bookmaker", "circa", "prophetx"]
RECREATIONAL_BOOKS = ["draftkings", "fanduel", "espnbet", "caesars", "fanatics"]
MARKETS = ["h2h", "spreads", "totals"]

def connect():
    return psycopg2.connect(**DB_CONFIG)

def format_ct_time(utc_dt):
    # Convert UTC datetime to Central Time (America/Chicago)
    central = pytz.timezone("America/Chicago")
    utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
    ct = utc_dt.astimezone(central)
    return ct.strftime("%Y-%m-%d %I:%M %p CT")

def highlight_ev(ev_pct):
    if 3 <= ev_pct < 6:
        return "🧠"
    elif 6 <= ev_pct < 9:
        return "🔥"
    elif 9 <= ev_pct <= 14:
        return "💎"
    else:
        return ""



def calculate_ev():
    conn = connect()
    cur = conn.cursor()
    

    # Filter for today's games only
    cur.execute("""
    SELECT g.id, g.home_team, g.away_team, s.title, g.game_date, g.status
    FROM games g
    JOIN sports s ON g.sport_id = s.id
    WHERE 
        (g.status = 'live'
        OR (g.status = 'upcoming' AND g.game_date BETWEEN NOW() AND NOW() + INTERVAL '12 hours')
        )
    ORDER BY g.game_date
    """)

    games = cur.fetchall()

    for game_id, home, away, sport_title, game_dt, status in games:
        is_live = status == "live"
        live_tag = " 🛰️" if is_live else ""
        print(f"\n📊 {away} @ {home} ({sport_title} - {format_ct_time(game_dt)}){live_tag}")


        for market in MARKETS:
            cur.execute("""
                SELECT sportsbook, side, decimal_price, point
                FROM odds
                WHERE game_id = %s AND market = %s
            """, (game_id, market))

            rows = cur.fetchall()
            if not rows:
                continue

            # Organize odds by side
            odds_by_side = {}
            for book, side, price, point in rows:
                if price is None:
                    continue
                if side not in odds_by_side:
                    odds_by_side[side] = {}
                odds_by_side[side][book] = (float(price), point)

            for side, all_books in odds_by_side.items():
                # Get sharp prices for side
                sharp_prices = [v[0] for b, v in all_books.items() if b in SHARP_BOOKS and v[0] > 1]
                if len(sharp_prices) < 2:
                    continue

                prob_list = no_vig_prob(sharp_prices)
                win_prob = prob_list[0] if prob_list else None
                if win_prob is None:
                    continue

                # Use first available point as market line
                _, line_point = next(iter(all_books.values()))
                
                line_label = ""
                if market == "spreads":
                    line_label = f" ({line_point:+.1f})"
                elif market == "totals":
                    line_label = f" ({line_point:.1f})"

                market_label = market.title().replace("H2H", "Moneyline").replace("Spreads", "Spread").replace("Totals", "Total")
                print(f"  ➤ {market_label}{line_label} - {side.title()} (Win%: {win_prob:.2%})")

                for book in RECREATIONAL_BOOKS:
                    if book in all_books:
                        price, _ = all_books[book]
                        ev = expected_value(win_prob, price)
                        ev_pct = ev * 100 if ev is not None else None
                        american = decimal_to_american(price)
                        odds_str = f"{american:+}" if american is not None else "N/A"
                        ev_str = f"{ev_pct:+.2f}%" if ev_pct is not None else "N/A"
                        stake_frac = kelly_fraction(win_prob, price, factor=0.25)
                        stake_amt = bankroll * stake_frac
                        stake_str = f"${stake_amt:.2f}" if stake_amt >= 1 else ""

                        line = f"    {book.title():<10} | Odds: {odds_str:<6} | EV: {ev_str}"
                        if stake_str:
                            line += f" | Kelly Stake: {stake_str}"
                        if ev_pct is None or ev_pct < 3 or ev_pct > 14:
                            continue  # skip out-of-range EV%
                        emoji = highlight_ev(ev_pct)
                        line += f" {emoji}"
                        print(line)


                        


    conn.close()

if __name__ == "__main__":
    print("🚀 Calculating EV% across all markets...")
    calculate_ev()
    print("\n✅ EV% analysis complete.")
