# Energy Analytics

French energy data analytics project with object-oriented pipelines for real-time consumption and fuel price data.

## Quick Start

```bash
# Install dependencies
uv install

# Run all OOP pipelines (from src directory)
cd src
python main.py

# Or run individual OOP pipelines
cd src
python run_consumption_pipeline.py  # ConsumptionPipeline class
python run_stations_pipeline.py     # StationsPipeline class
python run_analytics.py             # Query and analyze data
```

## Project Structure

Object-oriented architecture with inheritance and polymorphism:

```
src/
├── main.py                         # Unified OOP entry point
├── run_*.py                       # Individual OOP pipeline runners
├── pipelines/                     # OOP pipeline implementations
│   ├── consumption_pipeline.py   # ConsumptionPipeline class
│   └── stations_pipeline.py      # StationsPipeline class
├── utils/                         # Base classes and utilities
│   ├── configuration_classes.py  # BaseConfiguration, ConfigurationManager
│   ├── pipeline_classes.py       # BasePipeline, BaseProcessor, BaseStorage
│   ├── config.py                 # Legacy compatibility functions
│   └── *.py                      # Other utilities (API, database, file handling)
├── analytics/                     # Data analysis queries
└── sql/                          # Database schemas
```

## OOP Features

- **Inheritance**: `BaseConfiguration` → `DataGouvConfiguration`/`EconomieGouvConfiguration`
- **Polymorphism**: Same pipeline interface for different data sources
- **Factory Pattern**: `BaseConfiguration.create_from_dict()` for object creation
- **Manager Pattern**: `ConfigurationManager` for centralized config operations
- **Abstract Classes**: Clear interfaces for extensibility

## Data Sources

- **Energy Consumption**: French electricity/gas hourly consumption via Data.gouv.fr tabular API
- **Fuel Prices**: Real-time prices from 9,700+ fuel stations via Economie.gouv.fr API

## Database

DuckDB database (`data/energy-analytics.db`) with two main tables:
- `consumption` - Hourly energy consumption data (electricity, gas in MW) 
- `stations` - Fuel stations with GPS coordinates, prices, and metadata

Data files stored in `data/` directory (git-ignored).

## Features

- **Modular Architecture**: Clean separation with entity-based pipelines
- **Configuration-driven**: JSON config with external SQL schemas
- **Efficient Date Range Fetching**: Single API call for 3-month consumption data using proper range operators
- **Pagination Handling**: Automatic pagination for large datasets
- **Comprehensive Analytics**: Statistics, regional analysis, price comparisons
- **Error Resilience**: Graceful handling of API errors and duplicates

## Requirements

- Python 3.13+
- Dependencies: DuckDB, Requests (managed via `uv`)
- Package management: `uv` (UV package manager)