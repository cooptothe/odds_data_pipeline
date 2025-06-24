TEAM_NAME_MAP = {
    # AL East
    "BAL Orioles": "Baltimore Orioles",
    "Baltimore Orioles": "Baltimore Orioles",
    "BOS Red Sox": "Boston Red Sox",
    "Boston Red Sox": "Boston Red Sox",
    "NY Yankees": "New York Yankees",
    "New York Yankees": "New York Yankees",
    "TB Rays": "Tampa Bay Rays",
    "Tampa Bay Rays": "Tampa Bay Rays",
    "TOR Blue Jays": "Toronto Blue Jays",
    "Toronto Blue Jays": "Toronto Blue Jays",

    # AL Central
    "CHI White Sox": "Chicago White Sox",
    "Chicago White Sox": "Chicago White Sox",
    "CLE Guardians": "Cleveland Guardians",
    "Cleveland Guardians": "Cleveland Guardians",
    "DET Tigers": "Detroit Tigers",
    "Detroit Tigers": "Detroit Tigers",
    "KC Royals": "Kansas City Royals",
    "Kansas City Royals": "Kansas City Royals",
    "MIN Twins": "Minnesota Twins",
    "Minnesota Twins": "Minnesota Twins",

    # AL West
    "HOU Astros": "Houston Astros",
    "Houston Astros": "Houston Astros",
    "LA Angels": "Los Angeles Angels",
    "Los Angeles Angels": "Los Angeles Angels",
    "OAK Athletics": "Oakland Athletics",
    "Oakland Athletics": "Oakland Athletics",
    "SEA Mariners": "Seattle Mariners",
    "Seattle Mariners": "Seattle Mariners",
    "TEX Rangers": "Texas Rangers",
    "Texas Rangers": "Texas Rangers",

    # NL East
    "ATL Braves": "Atlanta Braves",
    "Atlanta Braves": "Atlanta Braves",
    "MIA Marlins": "Miami Marlins",
    "Miami Marlins": "Miami Marlins",
    "NY Mets": "New York Mets",
    "New York Mets": "New York Mets",
    "PHI Phillies": "Philadelphia Phillies",
    "Philadelphia Phillies": "Philadelphia Phillies",
    "WAS Nationals": "Washington Nationals",
    "Washington Nationals": "Washington Nationals",

    # NL Central
    "CHC Cubs": "Chicago Cubs",
    "CHI Cubs": "Chicago Cubs",
    "Chicago Cubs": "Chicago Cubs",
    "CIN Reds": "Cincinnati Reds",
    "Cincinnati Reds": "Cincinnati Reds",
    "MIL Brewers": "Milwaukee Brewers",
    "Milwaukee Brewers": "Milwaukee Brewers",
    "PIT Pirates": "Pittsburgh Pirates",
    "Pittsburgh Pirates": "Pittsburgh Pirates",
    "STL Cardinals": "St. Louis Cardinals",
    "St. Louis Cardinals": "St. Louis Cardinals",

    # NL West
    "ARI Diamondbacks": "Arizona Diamondbacks",
    "Arizona Diamondbacks": "Arizona Diamondbacks",
    "COL Rockies": "Colorado Rockies",
    "Colorado Rockies": "Colorado Rockies",
    "LA Dodgers": "Los Angeles Dodgers",
    "Los Angeles Dodgers": "Los Angeles Dodgers",
    "SD Padres": "San Diego Padres",
    "San Diego Padres": "San Diego Padres",
    "SF Giants": "San Francisco Giants",
    "San Francisco Giants": "San Francisco Giants",
}

def normalize_team(name: str) -> str:
    return TEAM_NAME_MAP.get(name.strip(), name.strip())


def normalize_team(name):
    return TEAM_NAME_MAP.get(name, name)  # fallback to original if not mapped
