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

# Testing with coverage
pytest                        # Run 60 tests with coverage report
pytest -v                     # Verbose output 
pytest --cov-report=html      # Generate HTML coverage report
```

## Project Structure

```
scripts/           # Entry point scripts
src/              # Source code with OOP pipelines
├── pipelines/    # Pipeline implementations
├── utils/        # Base classes and utilities
└── analytics/    # Data analysis queries
tests/            # Production-ready test suite (60 tests)
├── conftest.py   # Advanced fixture patterns
├── test_*.py     # 6 focused test modules
└── fixtures/     # Test data and configurations
config.json       # API configuration
sql/             # Database schemas
data/            # Generated data and database
```

## Features

- **Modern Python**: Type hints, Pydantic dataclasses, OOP architecture
- **Testing**: 60 production-ready tests with clean organization and 25% coverage
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

## Development

**Testing:**
- Production-ready test suite with clean, flat organization
- Enhanced patterns: Content validation, Unicode handling, parametrized testing
- Session-scoped fixtures for performance optimization
- Code coverage reporting with HTML output (25% baseline)
- Comprehensive testing: API, configuration, database, files, integration, pipelines

**Dependencies:**
```bash
uv install                   # Production dependencies
uv sync --group test         # Add testing dependencies
```

## Requirements

- Python 3.13+
- Dependencies: DuckDB, Requests, pytest-cov (managed via `uv`)
- Package management: `uv` (UV package manager)