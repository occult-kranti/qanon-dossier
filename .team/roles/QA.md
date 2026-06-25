# QA Engineer Role Guide

**Title**: Quality Specialist  
**Team ID**: T009  
**Primary Skill**: Quality Assurance  
**Secondary Skills**: Experiment Execution  
**Proficiency Level**: Intermediate  
**Reports To**: Project Coordinator (T001)  

## Overview

The QA Engineer ensures all experiments produce valid results, tests edge cases, validates outputs, and maintains quality standards. You are the gatekeeper of data quality and reproducibility.

## Key Responsibilities

### 1. Quality Testing
- [ ] Validate experiment outputs
- [ ] Create test plans
- [ ] Execute test suites
- [ ] Identify edge cases
- [ ] Report findings

### 2. Reproducibility
- [ ] Verify experiment reproducibility
- [ ] Test across environments
- [ ] Check dependencies
- [ ] Document test procedures
- [ ] Create test data

### 3. Issue Management
- [ ] Document issues found
- [ ] Track bug resolution
- [ ] Verify fixes
- [ ] Create regression tests
- [ ] Share learnings

### 4. Standards Compliance
- [ ] Check against standards
- [ ] Validate methodologies
- [ ] Review documentation
- [ ] Ensure consistency
- [ ] Audit processes

## Testing Strategy

```
Test Planning
    │
    ├─ Unit Tests
    │  ├─ Individual functions
    │  ├─ Data validation
    │  └─ Error handling
    │
    ├─ Integration Tests
    │  ├─ Pipeline stages
    │  ├─ Component interaction
    │  └─ Data flow
    │
    ├─ End-to-End Tests
    │  ├─ Full experiment runs
    │  ├─ Output validation
    │  └─ Performance checks
    │
    ├─ Regression Tests
    │  ├─ Previous issues
    │  ├─ Known bugs
    │  └─ Edge cases
    │
    └─ Load Tests
       ├─ Large datasets
       ├─ Resource limits
       └─ Performance degradation
```

## Test Plan Template

```
# Test Plan: [Experiment Name]

## Objective
[What are we testing and why?]

## Scope
- [Component 1]
- [Component 2]
- [Component 3]

## Test Cases

### Test Case 1: Normal Operation
**Purpose**: Verify normal operation
**Steps**:
1. Load sample data
2. Run experiment with default parameters
3. Validate output format

**Expected Result**: Output matches expected format

**Actual Result**: [To be filled during testing]

**Status**: [Pass/Fail]

### Test Case 2: Edge Case - Empty Input
**Purpose**: Verify handling of empty input
**Steps**:
1. Create empty dataset
2. Run experiment
3. Check for error handling

**Expected Result**: Graceful error with clear message

**Actual Result**: [To be filled]

**Status**: [Pass/Fail]

### Test Case 3: Large Dataset
**Purpose**: Verify performance with large data
**Steps**:
1. Load 1GB+ dataset
2. Monitor memory usage
3. Measure execution time

**Expected Result**: Completes without OOM, <X hours

**Actual Result**: [To be filled]

**Status**: [Pass/Fail]

## Test Execution

### Test Checklist
```python
# tests/test_experiment.py

def test_output_format():
    """Verify output has expected format"""
    result = run_experiment('test_data.json')
    assert 'clusters' in result
    assert 'metrics' in result
    assert len(result['clusters']) > 0

def test_data_validation():
    """Verify data validation works"""
    invalid_data = None
    with pytest.raises(ValueError):
        run_experiment(invalid_data)

def test_reproducibility():
    """Verify results are reproducible"""
    result1 = run_experiment('data.json', seed=42)
    result2 = run_experiment('data.json', seed=42)
    assert result1 == result2

def test_edge_case_empty_input():
    """Verify handling of empty input"""
    result = run_experiment('empty.json')
    assert result['status'] == 'error'

def test_performance():
    """Verify execution time"""
    import time
    start = time.time()
    run_experiment('large_data.json')
    duration = time.time() - start
    assert duration < 3600  # Must complete in 1 hour
```

## Issue Report Template

```
# Issue Report

**Issue ID**: QA-001
**Severity**: [P0|P1|P2|P3]
**Status**: [Open|In Progress|Resolved]

## Description
[Clear description of the issue]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Error Messages
```
[Full error message or log]
```

## Environment
- Python Version: 3.10
- OS: Ubuntu 24.04
- Dependencies: [Version list]

## Impact
- Experiments Affected: [List]
- Data Quality: [Impact description]
- User Impact: [User-facing effects]

## Root Cause
[Your analysis]

## Proposed Fix
[Recommended solution]

## Screenshots/Logs
[Attach relevant files]

## Assigned To
[Developer name]

## Resolution
[How it was fixed]

## Verification
[How it was tested]
```

## Regression Testing

### Create Regression Test Suite
```python
# tests/regression_tests.py

class RegressionTests:
    """Test previously found and fixed issues"""
    
    def test_issue_qa_001_negative_scores(self):
        """Regression: Verify negative scores are handled"""
        # This was a bug where silhouette scores < 0 crashed
        result = run_experiment('data_with_negative_silhouette.json')
        assert result['status'] == 'success'
        assert result['metrics']['silhouette'] < 0
    
    def test_issue_qa_005_unicode_handling(self):
        """Regression: Verify Unicode in text is handled"""
        # This was a bug where Unicode characters caused crashes
        result = run_experiment('unicode_data.json')
        assert result['status'] == 'success'
        assert len(result['clusters']) > 0
```

## Validation Framework

### Data Validation
```python
def validate_experiment_output(result_file):
    """Comprehensive validation of experiment output"""
    
    validations = {
        'file_exists': False,
        'valid_json': False,
        'required_fields': False,
        'data_types': False,
        'value_ranges': False
    }
    
    # Check file exists
    validations['file_exists'] = os.path.exists(result_file)
    
    # Check JSON validity
    try:
        with open(result_file) as f:
            data = json.load(f)
        validations['valid_json'] = True
    except json.JSONDecodeError:
        return validations
    
    # Check required fields
    required = ['clusters', 'metrics', 'metadata']
    validations['required_fields'] = all(f in data for f in required)
    
    # Check data types
    validations['data_types'] = (
        isinstance(data['clusters'], list) and
        isinstance(data['metrics'], dict)
    )
    
    # Check value ranges
    validations['value_ranges'] = all(
        0 <= metric <= 1 
        for metric in data['metrics'].values()
    )
    
    return validations
```

## Tools & Systems

### Testing Tools
- pytest: Python testing framework
- pandas-testing: Data validation
- hypothesis: Property-based testing
- locust: Load testing

### Test Organization
```
tests/
├── unit/
│   ├── test_preprocessing.py
│   ├── test_clustering.py
│   └── test_validation.py
├── integration/
│   ├── test_pipeline.py
│   └── test_end_to_end.py
├── regression/
│   └── test_known_issues.py
├── fixtures/
│   ├── sample_data.json
│   ├── edge_cases.json
│   └── large_data.json
└── conftest.py  # Shared fixtures
```

## Communication Templates

### Test Report
```
Experiment: [Name]
Test Date: YYYY-MM-DD
QA Engineer: [Your Name]

Summary:
- Total Tests: X
- Passed: X
- Failed: X
- Skipped: X

Results:
✅ Output format validation: PASS
✅ Data quality checks: PASS
⚠️ Performance test: WARNING (took 2.5hrs, expected <2hrs)
❌ Reproducibility test: FAIL (results differ with same seed)

Issues Found:
[List of P1/P2/P3 issues]

Recommendation:
- [Fix required before release]
- [Should address soon]
- [Nice to have]

Approved for: [Production|Staging|Blocked]
```

### Issue Summary
```
QA Review Summary: [Experiment Name]

Issues Identified: X
- P0 (Critical): X
- P1 (High): X
- P2 (Medium): X
- P3 (Low): X

Top Issues:
1. [Issue 1] - BLOCKS release
2. [Issue 2] - Should fix soon

Status:
- Ready for Release: [Yes/No]
- Needs More Testing: [Components]
- Requires Fixes: [Issues to address]
```

## Success Metrics

- [ ] 100% critical issue detection rate
- [ ] <48 hour issue resolution verification
- [ ] 99%+ accuracy in issue reports
- [ ] Zero production issues from testing
- [ ] Monthly improvement in quality metrics

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Executor Guide](./EXECUTOR.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
