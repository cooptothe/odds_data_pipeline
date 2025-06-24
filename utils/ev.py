def american_to_implied(american_odds):
    if american_odds is None:
        return None
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return -american_odds / (-american_odds + 100)

def no_vig_prob(odds_home, odds_away):
    """Convert Pinnacle odds to true probabilities without juice."""
    p_home = american_to_implied(odds_home)
    p_away = american_to_implied(odds_away)
    total = p_home + p_away
    return p_home / total, p_away / total  # normalized

def expected_value(prob, offered_odds):
    """Calculate EV% from implied prob and DK odds."""
    if prob is None or offered_odds is None:
        return None
    implied = american_to_implied(offered_odds)
    return round((prob * (1 + abs(offered_odds) / 100 if offered_odds > 0 else 100 / abs(offered_odds))) - 1, 4)
