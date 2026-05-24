import sys
sys.path.append('..')

from src.analytics.stations_queries import show_tables_overview, show_stations_stats
from src.analytics.consumption_queries import show_consumption_stats


def main() -> None:
    """Run comprehensive database analytics"""
    show_tables_overview()
    show_consumption_stats()
    show_stations_stats()


if __name__ == "__main__":
    main()