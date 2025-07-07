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

## DEMO

https://github.com/user-attachments/assets/ec7666e7-825b-4bd4-aca5-ff3e8e7aec95


