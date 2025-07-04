# Betting Edge Tool
 This tool scrapes MLB pregame odds from DraftKings and Pinnacle sportsbooks, processes the data to calculate Expected Value percentages (EV%) for each betting market, and identifies value bets based on Pinnacle’s no-vig implied probabilities. By comparing Pinnacle’s market maker odds with DraftKings' lines, it highlights profitable betting opportunities.

# How it works
Ingestion: Fetches real-time odds data from multiple sportsbooks.

Normalization: Converts odds formats (American/decimal) and removes vig to calculate true implied probabilities.

EV% Calculation: Compares the user’s sportsbook odds against market maker odds to compute Expected Value percentages, signaling bets with positive expected value.

Discord Alerts: Created webhook that sends alrts to discord channel.

This pipeline empowers bettors with data-driven insights to find edges in the market.


https://github.com/user-attachments/assets/150b46fa-da54-4c95-a55e-622044c042bb

