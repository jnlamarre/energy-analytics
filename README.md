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
pytest                        # Run 125 tests with 100% coverage
pytest -v                     # Verbose output with test names
pytest --cov-report=html      # Generate HTML coverage report
```

## Project Structure

```
scripts/           # Entry point scripts
src/              # Source code with OOP pipelines
├── pipelines/    # Pipeline implementations
├── utils/        # Base classes and utilities
└── analytics/    # Data analysis queries
tests/            # Production-ready test suite (125 tests, 100% coverage)
├── unit/         # Unit tests (7 modules)
├── integration/  # Cross-component tests
├── e2e/          # End-to-end workflow tests
├── conftest.py   # Session-scoped fixtures
└── fixtures/     # Test data and configurations
config.json       # API configuration
sql/             # Database schemas
data/            # Generated data and database
```

## Features

- **Modern Python**: Type hints, Pydantic dataclasses, OOP architecture
- **Testing**: 125 comprehensive tests with perfect 100% coverage
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
- **Perfect 100% coverage** across all 7 core modules (335 lines tested)
- **125 comprehensive tests** with unit/integration/e2e organization
- **Advanced patterns**: Mocking, content validation, Unicode handling, parametrized testing
- **Session-scoped fixtures** for performance optimization
- **Professional test architecture**: Coherent pragma usage, appropriate exclusions
- **Complete coverage**: All utils, pipelines, and business logic thoroughly tested

**Dependencies:**
```bash
uv install                   # Production dependencies
uv sync --group test         # Add testing dependencies
```

## Requirements

- Python 3.13+
- Dependencies: DuckDB, Requests, pytest-cov (managed via `uv`)
- Package management: `uv` (UV package manager)