import psycopg2
from config import DB_CONFIG
from utils.ev import no_vig_prob, expected_value, decimal_to_american, kelly_fraction
from datetime import datetime
import pytz
import argparse
import csv
import os
import json
from utils.discord_message import send_discord_alert
from collections import defaultdict
import decimal

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # store in .env

import subprocess
print("🔄 Running odds ingestion pipeline...")

print("Current working directory:", os.getcwd())
parser = argparse.ArgumentParser()
parser.add_argument("--bankroll", type=float, default=100, help="Bankroll amount for Kelly staking")
parser.add_argument("--sport", type=str, default=None, help="Sport key to filter (e.g. baseball_mlb)")
args = parser.parse_args()
bankroll = args.bankroll
sport_filter = args.sport

SHARP_BOOKS = ["pinnacle", "novig", "betonlineag"]
RECREATIONAL_BOOKS = ["draftkings", "fanduel", "espnbet", "betmgm"]
MARKETS = ["h2h", "spreads", "totals"]

def connect():
    return psycopg2.connect(**DB_CONFIG)

def format_ct_short_time(utc_dt):
    central = pytz.timezone("America/Chicago")
    utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
    ct = utc_dt.astimezone(central)
    return ct.strftime("%I:%M %p CT")

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
        try:
            with open(LINE_CACHE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ line_cache.json is corrupted. Resetting cache.")
            return {}
    return {}

def save_line_cache(cache):
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return obj
    with open(LINE_CACHE_FILE, "w") as f:
        json.dump(convert(cache), f, indent=2)

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
    # Run odds ingestion pipeline for the selected sport
    if sport_filter:
        subprocess.run(["python", "-m", "pipelines.fetch_odds_api", "--sport", sport_filter])
    else:
        subprocess.run(["python", "-m", "pipelines.fetch_odds_api", "--sport", "upcoming"])

    conn = connect()
    cur = conn.cursor()
    output_file = "ev_bets.csv"

    prev_session = load_session()
    prev_bet_keys = set(bet.get("key") for bet in prev_session.get("bets", []))
    session = load_session()

    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "date", "sport", "home_team", "away_team", "market", "side", "line",
            "sportsbook", "odds_decimal", "odds_american", "win_prob", "ev_percent", "kelly_stake"
        ])

    # Filter for today's games only, and by sport if specified
    if sport_filter:
        cur.execute("""
        SELECT g.id, g.home_team, g.away_team, s.title, g.game_date, g.status
        FROM games g
        JOIN sports s ON g.sport_id = s.id
        WHERE
        s.title = %s
        AND g.game_date > NOW() - INTERVAL '15 minutes'
        AND g.game_date < NOW() + INTERVAL '12 hours'
        ORDER BY g.game_date
        """, (sport_filter,))
    else:
        cur.execute("""
        SELECT g.id, g.home_team, g.away_team, s.title, g.game_date, g.status
        FROM games g
        JOIN sports s ON g.sport_id = s.id
        WHERE
        g.game_date > NOW() - INTERVAL '15 minutes'
        AND g.game_date < NOW() + INTERVAL '12 hours'
        ORDER BY g.game_date
        """)

    games = cur.fetchall()
    line_cache = load_line_cache()

    for game_id, home, away, sport_title, game_dt, status in games:
        is_live = status == "live"
        live_tag = " 🛰️" if is_live else ""
        print(f"\n📊 {away} @ {home} ({sport_title} - {format_ct_short_time(game_dt)}){live_tag}")

        for market in MARKETS:
            cur.execute("""
                SELECT sportsbook, side, decimal_price, point, betslip_link, market_link, event_link
                FROM odds
                WHERE game_id = %s AND market = %s AND fetched_at > NOW() - INTERVAL '30 minutes'
            """, (game_id, market))

            rows = cur.fetchall()
            if not rows:
                continue

            odds_by_side = {}
            for book, side, price, point, betslip_link, market_link, event_link in rows:
                link = betslip_link or market_link or event_link
                if price is None:
                    continue
                if side not in odds_by_side:
                    odds_by_side[side] = {}
                odds_by_side[side][book] = {
                    "price": float(price),
                    "point": point,
                    "link": link
                }

            for side, all_books in odds_by_side.items():
                sharp_prices = [v["price"] for b, v in all_books.items() if b in SHARP_BOOKS and v["price"] > 1]
                if len(sharp_prices) < 2:
                    continue

                prob_list = no_vig_prob(sharp_prices)
                win_prob = prob_list[0] if prob_list else None

                if not prob_list or len(prob_list) < 2:
                    continue

                market_width = abs(prob_list[0] - prob_list[1]) * 100
                if not (0 <= market_width <= 50):
                    continue

                if win_prob is None:
                    continue

                line_point = next(iter(all_books.values())).get("point")
                line_label = ""
                if market == "spreads":
                    line_label = f" ({line_point:+.1f})"
                elif market == "totals":
                    line_label = f" ({line_point:.1f})"

                market_label = market.title().replace("H2H", "Moneyline").replace("Spreads", "Spread").replace("Totals", "Total")
                print(f"  ➤ {market_label}{line_label} - {side.title()} (Win%: {win_prob:.2%})")

                for book in RECREATIONAL_BOOKS:
                    key = f"{home}_{away}_{sport_title}_{market}_{side}_{book}"
                    bet_key = f"{away}@{home}_{market}_{side}_{book}_{line_label.strip()}"
                    if any(bet.get("key") == bet_key for bet in session["bets"]):
                        continue
                    if book in all_books:
                        price = all_books[book]["price"]
                        link = all_books[book].get("link")
                        ev = expected_value(win_prob, price)
                        ev_pct = ev * 100 if ev is not None else None
                        american = decimal_to_american(price)
                        if american is None or american < -250 or american > +2000:
                            continue
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
                        if ev_pct is None or ev_pct < 1 or ev_pct > 14:
                            continue
                        emoji = highlight_ev(ev_pct)
                        line += f" {emoji} {change_indicator}"
                        if 1 <= ev_pct <= 14:
                            with open(output_file, mode="a", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    format_ct_short_time(game_dt), sport_title, home, away,
                                    market_label, side.title(), line_label.strip("()").strip(),
                                    book.title(), price, american, win_prob, ev_pct, round(stake_amt, 2)
                                ])

                                session["risked"] += stake_amt
                                session["bets"].append({
                                    "key": bet_key,
                                    "book": book,
                                    "game": f"{away} @ {home}",
                                    "market": market,
                                    "line": line_label,
                                    "sport": sport_title,
                                    "date": format_ct_short_time(game_dt),
                                    "side": side,
                                    "odds": price,
                                    "win_prob": round(win_prob, 4),
                                    "ev_pct": round(ev_pct, 2),
                                    "stake": round(stake_amt, 2),
                                    "link": link
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

    latest_bets = {}
    for bet in session["bets"]:
        bet_key = bet["key"]
        if (
            bet_key not in latest_bets
            or bet["ev_pct"] > latest_bets[bet_key]["ev_pct"]
            or bet["stake"] > latest_bets[bet_key]["stake"]
        ):
            latest_bets[bet_key] = bet

    session["bets"] = list(latest_bets.values())

    new_bets = session["bets"]

    MAX_DISCORD_LENGTH = 1900

    if new_bets:
        grouped_bets = defaultdict(list)
        for bet in new_bets:
            key = (bet["game"], bet["market"], bet["side"])
            grouped_bets[key].append(bet)

        messages = []
        now_ct = datetime.now(pytz.timezone("America/Chicago"))
        date_str = now_ct.strftime("%A, %B %d, %Y")
        time_str = now_ct.strftime("%I:%M%p").lstrip("0").lower()
        header_line = f"**📈 Top EV Bets Alert**\n**{date_str} | {time_str} CT**\n"
        current_msg = header_line
        printed_games = set()

        for (game, market, side), bets in grouped_bets.items():
            if not bets:
                continue

            unique_bets = {}
            for bet in bets:
                book = bet["book"]
                if (
                    book not in unique_bets
                    or bet["ev_pct"] > unique_bets[book]["ev_pct"]
                    or bet["stake"] > unique_bets[book]["stake"]
                ):
                    unique_bets[book] = bet
            bets = list(unique_bets.values())

            sport = bets[0].get("sport", "")
            win_prob = bets[0].get("win_prob", 0)
            line = bets[0].get("line", "")
            market_title = market.replace("h2h", "💰 Moneyline").replace("spreads", "📏 Spread").replace("totals", "📊 Total")

            time_str_bet = bets[0]["date"]
            header = f"\n🏟️ {game} ({sport} - {time_str_bet})\n"
            market_line = f"  ➤ {market_title} {line} | {side.title().upper()} (Win%: {win_prob:.2%})\n"

            if len(current_msg) + len(header) + len(market_line) >= MAX_DISCORD_LENGTH:
                messages.append(current_msg)
                current_msg = header_line

            if game not in printed_games:
                current_msg += header
                printed_games.add(game)

            current_msg += market_line

            for bet in bets:
                emoji = highlight_ev(bet["ev_pct"])
                american = decimal_to_american(bet["odds"])
                odds_str = f"{american:+}" if american else f"{bet['odds']:.2f}"
                stake_str = f" | Stake: ${bet['stake']:.2f}" if bet["stake"] >= 1 else ""
                link = bet.get("link")
                book_title = bet["book"].title()
                book_str = f"[{book_title}]({link})" if link else book_title
                if bet["date"] == format_ct_short_time(datetime.now(pytz.timezone("America/Chicago"))):
                    emoji = "🛰️ " + emoji
                bet_line = f"    {book_str:<40} | Odds: {odds_str:<6} | EV: +{bet['ev_pct']:.2f}%{stake_str} {emoji}\n"

                if len(current_msg) + len(bet_line) >= MAX_DISCORD_LENGTH:
                    messages.append(current_msg)
                    current_msg = header_line

                current_msg += bet_line

        if current_msg.strip() and current_msg not in messages:
            messages.append(current_msg)

        for msg in messages:
            send_discord_alert(msg.strip(), DISCORD_WEBHOOK_URL)

    print("\n📊 Session Summary:")
    print(f"Bankroll: ${session['bankroll']:.2f}")
    print(f"Total Risked: ${session['risked']:.2f}")
    print(f"Bets Logged: {len(session['bets'])}")

    print("Session file path:", os.path.abspath(SESSION_FILE))
    print("Session contents:", session)
    print("Prev bet keys:", prev_bet_keys)
    print("New bets:", new_bets)

    print("\n✅ EV% analysis complete.")

if __name__ == "__main__":
    print("🚀 Calculating EV% across all markets...")
    calculate_ev()
    print("\n✅ EV% analysis complete.")
