import psycopg2
from config import DB_CONFIG
from utils.ev import no_vig_prob, expected_value, decimal_to_american, kelly_fraction
from datetime import datetime
import pytz
import argparse
import csv
import os
import json
from utils.discord import send_discord_alert

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # store in .env

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

SESSION_FILE = "session.json"

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {
        "bankroll": bankroll,
        "risked": 0,
        "won": 0,
        "bets": []
    }

def save_session(session):
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)

LINE_CACHE_FILE = "line_cache.json"

def load_line_cache():
    if os.path.exists(LINE_CACHE_FILE):
        with open(LINE_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_line_cache(cache):
    with open(LINE_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)



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
    output_file = "ev_bets.csv"
    session = load_session()


    # Create or overwrite file and write header
    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "date", "sport", "home_team", "away_team", "market", "side", "line", 
            "sportsbook", "odds_decimal", "odds_american", "win_prob", "ev_percent", "kelly_stake"
        ])
    

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

    
    line_cache = load_line_cache()

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
                    key = f"{home}_{away}_{sport_title}_{market}_{side}_{book}"
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
                        prev_entry = line_cache.get(key)

                        change_indicator = ""
                        if prev_entry is None:
                            change_indicator = "✅ New"
                        elif abs(prev_entry["ev_pct"] - ev_pct) >= 0.1:
                            if ev_pct > prev_entry["ev_pct"]:
                                change_indicator = "📈 EV↑"
                            else:
                                change_indicator = "📉 EV↓"
                        elif price != prev_entry["price"]:
                            change_indicator = "⚠️ Line moved"


                        line = f"    {book.title():<10} | Odds: {odds_str:<6} | EV: {ev_str}"
                        if stake_str:
                            line += f" | Kelly Stake: {stake_str}"
                        if ev_pct is None or ev_pct < 3 or ev_pct > 14:
                            continue  # skip out-of-range EV%
                        emoji = highlight_ev(ev_pct)
                        line += f" {emoji} {change_indicator}"
                        if 3 <= ev_pct <= 14:
                            with open(output_file, mode="a", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    format_ct_time(game_dt), sport_title, home, away,
                                    market_label, side.title(), line_label.strip("()").strip(),
                                    book.title(), price, american, win_prob, ev_pct, round(stake_amt, 2)
                                ])
                                # Update session stats
                                session["risked"] += stake_amt
                                session["bets"].append({
                                    "book": book,
                                    "game": f"{away} @ {home}",
                                    "market": market,
                                    "side": side,
                                    "odds": price,
                                    "win_prob": round(win_prob, 4),
                                    "ev_pct": round(ev_pct, 2),
                                    "stake": round(stake_amt, 2)
                                })
                        print(line)

                
    line_cache[key] = {
    "ev_pct": ev_pct,
    "price": price
}


        
    conn.close()
    save_session(session)
    save_line_cache(line_cache)


    print("\n📊 Session Summary:")
    print(f"Bankroll: ${session['bankroll']:.2f}")
    print(f"Total Risked: ${session['risked']:.2f}")
    print(f"Bets Logged: {len(session['bets'])}")


    if session["bets"]:
        top_bets = session["bets"][-5:]  # last 5 bets this run
        discord_msg = "**📈 Top EV Bets Alert**\n"
        for bet in top_bets:
            emoji = highlight_ev(bet["ev_pct"])
            discord_msg += (
                f"{bet['game']} | {bet['market']} - {bet['side']} | "
                f"Odds: {bet['odds']} | EV: {bet['ev_pct']}% | Stake: ${bet['stake']} {emoji}\n"
            )
        send_discord_alert(discord_msg, DISCORD_WEBHOOK_URL)



if __name__ == "__main__":
    print("🚀 Calculating EV% across all markets...")
    calculate_ev()
    print("\n✅ EV% analysis complete.")
