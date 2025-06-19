CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    game_date TIMESTAMP NOT NULL,
    home_team VARCHAR(50) NOT NULL,
    away_team VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE odds (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    sportsbook VARCHAR(50) NOT NULL,
    moneyline_home INTEGER,
    moneyline_away INTEGER,
    spread_home FLOAT,
    spread_away FLOAT,
    spread_odds_home INTEGER,
    spread_odds_away INTEGER,
    total FLOAT,
    over_odds INTEGER,
    under_odds INTEGER,
    ev_home FLOAT,
    ev_away FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
