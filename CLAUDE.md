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

## Development Notes
**Windows Console Encoding Issue:** When running Python scripts via Bash tool, avoid Unicode characters (emojis, special symbols) in print statements as Windows console uses cp1252 encoding which causes `UnicodeEncodeError`. Use plain ASCII text instead.

## APIs Used
1. **Energy Consumption**: `https://tabular-api.data.gouv.fr/api/resources/cfc27ff9-1871-4ee8-be64-b9a290c06935/data/`
2. **Fuel Prices**: `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records`

## Current Status ✅ PRODUCTION-READY WITH MODERN TYPE HINTING
- ✅ **Architecture**: Full OOP implementation with class hierarchy and inheritance
- ✅ **Type Hinting**: Modern Python 3.10+ syntax (Union operators, built-in generics)
- ✅ **Pydantic Dataclasses**: Modern dataclass approach with @property decorators
- ✅ **English Naming**: All field names converted from French to English
- ✅ **Configuration Classes**: BaseConfiguration with DataGouv/EconomieGouv implementations
- ✅ **Pipeline Classes**: Complete BasePipeline, BaseProcessor, BaseStorage abstractions
- ✅ **Configuration Manager**: Centralized ConfigurationManager with factory patterns
- ✅ **Pipelines**: ConsumptionPipeline and StationsPipeline with full OOP encapsulation
- ✅ **Database**: DuckDB with modern database management patterns
- ✅ **Context Managers**: Automatic resource management throughout codebase
- ✅ **Bulk Import Optimization**: 200x+ performance improvement with read_json_auto()
- ✅ **Schema Coherence**: Complete JSON-to-database field mapping
- ✅ **Analytics**: Comprehensive statistics and reporting queries
- ✅ **Entry Points**: Unified OOP main.py + individual pipeline runners
- ✅ **Pipeline Fixes**: UTF-8 encoding, error handling, API pagination working
- ✅ **Legacy Cleanup**: All redundant code removed, production-ready

## Data Quality Notes
- Energy consumption: Complete 3-month dataset (3,024 records, Jan 1 - Mar 31, 2026)
- Electricity consumption range: 41,322 - 76,638 MW (avg: 59,091 MW)
- Fuel stations: Current dataset (9,772 active stations with real-time prices)
- Diesel price coverage: 98% of stations have pricing data
- Geographic coverage: All French departments represented
- UTF-8 encoding: Properly handles French accented characters

## Git Status
- **Current Branch**: `main`
- **Last Commit**: `5e00d23` - "feat: implement modern database management patterns"
- **Architecture**: Complete OOP implementation with modern database patterns
- **Recent Changes**:
  - **COMPLETED**: Modern database management with context managers
  - **COMPLETED**: Bulk import optimization (200x+ performance improvement)
  - **COMPLETED**: English field name conversion and Pydantic dataclasses
  - **COMPLETED**: Complete OOP pipeline architecture implementation
  - **WORKING TREE**: Clean, no untracked files

## Database Management Modernization ✅ COMPLETED
**Implemented advanced database patterns based on trainer's approach:**

### **1. Context Manager Pattern**
- **Before**: Manual `try/finally` blocks in 15+ locations
- **After**: Clean `with DuckDBConnection()` statements
- **Benefits**: Automatic resource cleanup, no connection leaks
- **Implementation**: `DuckDBConnection` class in `src/utils/database.py`

### **2. Bulk Import Optimization**  
- **Before**: 12,796 individual INSERT operations (Python loops)
- **After**: 2 bulk operations with `read_json_auto()`
- **Performance**: 200x+ improvement (67,581 records/second)
- **Implementation**: SQL-based bulk imports in both pipelines

### **3. Raw Data Philosophy**
- **Approach**: Preserve all source data with clean English schemas
- **Schema**: Complete JSON field mapping with proper types
- **Benefits**: Data integrity + readable analytics
- **Tables**: Both `consumption` and `stations` fully coherent

### **4. Code Cleanup**
- **Removed**: Duplicate coordinate processing functions
- **Removed**: Legacy database utility functions  
- **Removed**: Unused imports and redundant code
- **Result**: Clean, maintainable production code

## Type Hinting Modernization ✅ COMPLETED
**Upgraded from trainer's traditional approach to modern Python 3.10+ syntax:**

### **Trainer's Approach** (cours_python_avance-18.la_librairie_typing):
```python
from typing import List, Union, Optional
typing.List[typing.Union[EconomieGouvConfiguration, DataGouvConfiguration]]
def function(param: List[Dict]) -> Optional[str]:
```

### **Your Modern Implementation**:
```python
from typing import Optional  # minimal imports
BaseConfiguration = DataGouvConfiguration | EconomieGouvConfiguration  # Union operator
def function(param: list[dict]) -> str | None:  # Built-in generics + Union syntax
```

### **Key Improvements**:
- **`List[Dict]` → `list[dict]`**: Using built-in generics (Python 3.9+)
- **`Optional[str]` → `str | None`**: Union operators (Python 3.10+)
- **`Union[A, B]` → `A | B`**: Cleaner syntax
- **Reduced imports**: Removed `typing.List, Dict, Union`
- **Comprehensive coverage**: All function parameters and returns typed
- **Inheritance consistency**: Types maintained across abstract base classes

## Next Steps - Priority Order
1. ✅ ~~Implement configuration classes with inheritance~~
2. ✅ ~~Create pipeline base classes and implementations~~
3. ✅ ~~Add factory patterns and ConfigurationManager~~
4. ✅ ~~Convert to Pydantic dataclasses with @property decorators~~
5. ✅ ~~Convert French field names to English naming~~
6. ✅ ~~Remove unused legacy compatibility functions~~
7. ✅ ~~Update documentation to reflect current state~~
8. ✅ ~~Implement modern database management patterns~~
9. ✅ ~~Modernize type hinting with Python 3.10+ syntax~~
10. Implement advanced logging system (based on trainer's approach)
11. Configure linting/type checking (ruff, mypy, etc.)
12. Unit testing implementation with OOP structure
13. Performance monitoring and optimization
14. CI/CD pipeline setup

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