# Energy Analytics Project

## Overview
French energy data analytics with two main pipelines:
- **Energy Consumption**: 3,024 hourly electricity/gas records (Jan-Mar 2026)  
- **Fuel Stations**: 9,772 stations with real-time prices across France

## Project Structure
```
energy-analytics/
├── README.md                   # User documentation
├── CLAUDE.md                   # This file - Project context
├── pyproject.toml              # UV package management (Python 3.13+)
├── config.json                 # API endpoints and table configuration
├── uv.lock                     # UV lock file
├── scripts/                    # Entry point scripts
│   ├── run_analytics.py        # Database analytics runner
│   ├── run_consumption.py      # Individual consumption pipeline
│   └── run_stations.py         # Individual stations pipeline
├── sql/                        # Database schema definitions
│   ├── consumption.sql         # Consumption table schema
│   └── stations.sql            # Stations table schema
├── src/                        # Main source code
│   ├── main.py                 # Unified entry point for all pipelines
│   ├── analytics/              # Data analysis and reporting
│   │   ├── consumption.py      # Energy consumption statistics
│   │   └── stations.py         # Fuel price and geographic analysis
│   ├── pipelines/              # Pipeline implementations
│   │   ├── consumption.py      # Complete consumption pipeline class
│   │   └── stations.py         # Complete stations pipeline class
│   └── utils/                  # Core utilities and base classes
│       ├── api.py              # HTTP request handling with pagination
│       ├── configuration_classes.py # Pydantic config classes & manager
│       ├── database.py         # DuckDB connection and query operations
│       ├── files.py            # JSON save/load operations
│       ├── logging.py          # Advanced logging system
│       └── pipelines.py        # Base pipeline, processor, and storage classes
├── tests/                      # Production-ready test suite
│   ├── conftest.py             # Central fixture definitions (session-scoped)
│   ├── test_api.py            # API operations testing
│   ├── test_configuration.py  # Configuration objects & manager testing
│   ├── test_database.py       # Database operations testing
│   ├── test_files.py          # File operations testing (with enhanced patterns)
│   ├── test_integration.py    # Cross-component integration testing
│   ├── test_pipelines.py      # Pipeline workflows testing
│   └── fixtures/              # Test data and configurations
│       ├── config/            # JSON configuration test files
│       └── sql/               # Test SQL fixtures
├── pytest.ini                 # Pytest configuration with coverage settings
├── .coveragerc                # Coverage reporting configuration
├── htmlcov/                   # HTML coverage reports (ignored by git)
├── data/                      # Ignored by git (large data files)
│   ├── consumption.json       # Energy consumption data
│   ├── stations.json         # Fuel station data
│   └── energy-analytics.db   # DuckDB database
└── logs/                      # Ignored by git (log files)
    ├── main.log               # Centralized logging for full suite
    ├── consumption.log        # Individual consumption pipeline logs
    └── stations.log           # Individual stations pipeline logs
```

## Database Schema
- **`consumption` table**: 3,024 hourly energy records (electricity/gas consumption in MW, Jan 1 - Mar 31, 2026)
- **`stations` table**: 9,772 fuel stations with current prices and locations

## Key Commands
```bash
# Run all pipelines
cd src && python main.py

# Run individual pipelines  
python scripts/run_consumption.py
python scripts/run_stations.py

# Analytics
python scripts/run_analytics.py

# Dependencies
uv install

# Testing
pytest                          # Run all tests with coverage
pytest -v                       # Verbose output with test names
pytest --cov-report=html        # Generate HTML coverage report
pytest tests/test_api.py        # Run specific test module
pytest tests/test_files.py      # Run enhanced file operation tests

# Test Dependencies
uv sync --group test            # Install test dependencies
```

## Development Notes
**Windows Console Encoding Issue:** When running Python scripts via Bash tool, avoid Unicode characters (emojis, special symbols) in print statements as Windows console uses cp1252 encoding which causes `UnicodeEncodeError`. Use plain ASCII text instead.

## APIs Used
1. **Energy Consumption**: `https://tabular-api.data.gouv.fr/api/resources/cfc27ff9-1871-4ee8-be64-b9a290c06935/data/`
2. **Fuel Prices**: `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records`

## Current Status ✅ PRODUCTION-READY
- Full OOP architecture with modern Python 3.10+ type hints
- Advanced logging system with structured output
- DuckDB database with context managers and bulk imports
- Clean file organization following Python best practices
- Complete pipelines working with UTF-8 encoding support
- **Professional test suite** with 60 tests and 25% coverage

## Architecture Features
- **Pydantic dataclasses** with configuration management
- **Base classes** for pipelines, processors, and storage
- **Context managers** for automatic database resource cleanup
- **Factory patterns** for polymorphic object creation
- **English naming** throughout codebase
- **Advanced testing methodology** with fixtures and coverage

## Testing Infrastructure
- **60 production-ready tests** with clean, flat organization structure
- **Professional test suite** covering all core functionality
- **Advanced patterns integrated**: Content validation, Unicode handling, parametrized testing
- **Session-scoped fixtures** for performance optimization  
- **Code coverage analysis** with HTML reports (25% baseline)
- **Clean test organization**: 6 focused test files (api, configuration, database, files, integration, pipelines)

## Coverage Analysis
**Well-tested modules (high coverage):**
- `utils/files.py`: 100% coverage (enhanced with content validation)
- `utils/database.py`: 87% coverage (enhanced with integration patterns)
- `utils/configuration_classes.py`: 81% coverage (consolidated testing)
- `utils/api.py`: 88% coverage (comprehensive API testing)

**Coverage opportunities:**
- Pipeline implementations: 0% (business logic testing needed)
- Analytics modules: 0% (reporting functions testing needed)
- Logging system: 0% (utility functions testing needed)

## Next Steps
1. Configure linting/type checking (ruff, mypy, etc.)
2. Expand test coverage for pipeline and analytics modules (currently 0%)
3. Add performance testing and monitoring
4. CI/CD pipeline setup with automated test execution