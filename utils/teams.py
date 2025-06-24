TEAM_NAME_MAP = {
    # AL East
    "BAL Orioles": "Baltimore Orioles",
    "BOS Red Sox": "Boston Red Sox",
    "NY Yankees": "New York Yankees",
    "TB Rays": "Tampa Bay Rays",
    "TOR Blue Jays": "Toronto Blue Jays",

    # AL Central
    "CHI White Sox": "Chicago White Sox",
    "CLE Guardians": "Cleveland Guardians",
    "DET Tigers": "Detroit Tigers",
    "KC Royals": "Kansas City Royals",
    "MIN Twins": "Minnesota Twins",

    # AL West
    "HOU Astros": "Houston Astros",
    "LA Angels": "Los Angeles Angels",
    "OAK Athletics": "Oakland Athletics",
    "SEA Mariners": "Seattle Mariners",
    "TEX Rangers": "Texas Rangers",

    # NL East
    "ATL Braves": "Atlanta Braves",
    "MIA Marlins": "Miami Marlins",
    "NY Mets": "New York Mets",
    "PHI Phillies": "Philadelphia Phillies",
    "WAS Nationals": "Washington Nationals",

    # NL Central
    "CHC Cubs": "Chicago Cubs",
    "CHI Cubs": "Chicago Cubs",
    "CIN Reds": "Cincinnati Reds",
    "MIL Brewers": "Milwaukee Brewers",
    "PIT Pirates": "Pittsburgh Pirates",
    "STL Cardinals": "St. Louis Cardinals",

    # NL West
    "ARI Diamondbacks": "Arizona Diamondbacks",
    "COL Rockies": "Colorado Rockies",
    "LA Dodgers": "Los Angeles Dodgers",
    "SD Padres": "San Diego Padres",
    "SF Giants": "San Francisco Giants",
}

def normalize_team(name: str) -> str:
    return TEAM_NAME_MAP.get(name.strip(), name.strip())