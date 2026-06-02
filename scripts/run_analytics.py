import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from analytics.consumption import show_consumption_stats
from analytics.stations import show_stations_stats, show_tables_overview


def main() -> None:
    """Run comprehensive database analytics"""
    show_tables_overview()
    show_consumption_stats()
    show_stations_stats()


if __name__ == "__main__":
    main()
