import psycopg2
from config import DB_CONFIG
from utils.ev import no_vig_prob, expected_value
from datetime import date

def connect():
    return psycopg2.connect(**DB_CONFIG)

print("🚀 Starting EV% calculation...")

def calculate_ev():
    conn = connect()
    cur = conn.cursor()

    # Only consider games from today
    cur.execute("""
        SELECT
            g.id,
            g.game_date,
            g.home_team,
            g.away_team,
            dk.moneyline_home, dk.moneyline_away,
            dk.spread_home, dk.spread_away,
            dk.spread_odds_home, dk.spread_odds_away,
            dk.total, dk.over_odds, dk.under_odds,
            pin.moneyline_home, pin.moneyline_away,
            pin.spread_home, pin.spread_away,
            pin.spread_odds_home, pin.spread_odds_away,
            pin.total, pin.over_odds, pin.under_odds
        FROM games g
        JOIN (
            SELECT DISTINCT ON (game_id)
                *
            FROM odds
            WHERE sportsbook = 'DraftKings'
            ORDER BY game_id, created_at DESC
        ) dk ON dk.game_id = g.id
        JOIN (
            SELECT DISTINCT ON (game_id)
                *
            FROM odds
            WHERE sportsbook = 'Pinnacle'
            ORDER BY game_id, created_at DESC
        ) pin ON pin.game_id = g.id
        WHERE DATE(g.game_date) = CURRENT_DATE
    """)

    rows = cur.fetchall()
    print(f"🧪 Total rows fetched: {len(rows)}")

    if not rows:
        print("⚠️ No games found for today with odds from both books.")
        return

    for row in rows:
        (
            game_id, game_date, home, away,
            dk_ml_home, dk_ml_away,
            dk_spread_home, dk_spread_away,
            dk_spread_odds_home, dk_spread_odds_away,
            dk_total, dk_over_odds, dk_under_odds,
            pin_ml_home, pin_ml_away,
            pin_spread_home, pin_spread_away,
            pin_spread_odds_home, pin_spread_odds_away,
            pin_total, pin_over_odds, pin_under_odds
        ) = row

        print(f"\n📅 {away} @ {home} ({game_date.date()})")

        # --- MONEYLINE ---
        if None not in (dk_ml_home, dk_ml_away, pin_ml_home, pin_ml_away):
            prob_home_ml, prob_away_ml = no_vig_prob(pin_ml_home, pin_ml_away)
            ev_home_ml = expected_value(prob_home_ml, dk_ml_home)
            ev_away_ml = expected_value(prob_away_ml, dk_ml_away)

            print(f"  ➤ ML Home: {dk_ml_home}, EV%: {ev_home_ml * 100:.2f}%" if ev_home_ml else "  ⚠️ ML Home EV error")
            print(f"  ➤ ML Away: {dk_ml_away}, EV%: {ev_away_ml * 100:.2f}%" if ev_away_ml else "  ⚠️ ML Away EV error")

            if ev_home_ml and ev_home_ml > 0.03:
                print(f"🔥 +EV ML: {home} at {dk_ml_home} | EV%: {ev_home_ml * 100:.2f}%")
            if ev_away_ml and ev_away_ml > 0.03:
                print(f"🔥 +EV ML: {away} at {dk_ml_away} | EV%: {ev_away_ml * 100:.2f}%")

        # --- SPREAD ---
        if (
            None not in (dk_spread_odds_home, dk_spread_odds_away, pin_spread_odds_home, pin_spread_odds_away)
            and dk_spread_home == pin_spread_home
        ):
            prob_home_spread, prob_away_spread = no_vig_prob(pin_spread_odds_home, pin_spread_odds_away)
            ev_home_spread = expected_value(prob_home_spread, dk_spread_odds_home)
            ev_away_spread = expected_value(prob_away_spread, dk_spread_odds_away)

            print(f"  ➤ Spread Home ({dk_spread_home:+}): {dk_spread_odds_home}, EV%: {ev_home_spread * 100:.2f}%" if ev_home_spread else "  ⚠️ Spread Home EV error")
            print(f"  ➤ Spread Away ({dk_spread_away:+}): {dk_spread_odds_away}, EV%: {ev_away_spread * 100:.2f}%" if ev_away_spread else "  ⚠️ Spread Away EV error")

            if ev_home_spread and ev_home_spread > 0.03:
                print(f"🔥 +EV Spread: {home} {dk_spread_home:+} at {dk_spread_odds_home} | EV%: {ev_home_spread * 100:.2f}%")
            if ev_away_spread and ev_away_spread > 0.03:
                print(f"🔥 +EV Spread: {away} {dk_spread_away:+} at {dk_spread_odds_away} | EV%: {ev_away_spread * 100:.2f}%")

        # --- TOTAL ---
        if (
            None not in (dk_over_odds, dk_under_odds, pin_over_odds, pin_under_odds)
            and dk_total == pin_total
        ):
            prob_over, prob_under = no_vig_prob(pin_over_odds, pin_under_odds)
            ev_over = expected_value(prob_over, dk_over_odds)
            ev_under = expected_value(prob_under, dk_under_odds)

            print(f"  ➤ Over ({dk_total}): {dk_over_odds}, EV%: {ev_over * 100:.2f}%" if ev_over else "  ⚠️ Over EV error")
            print(f"  ➤ Under ({dk_total}): {dk_under_odds}, EV%: {ev_under * 100:.2f}%" if ev_under else "  ⚠️ Under EV error")

            if ev_over and ev_over > 0.03:
                print(f"🔥 +EV Total Over {dk_total} at {dk_over_odds} | EV%: {ev_over * 100:.2f}%")
            if ev_under and ev_under > 0.03:
                print(f"🔥 +EV Total Under {dk_total} at {dk_under_odds} | EV%: {ev_under * 100:.2f}%")

    conn.close()

if __name__ == "__main__":
    calculate_ev()
    print("✅ EV% calculation complete")
