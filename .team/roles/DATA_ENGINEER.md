# Data Engineer Role Guide

**Title**: Data Specialist  
**Team ID**: T002  
**Primary Skill**: Data Engineering  
**Secondary Skills**: DevOps & Infrastructure  
**Proficiency Level**: Intermediate  
**Reports To**: Project Coordinator (T001)  

## Overview

The Data Engineer is responsible for managing all data sources, creating robust pipelines, ensuring data quality, and maintaining data schemas. You ensure that clean, validated data flows to all downstream processes.

## Key Responsibilities

### 1. Data Management
- [ ] Manage multiple data sources
- [ ] Create data pipelines
- [ ] Validate data quality
- [ ] Document data schemas
- [ ] Version data assets

### 2. Data Pipeline Development
- [ ] Extract data from sources
- [ ] Transform and normalize data
- [ ] Load data into experiments
- [ ] Handle missing values
- [ ] Create backup systems

### 3. Data Quality
- [ ] Implement validation rules
- [ ] Monitor data integrity
- [ ] Identify and fix data issues
- [ ] Create quality reports
- [ ] Document data lineage

### 4. Documentation
- [ ] Document data schemas
- [ ] Create data dictionaries
- [ ] Write pipeline documentation
- [ ] Maintain data catalog
- [ ] Record data sources

## Data Architecture

```
Data Sources
├── Dataset 1 (CSV/JSON)
├── Dataset 2 (API)
├── Dataset 3 (Database)
└── Dataset 4 (Files)
        │
        ▼
   Data Pipelines
├── Extract Layer
├── Transform Layer
├── Validate Layer
└── Load Layer
        │
        ▼
   Validated Datasets
├── dataset_001_cleaned.json
├── dataset_002_processed.csv
├── dataset_003_indexed.pkl
└── dataset_004_aggregated.json
        │
        ▼
   Experiments
├── experiment_001/input_data/
├── experiment_002/input_data/
└── ...
```

## Daily Workflow

```
Morning:
├── Check data quality metrics
├── Review overnight data loads
├── Check for new data sources
└── Review pipeline logs

Afternoon:
├── Handle data requests
├── Monitor pipeline performance
├── Address data issues
└── Create validation reports

Evening:
├── Run nightly validation checks
├── Archive and backup data
├── Generate quality metrics
└── Update data catalog
```

## Data Schemas

### Template: Dataset Schema

```json
{
  "dataset_id": "dataset_001",
  "name": "Q Drops Analysis Dataset",
  "description": "Complete collection of Q drops with metadata",
  "source": "URL/API/Database",
  "format": "JSON/CSV/Parquet",
  "size_mb": 1024,
  "record_count": 50000,
  "last_updated": "2026-06-25",
  "update_frequency": "daily",
  "schemas": [
    {
      "field": "id",
      "type": "integer",
      "required": true,
      "description": "Unique identifier"
    },
    {
      "field": "timestamp",
      "type": "datetime",
      "required": true,
      "description": "Publication timestamp"
    },
    {
      "field": "content",
      "type": "string",
      "required": true,
      "description": "Full text content"
    }
  ],
  "quality_rules": [
    "No null values in required fields",
    "Timestamp must be valid date",
    "Content length > 0"
  ]
}
```

## Pipeline Templates

### ETL Pipeline Structure
```python
# pipeline_001.py
import json
from datetime import datetime

class DataPipeline:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.timestamp = datetime.now()
        
    def extract(self):
        """Extract data from source"""
        # Implement extraction logic
        pass
        
    def transform(self):
        """Transform and normalize data"""
        # Implement transformation logic
        pass
        
    def validate(self):
        """Validate data quality"""
        # Implement validation logic
        pass
        
    def load(self):
        """Load into target location"""
        # Implement loading logic
        pass
        
    def run(self):
        """Execute full pipeline"""
        self.extract()
        self.transform()
        self.validate()
        self.load()
```

## Data Quality Checks

### Standard Validations
```python
def validate_dataset(data, schema):
    issues = []
    
    # Check required fields
    for record in data:
        for field in schema['required_fields']:
            if field not in record or record[field] is None:
                issues.append(f"Missing {field} in record {record['id']}")
    
    # Check data types
    for record in data:
        for field, field_type in schema['field_types'].items():
            if not isinstance(record[field], field_type):
                issues.append(f"Wrong type for {field} in record {record['id']}")
    
    # Check value ranges
    for record in data:
        for field, bounds in schema['ranges'].items():
            if not bounds['min'] <= record[field] <= bounds['max']:
                issues.append(f"Value out of range for {field} in record {record['id']}")
    
    return issues
```

## Tools & Systems

### Data Tools
- Python/Pandas: Data processing
- JSON: Configuration and metadata
- SQL: If database backend
- Git: Version control for data configs

### Files to Maintain
```
data/
├── sources/          # Raw data sources
├── pipelines/        # ETL scripts
├── schemas/          # Schema definitions
├── quality_reports/  # Validation reports
└── catalog.json      # Data catalog
```

## Communication Templates

### Data Issue Report
```
Dataset: [dataset_name]
Issue: [Brief description]

Severity: [P0|P1|P2|P3]
Records Affected: [Number]
Percentage: [X%]

Details:
[Full description with examples]

Root Cause:
[Your analysis]

Fix:
[Proposed solution]

Timeline:
- Identified: YYYY-MM-DD
- Fix Applied: YYYY-MM-DD
- Validated: YYYY-MM-DD
```

### Data Quality Report
```
Dataset: [dataset_name]
Report Date: YYYY-MM-DD

Metrics:
- Total Records: X
- Valid Records: X (X%)
- Invalid Records: X (X%)
- Missing Values: X%
- Duplicates: X

Issues Found:
[List of issues by severity]

Validations Passed:
- [Check 1]: PASS
- [Check 2]: PASS

Next Steps:
[Recommendations]
```

## Success Metrics

- [ ] 99%+ data validation pass rate
- [ ] <1 hour average issue resolution
- [ ] Zero data loss incidents
- [ ] 100% schema documentation
- [ ] Daily automated backup completion

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Coordinator Guide](./COORDINATOR.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
