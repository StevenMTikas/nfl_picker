"""
Team utility functions for NFL Picker system.
Centralized team name and abbreviation mappings.
"""

from typing import Dict, Optional, List

__all__ = [
    'TEAM_ABBREVIATION_TO_NAME',
    'TEAM_NAME_TO_ABBREVIATION',
    'get_team_abbreviation',
    'get_team_name',
    'get_all_team_abbreviations',
    'get_all_team_names',
    'is_valid_team_name',
    'is_valid_team_abbreviation',
]

# Team abbreviation to full name mapping
TEAM_ABBREVIATION_TO_NAME: Dict[str, str] = {
    'ARI': 'Arizona Cardinals',
    'ATL': 'Atlanta Falcons',
    'BAL': 'Baltimore Ravens',
    'BUF': 'Buffalo Bills',
    'CAR': 'Carolina Panthers',
    'CHI': 'Chicago Bears',
    'CIN': 'Cincinnati Bengals',
    'CLE': 'Cleveland Browns',
    'DAL': 'Dallas Cowboys',
    'DEN': 'Denver Broncos',
    'DET': 'Detroit Lions',
    'GB': 'Green Bay Packers',
    'HOU': 'Houston Texans',
    'IND': 'Indianapolis Colts',
    'JAX': 'Jacksonville Jaguars',
    'KC': 'Kansas City Chiefs',
    'LV': 'Las Vegas Raiders',
    'LAC': 'Los Angeles Chargers',
    'LAR': 'Los Angeles Rams',
    'MIA': 'Miami Dolphins',
    'MIN': 'Minnesota Vikings',
    'NE': 'New England Patriots',
    'NO': 'New Orleans Saints',
    'NYG': 'New York Giants',
    'NYJ': 'New York Jets',
    'PHI': 'Philadelphia Eagles',
    'PIT': 'Pittsburgh Steelers',
    'SF': 'San Francisco 49ers',
    'SEA': 'Seattle Seahawks',
    'TB': 'Tampa Bay Buccaneers',
    'TEN': 'Tennessee Titans',
    'WAS': 'Washington Commanders'
}

# Reverse mapping: full name to abbreviation
TEAM_NAME_TO_ABBREVIATION: Dict[str, str] = {v: k for k, v in TEAM_ABBREVIATION_TO_NAME.items()}


def get_team_abbreviation(team_name: str) -> Optional[str]:
    """
    Convert full team name to abbreviation.
    
    Args:
        team_name: Full team name (e.g., "Kansas City Chiefs")
        
    Returns:
        Team abbreviation (e.g., "KC") or None if not found
    """
    return TEAM_NAME_TO_ABBREVIATION.get(team_name)


def get_team_name(team_abbreviation: str) -> Optional[str]:
    """
    Convert team abbreviation to full name.
    
    Args:
        team_abbreviation: Team abbreviation (e.g., "KC")
        
    Returns:
        Full team name (e.g., "Kansas City Chiefs") or None if not found
    """
    return TEAM_ABBREVIATION_TO_NAME.get(team_abbreviation.upper())


def get_all_team_abbreviations() -> List[str]:
    """Get list of all team abbreviations."""
    return list(TEAM_ABBREVIATION_TO_NAME.keys())


def get_all_team_names() -> List[str]:
    """Get list of all team names."""
    return list(TEAM_ABBREVIATION_TO_NAME.values())


def is_valid_team_name(team_name: str) -> bool:
    """Check if a team name is valid."""
    return team_name in TEAM_NAME_TO_ABBREVIATION


def is_valid_team_abbreviation(team_abbreviation: str) -> bool:
    """Check if a team abbreviation is valid."""
    return team_abbreviation.upper() in TEAM_ABBREVIATION_TO_NAME

