# Energy Analytics

French energy data analytics with two data pipelines: electricity/gas consumption and fuel station prices.

## Quick Start

```bash
# Install dependencies
uv install

# Run all pipelines
cd src && python main.py

# Individual pipelines
python scripts/run_consumption.py
python scripts/run_stations.py
python scripts/run_analytics.py
```

## Project Structure

```
scripts/           # Entry point scripts
src/              # Source code with OOP pipelines
├── pipelines/    # Pipeline implementations
├── utils/        # Base classes and utilities
└── analytics/    # Data analysis queries
config.json       # API configuration
sql/             # Database schemas
data/            # Generated data and database
```

## Features

- **Modern Python**: Type hints, Pydantic dataclasses, OOP architecture
- **Logging System**: Structured logging with component isolation
- **Database**: DuckDB with context managers and bulk imports
- **Configuration**: JSON-based config with automatic validation
- **Performance**: Efficient pagination and date range handling

## Data

**Sources:**
- Energy consumption: Data.gouv.fr tabular API (3,024 hourly records)
- Fuel prices: Economie.gouv.fr API (9,772 stations)

**Database:**
- DuckDB: `data/energy-analytics.db`
- Tables: `consumption`, `stations`
- Analytics: Regional analysis, price comparisons, consumption statistics

## Requirements

- Python 3.13+
- Dependencies: DuckDB, Requests (managed via `uv`)
- Package management: `uv` (UV package manager)