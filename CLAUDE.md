# Energy Analytics Project - Claude Context

## Project Overview
French energy data analytics project with two main data pipelines:
1. **Energy Consumption Data**: Hourly electricity/gas consumption from French grid
2. **Fuel Station Prices**: Real-time fuel prices from 9,700+ stations across France

## Current Project Structure (COMMITTED - Clean State)
```
energy-analytics/
├── src/                        # Modular structure with entity-based design
│   ├── __init__.py
│   ├── utils/                  # Common functionality across pipelines
│   │   ├── __init__.py
│   │   ├── api_client.py       # HTTP request handling with pagination support
│   │   ├── database.py         # DuckDB connection and query operations
│   │   ├── file_handler.py     # JSON save/load operations
│   │   ├── config.py           # Configuration system with SQL schema loading
│   │   └── config.json         # API endpoints and table configuration
│   ├── consumption/            # Energy consumption pipeline
│   │   ├── __init__.py
│   │   ├── fetcher.py          # API fetching with multi-date support
│   │   ├── processor.py        # Data processing and JSON saving
│   │   └── storage.py          # Database table creation and loading
│   ├── stations/               # Fuel stations pipeline  
│   │   ├── __init__.py
│   │   ├── fetcher.py          # Paginated API fetching
│   │   ├── processor.py        # Coordinate conversion and data processing
│   │   └── storage.py          # Database table creation and loading
│   ├── analytics/              # Data analysis and reporting
│   │   ├── __init__.py
│   │   ├── consumption_queries.py  # Energy consumption statistics
│   │   └── stations_queries.py     # Fuel price and geographic analysis
│   ├── sql/                    # External SQL schema definitions
│   │   ├── consumption.sql     # Consumption table schema
│   │   └── stations.sql        # Stations table schema
│   ├── main.py                 # Unified entry point for all pipelines
│   ├── run_consumption_pipeline.py # Individual pipeline entry points
│   ├── run_stations_pipeline.py
│   └── run_analytics.py        # Database analytics runner
├── data/                       # Ignored by git (large data files)
│   ├── consumption.json        # Energy consumption data
│   ├── stations.json          # Fuel station data
│   └── energy-analytics.db    # DuckDB database
├── .gitignore                 # Comprehensive exclusion rules
├── pyproject.toml            # UV package management (Python 3.13+)
├── uv.lock                   # UV lock file
├── README.md                 # Updated to reflect current structure
└── CLAUDE.md                 # This file
```

## Database Schema
- **`consumption` table**: 3,024 hourly energy records (electricity/gas consumption in MW, Jan 1 - Mar 31, 2026)
- **`stations` table**: 9,775 fuel stations with current prices and locations

## Key Commands
```bash
# Run all pipelines (unified entry point) - from src directory
cd src
python main.py

# Run individual pipelines (from src directory)
cd src
python run_consumption_pipeline.py
python run_stations_pipeline.py

# Query database (analytics)
cd src
python run_analytics.py

# Dependencies
uv install  # Install dependencies from pyproject.toml

# Linting/type checking
# TODO: No linting/type checking commands configured yet
```

## APIs Used
1. **Energy Consumption**: `https://tabular-api.data.gouv.fr/api/resources/cfc27ff9-1871-4ee8-be64-b9a290c06935/data/`
2. **Fuel Prices**: `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records`

## Current Status ✅ STABLE STATE
- ✅ **Architecture**: Modular entity-based design with clean separation of concerns
- ✅ **Pipelines**: Two complete data pipelines with efficient date range fetching
- ✅ **Configuration**: JSON-based config system with external SQL schemas
- ✅ **Database**: DuckDB with 3,024 consumption records (3 months) and 9,775 fuel stations
- ✅ **Analytics**: Comprehensive statistics and reporting queries
- ✅ **Entry Points**: Unified main.py + individual pipeline runners
- ✅ **API Integration**: Proper use of date range operators for efficient data fetching

## Data Quality Notes
- Energy consumption: Complete 3-month dataset (3,024 records, Jan 1 - Mar 31, 2026)
- Electricity consumption range: 41,322 - 76,638 MW (avg: 59,091 MW)
- Fuel stations: Duplicate IDs handled by skipping (preserves first occurrence)
- Diesel price coverage: 98% of stations (9,579/9,775)
- Geographic coverage: All French departments represented

## Git Status
- **Current Branch**: `feature/modular-architecture`
- **Last Commit**: `60cd312` - "Restructure project with clean entity-based pipelines" 
- **Uncommitted Changes**: 
  - **MODIFIED**: `.gitignore` (enhanced exclusions)
  - **MODIFIED**: `README.md` (updated for current structure) 
  - **DELETED**: `scripts/consumption_pipeline.py`, `scripts/query_db.py`, `scripts/stations_pipeline.py`
  - **UNTRACKED**: `CLAUDE.md` (this file)
  - **UNTRACKED**: `nul` (Windows command output file - safe to delete)

## Next Steps - Priority Order
1. ✅ ~~Update `README.md` to reflect new `src/` structure instead of old `scripts/`~~
2. ✅ ~~Update documentation (CLAUDE.md and README.md) with current accurate state~~
3. **OPTIONAL**: Commit current changes including updated documentation
4. Enhanced data validation and error handling
5. Configure linting/type checking (ruff, mypy, etc.)
6. Improved duplicate handling (UPSERT vs current exception catching)  
7. Additional analysis queries as needed
8. Performance optimization for large datasets
9. Unit testing implementation
10. CI/CD pipeline setup

## Architecture Details
- **File Paths**: All use `../data/` directory (scripts run from src/ directory)
- **Modular Design**: Clear separation of concerns with dedicated entity modules
- **Database Path**: Relative path `../data/energy-analytics.db`
- **Naming Convention**: Entity-based naming (`consumption` and `stations`)
- **Utils Module**: Common functionality across all pipelines (database, API, file handling)
- **Configuration**: JSON config in `src/utils/config.json` with external SQL schemas
- **SQL Schemas**: External files in `src/sql/` directory for maintainability
- **Import Structure**: Relative imports within src/ modules with sys.path.append in runners
- **API Integration**: Two different government APIs with pagination and parameter handling

## Key Features
- **Efficient Date Range Fetching**: Uses proper API range operators (Date__greater/Date__less) for single-call data retrieval
- **Pagination Support**: Stations pipeline handles large datasets with offset-based pagination
- **Coordinate Processing**: Automatic coordinate scaling for fuel station locations
- **Comprehensive Analytics**: Statistical analysis with regional breakdowns and price comparisons
- **Error Handling**: Graceful handling of API errors and duplicate records
- **Configuration-driven**: API URLs and table schemas loaded from external config files

## Technical Notes
- **Path Dependencies**: Scripts must be run from `src/` directory due to relative paths
- **Data Storage**: JSON intermediates + DuckDB database for analysis
- **Import Strategy**: Individual runners use sys.path.append for module access
- **Duplicate Handling**: Stations with duplicate IDs skip insertion (preserves first occurrence)