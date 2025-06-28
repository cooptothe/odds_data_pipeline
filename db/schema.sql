-- SPORTS
CREATE TABLE sports (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,  -- "baseball_mlb", "basketball_nba", etc.
    title VARCHAR(100) NOT NULL       -- "MLB", "NBA", etc.
);

-- GAMES
CREATE TABLE games (
    id UUID PRIMARY KEY,
    sport_id INT REFERENCES sports(id),
    game_date TIMESTAMP NOT NULL,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    status VARCHAR(50),                -- upcoming, live, completed
    created_at TIMESTAMP DEFAULT NOW()
);

-- ODDS
CREATE TABLE odds (
    id SERIAL PRIMARY KEY,
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    sportsbook VARCHAR(50) NOT NULL,        -- "draftkings", "pinnacle", etc.
    market VARCHAR(20) NOT NULL,            -- "moneyline", "spreads", "totals"
    side VARCHAR(20),                       -- "home", "away", "over", "under"
    price DECIMAL,                          -- American odds (optional)
    decimal_price DECIMAL,                  -- Original decimal odds
    implied_prob DECIMAL,                   -- 1 / decimal_price
    point DECIMAL,                          -- spread or total line
    created_at TIMESTAMP DEFAULT NOW()
);


