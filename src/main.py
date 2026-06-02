#!/usr/bin/env python3
"""
OOP-based Main Pipeline Runner

Unified entry point for all data pipelines using object-oriented architecture.
Runs both consumption and stations pipelines sequentially.
"""

import os
import sys

# Add src directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from pipelines.consumption import ConsumptionPipeline
from pipelines.stations import StationsPipeline
from utils.logging import get_main_logger


def main() -> None:
    """
    Run all data pipelines using OOP approach.
    """
    # Setup main logger
    logger = get_main_logger()

    logger.info("=== Energy Analytics Data Pipelines (OOP) ===")
    logger.info("Running all pipelines sequentially...")

    try:
        # Run consumption pipeline
        logger.info("1. Starting Consumption Pipeline...")
        consumption_pipeline = ConsumptionPipeline(logger)
        consumption_pipeline.run_full_pipeline()
        logger.info("SUCCESS: Consumption pipeline completed")

        # Run stations pipeline
        logger.info("2. Starting Stations Pipeline...")
        stations_pipeline = StationsPipeline(logger)
        stations_pipeline.run_full_pipeline()
        logger.info("SUCCESS: Stations pipeline completed")

        logger.info("=== All pipelines completed successfully! ===")

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
