#!/usr/bin/env python3
"""
OOP-based Fuel Stations Data Pipeline

This script demonstrates the new object-oriented pipeline architecture.
Fetches fuel station data and loads it into DuckDB using pipeline classes.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from pipelines.stations_pipeline import StationsPipeline
from utils.logging_config import get_pipeline_logger


def main() -> None:
    """
    Run the stations data pipeline using OOP approach.
    """
    # Setup pipeline logger
    logger = get_pipeline_logger('stations')
    
    logger.info("=== Fuel Stations Data Pipeline (OOP) ===")
    
    # Create pipeline instance with logger
    pipeline = StationsPipeline(logger)
    
    # Run the complete pipeline
    # This will: fetch -> process -> store -> load to database
    pipeline.run_full_pipeline()
    
    logger.info("=== Pipeline completed successfully! ===")


if __name__ == "__main__":
    main()