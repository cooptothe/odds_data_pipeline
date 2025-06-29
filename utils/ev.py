from math import isfinite

def decimal_to_american(decimal_odds):
    if not decimal_odds:
        return None
    try:
        decimal_odds = float(decimal_odds)
    except (ValueError, TypeError):
        return None

    if not isfinite(decimal_odds) or decimal_odds <= 1.0:
        return None
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100 + 0.5)
    else:
        return int(-100 / (decimal_odds - 1) + 0.5)


def decimal_to_implied_prob(decimal_odds):
    return round(1 / decimal_odds, 4) if decimal_odds and decimal_odds > 1 else None

def no_vig_prob(sharp_odds):
    """
    Accepts a list of decimal odds (e.g. [1.91, 2.05])
    Returns a list of no-vig win probabilities
    """
    implied = [decimal_to_implied_prob(o) for o in sharp_odds if o and o > 1]
    total = sum(implied)
    return [round(p / total, 4) for p in implied]

def expected_value(win_prob, decimal_odds):
    if not win_prob or not decimal_odds or decimal_odds <= 1:
        return None
    return round((decimal_odds * win_prob) - 1, 4)
