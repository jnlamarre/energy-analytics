#!/usr/bin/env python3
"""
OOP-based Energy Consumption Data Pipeline

This script demonstrates the new object-oriented pipeline architecture.
Fetches energy consumption data and loads it into DuckDB using pipeline classes.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from pipelines.consumption_pipeline import ConsumptionPipeline


def main():
    """
    Run the consumption data pipeline using OOP approach.
    """
    print("=== Energy Consumption Data Pipeline (OOP) ===")
    
    # Create pipeline instance
    pipeline = ConsumptionPipeline()
    
    # Run the complete pipeline
    # This will: fetch -> process -> store -> load to database
    pipeline.run_full_pipeline()
    
    print("=== Pipeline completed successfully! ===")


if __name__ == "__main__":
    main()