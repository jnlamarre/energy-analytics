#!/usr/bin/env python3
"""
OOP-based Energy Consumption Data Pipeline

This script demonstrates the new object-oriented pipeline architecture.
Fetches energy consumption data and loads it into DuckDB using pipeline classes.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from pipelines.consumption import ConsumptionPipeline
from utils.logging import get_pipeline_logger


def main() -> None:
    """
    Run the consumption data pipeline using OOP approach.
    """
    # Setup pipeline logger
    logger = get_pipeline_logger('consumption')
    
    logger.info("=== Energy Consumption Data Pipeline (OOP) ===")
    
    # Create pipeline instance with logger
    pipeline = ConsumptionPipeline(logger)
    
    # Run the complete pipeline
    # This will: fetch -> process -> store -> load to database
    pipeline.run_full_pipeline()
    
    logger.info("=== Pipeline completed successfully! ===")


if __name__ == "__main__":
    main()