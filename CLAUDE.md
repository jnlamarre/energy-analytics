# Energy Analytics Project - Claude Context

## Project Overview
French energy data analytics project with two main data pipelines:
1. **Energy Consumption Data**: Hourly electricity/gas consumption from French grid
2. **Fuel Station Prices**: Real-time fuel prices from 9,700+ stations across France

## Current Project Structure - Object-Oriented Architecture
```
energy-analytics/
├── src/                        # Object-oriented pipeline architecture
│   ├── __init__.py
│   ├── utils/                  # Core utilities and base classes
│   │   ├── __init__.py
│   │   ├── api_client.py       # HTTP request handling with pagination support
│   │   ├── database.py         # DuckDB connection and query operations
│   │   ├── file_handler.py     # JSON save/load operations
│   │   ├── config.py           # Modern OOP interface
│   │   ├── config.json         # API endpoints and table configuration
│   │   ├── configuration_classes.py # OOP configuration classes & manager
│   │   └── pipeline_classes.py     # Base pipeline, processor, and storage classes
│   ├── pipelines/              # OOP pipeline implementations
│   │   ├── __init__.py
│   │   ├── consumption_pipeline.py # Complete consumption pipeline class
│   │   └── stations_pipeline.py    # Complete stations pipeline class
│   ├── analytics/              # Data analysis and reporting
│   │   ├── __init__.py
│   │   ├── consumption_queries.py  # Energy consumption statistics
│   │   └── stations_queries.py     # Fuel price and geographic analysis
│   ├── sql/                    # External SQL schema definitions
│   │   ├── consumption.sql     # Consumption table schema
│   │   └── stations.sql        # Stations table schema
│   ├── main.py                 # Unified OOP entry point for all pipelines
│   ├── run_consumption_pipeline.py # Individual OOP pipeline runners
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
- **`stations` table**: 9,772 fuel stations with current prices and locations

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

## Current Status ✅ CLEAN OOP ARCHITECTURE WITH ENGLISH NAMING
- ✅ **Architecture**: Full OOP implementation with class hierarchy and inheritance
- ✅ **Pydantic Dataclasses**: Modern dataclass approach with @property decorators
- ✅ **English Naming**: All field names converted from French to English
- ✅ **Configuration Classes**: BaseConfiguration with DataGouv/EconomieGouv implementations
- ✅ **Pipeline Classes**: Complete BasePipeline, BaseProcessor, BaseStorage abstractions
- ✅ **Configuration Manager**: Centralized ConfigurationManager with factory patterns
- ✅ **Pipelines**: ConsumptionPipeline and StationsPipeline with full OOP encapsulation
- ✅ **Database**: DuckDB with 3,024 consumption records (3 months) and 9,772 fuel stations
- ✅ **Analytics**: Comprehensive statistics and reporting queries
- ✅ **Entry Points**: Unified OOP main.py + individual pipeline runners
- ✅ **Legacy Cleanup**: Unused legacy compatibility functions removed

## Data Quality Notes
- Energy consumption: Complete 3-month dataset (3,024 records, Jan 1 - Mar 31, 2026)
- Electricity consumption range: 41,322 - 76,638 MW (avg: 59,091 MW)
- Fuel stations: Duplicate IDs handled by skipping (preserves first occurrence)
- Diesel price coverage: 98% of stations (9,546/9,772)
- Geographic coverage: All French departments represented

## Git Status
- **Current Branch**: `refactor/config-classes`
- **Last Commit**: `e16edf3` - "Convert to English naming and remove legacy functions"
- **Architecture**: Complete OOP implementation with Pydantic dataclasses
- **Recent Changes**:
  - **COMPLETED**: English field name conversion (api_type, target_file, table_name, sql_file)
  - **COMPLETED**: Pydantic dataclasses with @property decorators
  - **COMPLETED**: Legacy function cleanup in config.py
  - **COMPLETED**: Pipeline updates to use property access instead of method calls
  - **WORKING TREE**: Clean, all changes committed

## Next Steps - Priority Order
1. ✅ ~~Implement configuration classes with inheritance~~
2. ✅ ~~Create pipeline base classes and implementations~~
3. ✅ ~~Add factory patterns and ConfigurationManager~~
4. ✅ ~~Convert to Pydantic dataclasses with @property decorators~~
5. ✅ ~~Convert French field names to English naming~~
6. ✅ ~~Remove unused legacy compatibility functions~~
7. ✅ ~~Update documentation to reflect current state~~
8. **OPTIONAL**: Enhanced data validation and error handling
9. Configure linting/type checking (ruff, mypy, etc.)
10. Improved duplicate handling (UPSERT vs current exception catching)  
11. Unit testing implementation with OOP structure
12. Performance optimization for large datasets
13. CI/CD pipeline setup

## OOP Architecture Details
- **Class Hierarchy**: BaseConfiguration → DataGouv/EconomieGouvConfiguration inheritance
- **Pipeline Classes**: BasePipeline → ConsumptionPipeline/StationsPipeline implementations
- **Factory Pattern**: BaseConfiguration.create_from_dict() for polymorphic object creation
- **Configuration Manager**: Centralized ConfigurationManager for all config operations
- **Base Classes**: BaseProcessor and BaseStorage with common functionality
- **Encapsulation**: Each pipeline encapsulates fetch → process → store → database operations
- **Polymorphism**: Same interface works for different API types and data sources
- **File Paths**: All use `../data/` directory (scripts run from src/ directory)
- **Database Path**: Relative path `../data/energy-analytics.db`
- **Modern Interface**: Clean OOP interface with legacy functions removed
- **SQL Integration**: Schema loading integrated into configuration class initialization

## Key OOP Features
- **Pydantic Dataclasses**: Modern dataclass approach with automatic validation
- **@property Decorators**: Dynamic URL building and computed attributes
- ****kwargs Unpacking**: Flexible object creation from configuration dictionaries
- **Inheritance**: Clear inheritance hierarchy for configurations and pipelines
- **Factory Methods**: Automatic object creation based on configuration type
- **Composition**: Pipelines compose processor and storage objects
- **Manager Pattern**: ConfigurationManager centralizes configuration logic
- **Abstract Base Classes**: Define clear interfaces for extensibility
- **Run-time Polymorphism**: Same pipeline interface for different data sources
- **English Naming**: Consistent English field names throughout codebase

## Technical Implementation
- **Path Dependencies**: Scripts must be run from `src/` directory due to relative paths
- **Data Storage**: JSON intermediates + DuckDB database for analysis
- **Object Instantiation**: ConfigurationManager.get_configuration_by_table()
- **Pipeline Execution**: pipeline.run_full_pipeline() for complete data flow
- **Error Handling**: Graceful handling through inheritance and method overrides