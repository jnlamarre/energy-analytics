#!/usr/bin/env python3
"""
OOP-based Main Pipeline Runner

Unified entry point for all data pipelines using object-oriented architecture.
Runs both consumption and stations pipelines sequentially.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from pipelines.consumption_pipeline import ConsumptionPipeline
from pipelines.stations_pipeline import StationsPipeline


def main():
    """
    Run all data pipelines using OOP approach.
    """
    print("=== Energy Analytics Data Pipelines (OOP) ===")
    print("Running all pipelines sequentially...\n")
    
    try:
        # Run consumption pipeline
        print("1. Starting Consumption Pipeline...")
        consumption_pipeline = ConsumptionPipeline()
        consumption_pipeline.run_full_pipeline()
        print("SUCCESS: Consumption pipeline completed\n")
        
        # Run stations pipeline
        print("2. Starting Stations Pipeline...")
        stations_pipeline = StationsPipeline()
        stations_pipeline.run_full_pipeline()
        print("SUCCESS: Stations pipeline completed\n")
        
        print("=== All pipelines completed successfully! ===")
        
    except Exception as e:
        print(f"ERROR: Pipeline execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()