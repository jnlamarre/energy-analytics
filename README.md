# Energy Analytics

French energy data analytics project with modern Pydantic dataclass pipelines for real-time consumption and fuel price data.

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
│   ├── configuration_classes.py  # Pydantic dataclasses, ConfigurationManager
│   ├── pipeline_classes.py       # BasePipeline, BaseProcessor, BaseStorage
│   ├── config.py                 # Modern OOP interface
│   ├── config.json               # English field names configuration
│   └── *.py                      # Other utilities (API, database, file handling)
├── analytics/                     # Data analysis queries
└── sql/                          # Database schemas
```

## Modern OOP Features

- **Pydantic Dataclasses**: Automatic validation and @property decorators
- **English Naming**: Consistent English field names (api_type, target_file, table_name)
- **Inheritance**: `BaseConfiguration` → `DataGouvConfiguration`/`EconomieGouvConfiguration`
- **@property Decorators**: Dynamic URL building and computed attributes
- **ConfigurationManager**: Factory methods with **kwargs unpacking
- **Polymorphism**: Same pipeline interface for different data sources
- **Clean Architecture**: Legacy functions removed, modern OOP interface only

## Data Sources

- **Energy Consumption**: French electricity/gas hourly consumption via Data.gouv.fr tabular API
- **Fuel Prices**: Real-time prices from 9,772 fuel stations via Economie.gouv.fr API

## Database

DuckDB database (`data/energy-analytics.db`) with two main tables:
- `consumption` - Hourly energy consumption data (electricity, gas in MW) 
- `stations` - Fuel stations with GPS coordinates, prices, and metadata

Data files stored in `data/` directory (git-ignored).

## Features

- **Modular Architecture**: Clean separation with entity-based pipelines
- **Configuration-driven**: English-named JSON config with external SQL schemas and Pydantic validation
- **Efficient Date Range Fetching**: Single API call for 3-month consumption data using proper range operators
- **Pagination Handling**: Automatic pagination for large datasets
- **Comprehensive Analytics**: Statistics, regional analysis, price comparisons
- **Error Resilience**: Graceful handling of API errors and duplicates

## Requirements

- Python 3.13+
- Dependencies: DuckDB, Requests (managed via `uv`)
- Package management: `uv` (UV package manager)