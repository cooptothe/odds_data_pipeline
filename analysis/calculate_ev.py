import psycopg2
from config import DB_CONFIG
from utils.ev import no_vig_prob, expected_value

def connect():
    return psycopg2.connect(**DB_CONFIG)

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
        JOIN odds dk ON dk.game_id = g.id AND dk.sportsbook = 'DraftKings'
        JOIN odds pin ON pin.game_id = g.id AND pin.sportsbook = 'Pinnacle'
        WHERE dk.moneyline_home IS NOT NULL AND pin.moneyline_home IS NOT NULL
    """)

    rows = cur.fetchall()

    for row in rows:
        game_id, date, home, away, dk_home, dk_away, pin_home, pin_away = row

        # Step 2: Get true probabilities from Pinnacle odds
        prob_home, prob_away = no_vig_prob(pin_home, pin_away)

        # Step 3: Calculate EV% for both DK sides
        ev_home = expected_value(prob_home, dk_home)
        ev_away = expected_value(prob_away, dk_away)

        print(f"\n{away} @ {home} ({date.date()})")
        print(f"  ➤ DraftKings Home: {dk_home}, EV%: {ev_home * 100:.2f}%")
        print(f"  ➤ DraftKings Away: {dk_away}, EV%: {ev_away * 100:.2f}%")

    conn.close()
