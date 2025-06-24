TEAM_NAME_MAP = {
    "BAL Orioles": "Baltimore Orioles",
    "NY Yankees": "New York Yankees",
    "NY Mets": "New York Mets",
    "CHC Cubs": "Chicago Cubs",
    "CWS White Sox": "Chicago White Sox",
    "TB Rays": "Tampa Bay Rays",
    "KC Royals": "Kansas City Royals",
    "SF Giants": "San Francisco Giants",
    "SD Padres": "San Diego Padres",
    # Add more as needed
}

def normalize_team(name):
    return TEAM_NAME_MAP.get(name, name)  # fallback to original if not mapped
