import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from analytics.stations import show_tables_overview, show_stations_stats
from analytics.consumption import show_consumption_stats


def main() -> None:
    """Run comprehensive database analytics"""
    show_tables_overview()
    show_consumption_stats()
    show_stations_stats()


if __name__ == "__main__":
    main()