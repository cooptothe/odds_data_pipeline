import psycopg2
from config import DB_CONFIG
from utils.ev import no_vig_prob, expected_value

def connect():
    return psycopg2.connect(**DB_CONFIG)
print("🚀 Starting EV% calculation...")


def calculate_ev():
    conn = connect()
    cur = conn.cursor()

    # Step 1: Join Pinnacle + DraftKings odds by game
    cur.execute("""
        SELECT
            g.id,
            g.game_date,
            g.home_team,
            g.away_team,
            dk.moneyline_home AS dk_ml_home,
            dk.moneyline_away AS dk_ml_away,
            pin.moneyline_home AS pin_ml_home,
            pin.moneyline_away AS pin_ml_away
        FROM games g
        JOIN (
    SELECT DISTINCT ON (game_id)
                game_id, moneyline_home, moneyline_away
            FROM odds
            WHERE sportsbook = 'DraftKings'
            ORDER BY game_id, created_at DESC
        ) dk ON dk.game_id = g.id
        JOIN (
            SELECT DISTINCT ON (game_id)
                game_id, moneyline_home, moneyline_away
            FROM odds
            WHERE sportsbook = 'Pinnacle'
            ORDER BY game_id, created_at DESC
        ) pin ON pin.game_id = g.id
        WHERE dk.moneyline_home IS NOT NULL
        AND pin.moneyline_home IS NOT NULL;
    """)

    rows = cur.fetchall()
    
    print(f"🧪 Total rows fetched: {len(rows)}")


    if not rows:
        print("⚠️ No matching games found with both DK and Pinnacle odds.")
        return

    print(f"✅ Found {len(rows)} games with odds from both books")

    for row in rows:
        game_id, date, home, away, dk_home, dk_away, pin_home, pin_away = row

        if None in (dk_home, dk_away, pin_home, pin_away):
            print(f"⚠️ Skipping game with missing odds: {away} @ {home}")
            continue

        from utils.ev import no_vig_prob, expected_value

        # Step 2: Get true probabilities from Pinnacle odds
        prob_home, prob_away = no_vig_prob(pin_home, pin_away)

        # Step 3: Calculate EV% for both DK sides
        ev_home = expected_value(prob_home, dk_home)
        ev_away = expected_value(prob_away, dk_away)

        print(f"\n{away} @ {home} ({date.date()})")
        print(f"  ➤ DraftKings Home: {dk_home}, EV%: {ev_home * 100:.2f}%" if ev_home is not None else "  ⚠️ EV% home calc error")
        print(f"  ➤ DraftKings Away: {dk_away}, EV%: {ev_away * 100:.2f}%" if ev_away is not None else "  ⚠️ EV% away calc error")

    conn.close()

if __name__ == "__main__":
    calculate_ev()
    print("✅ EV% calculation complete")
