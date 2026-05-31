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
├── tests/                      # Production-ready test suite (100% coverage)
│   ├── conftest.py             # Central fixture definitions (session-scoped)
│   ├── unit/                   # Unit tests for individual components
│   │   ├── test_api.py        # API operations testing
│   │   ├── test_configuration.py # Configuration objects & manager testing
│   │   ├── test_database.py   # Database operations testing
│   │   ├── test_files.py      # File operations testing
│   │   ├── test_pipelines.py  # Base pipeline classes testing
│   │   ├── test_consumption_pipeline.py # Consumption pipeline testing
│   │   └── test_stations_pipeline.py # Stations pipeline testing
│   ├── integration/            # Cross-component integration testing
│   │   └── test_integration.py
│   ├── e2e/                   # End-to-end workflow testing
│   │   └── test_workflows.py
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
- Full OOP architecture with modern Python 3.13+ type hints
- Advanced logging system with structured output
- DuckDB database with context managers and bulk imports
- Clean file organization following Python best practices
- Complete pipelines working with UTF-8 encoding support
- **100% test coverage** with 125 comprehensive tests across all modules

## Architecture Features
- **Pydantic dataclasses** with configuration management
- **Base classes** for pipelines, processors, and storage
- **Context managers** for automatic database resource cleanup
- **Factory patterns** for polymorphic object creation
- **English naming** throughout codebase
- **Advanced testing methodology** with fixtures and coverage

## Testing Infrastructure ✅ 100% COVERAGE
- **125 production-ready tests** with clean hierarchical organization
- **Professional test suite** covering all core functionality
- **Advanced patterns integrated**: Mocking, content validation, Unicode handling, parametrized testing
- **Session-scoped fixtures** for performance optimization
- **Perfect test coverage** (100%) with HTML reports and coherent pragma usage
- **Clean test organization**: Unit/Integration/E2E structure with 9 focused test modules
- **Comprehensive testing**: All utils, pipelines, and core business logic covered

## Coverage Analysis ✅ PERFECT 100%
**All testable modules at 100% coverage:**
- `utils/api.py`: 100% (42 lines) - HTTP requests, pagination, error handling
- `utils/configuration_classes.py`: 100% (77 lines) - Config management, path resolution
- `utils/database.py`: 100% (23 lines) - DuckDB operations, context managers
- `utils/files.py`: 100% (8 lines) - JSON operations with Unicode support
- `utils/pipelines.py`: 100% (71 lines) - Base classes, abstract methods
- `pipelines/consumption.py`: 100% (56 lines) - Energy consumption pipeline
- `pipelines/stations.py`: 100% (58 lines) - Fuel stations pipeline

**Appropriately excluded from coverage:**
- `src/main.py` - Entry point script
- `src/utils/logging.py` - Logging infrastructure
- `src/analytics/*` - Reporting functions (no business logic)
- `scripts/*` - Individual pipeline runners

**Total: 335 lines tested, 0 lines missing**

## Next Steps
1. Configure linting/type checking (ruff, mypy, etc.)
2. Add performance testing and monitoring
3. CI/CD pipeline setup with automated test execution
4. Consider integration testing with real APIs (currently mocked)