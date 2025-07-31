# 🧠 Odds Data Pipeline

A real-time betting odds data pipeline built in Python that analyzes sharp vs recreational sportsbook lines across major sports and surfaces high-EV betting opportunities. Alerts are sent to Discord with context, Kelly staking suggestions, and bookmaker links.

---

## 🚀 Features

- **Supports 15+ Sports**: MLB, NBA, NFL, NCAAF, MMA, Tennis, NHL, Soccer (EPL, MLS, etc.)
- **Sharp vs Rec Comparison**: Compares Pinnacle, Circa, BetOnline odds vs books like DraftKings, FanDuel, BetMGM.
- **EV% Calculation**: Uses no-vig probabilities to calculate expected value (EV%) for spreads, totals, and moneylines.
- **Discord Alerts**: Sends intuitive, formatted betting alerts under 2,000 characters with emojis, Kelly stakes, and betslip links.
- **Market Filtering**:
  - Filters by EV% range (3%–14%)
  - Market width between 0%–50%
  - Odds between -250 and +120
  - Fresh lines (within 30 minutes)


 🛠️ Tech Stack
**Python (3.11+)**

**PostgreSQL (session tracking, odds storage)**

**psycopg2 for DB access**

**The Odds API (https://the-odds-api.com/)**

🧰 Usage
# Fetch odds for a specific sport (e.g. MLB)
```
python -m pipelines.fetch_odds_api --sport baseball_mlb
```
# Run EV analysis
```
python -m analysis.calculate_ev --bankroll 100
```
# API keys and webhook URLs
**🔐 API Key**
You'll need a free or paid key from The Odds API stored in your .env:

**ODDS_API_KEY=your_api_key**

**DISCORD_WEBHOOK_URL=your_webhook_url**


## DEMO

https://github.com/user-attachments/assets/ec7666e7-825b-4bd4-aca5-ff3e8e7aec95


