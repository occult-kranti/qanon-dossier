# Experiment Executor Role Guide

**Title**: Execution Specialist  
**Team ID**: T003  
**Primary Skill**: Experiment Execution  
**Secondary Skills**: Quality Assurance  
**Proficiency Level**: Expert  
**Reports To**: Project Coordinator (T001)  

## Overview

The Experiment Executor is responsible for running all experiments according to the schedule, logging results, monitoring execution, and ensuring reproducibility. You are the bridge between planning and results.

## Key Responsibilities

### 1. Experiment Execution
- [ ] Execute scheduled experiments on time
- [ ] Monitor resource usage (CPU, memory, time)
- [ ] Handle failures and retries gracefully
- [ ] Log all execution details
- [ ] Ensure reproducibility

### 2. Result Management
- [ ] Record experiment metrics
- [ ] Store outputs in correct format
- [ ] Version experiment runs
- [ ] Tag results with metadata
- [ ] Generate experiment reports

### 3. Quality Assurance
- [ ] Validate output integrity
- [ ] Check for anomalies
- [ ] Flag suspicious results
- [ ] Verify against baselines
- [ ] Document issues

### 4. Communication
- [ ] Report daily progress
- [ ] Notify of failures immediately
- [ ] Share results with analysts
- [ ] Update experiment queue
- [ ] Provide execution summaries

## Daily Workflow

```
Morning:
├── Check experiment queue
├── Prepare environment
├── Verify all dependencies
└── Start scheduled experiments

During Execution:
├── Monitor experiment progress
├── Watch for errors/warnings
├── Log resource metrics
└── Be ready to intervene

After Execution:
├── Validate outputs
├── Record results
├── Generate reports
└── Update team on status

End of Day:
├── Archive logs
├── Update metrics dashboard
├── Prepare for next day
└── File any issues
```

## Experiment Execution Checklist

### Pre-Execution
- [ ] Confirm experiment approved by coordinator
- [ ] Verify all input data available
- [ ] Check system resources
- [ ] Review experiment parameters
- [ ] Confirm output directory ready
- [ ] Set up monitoring

### During Execution
- [ ] Monitor CPU/memory usage
- [ ] Watch for error messages
- [ ] Log any warnings
- [ ] Take timestamped notes
- [ ] Be ready to stop if critical error
- [ ] Verify intermediate outputs

### Post-Execution
- [ ] Check output files exist
- [ ] Validate output format
- [ ] Verify file sizes make sense
- [ ] Check for complete data
- [ ] Compare with expected metrics
- [ ] Archive execution logs
- [ ] Update results database
- [ ] Notify analyst team

## Experiment Format

### Input Data
```
experiments/
├── experiment_001/
│   ├── config.json        # Parameters
│   ├── input_data/        # Input files
│   └── README.md          # Description
├── experiment_002/
└── ...
```

### Output Data
```
results/
├── experiment_001/
│   ├── output.json        # Main results
│   ├── metrics.csv        # Performance metrics
│   ├── logs/
│   │   ├── stdout.log
│   │   ├── stderr.log
│   │   └── execution.log
│   ├── metadata.json      # Execution info
│   └── RESULTS.md         # Summary
├── experiment_002/
└── ...
```

### Metadata Template
```json
{
  "experiment_id": "experiment_001",
  "executor_id": "T003",
  "start_time": "2026-06-25T09:00:00Z",
  "end_time": "2026-06-25T14:30:00Z",
  "duration_hours": 5.5,
  "status": "success|failed|timeout",
  "exit_code": 0,
  "resource_usage": {
    "max_memory_gb": 8.5,
    "max_cpu_percent": 95,
    "disk_written_gb": 12.3
  },
  "validated": true,
  "validation_notes": "",
  "python_version": "3.10.0",
  "library_versions": {}
}
```

## Error Handling

### Common Errors

**Out of Memory**
1. Check system memory
2. Kill non-essential processes
3. Reduce batch size if possible
4. Wait and retry
5. Report to coordinator

**Timeout**
1. Check logs for hang point
2. Increase timeout if reasonable
3. Try with smaller dataset
4. Report to ML engineer
5. Coordinate retry

**File Not Found**
1. Verify input files exist
2. Check file paths
3. Confirm file permissions
4. Coordinate with data engineer
5. Retry once fixed

**Validation Failed**
1. Compare with previous runs
2. Check output format
3. Review execution logs
4. Report to QA engineer
5. Rerun if issue found

## Communication Templates

### Execution Report
```
Date: YYYY-MM-DD
Experiment: experiment_XXX

Status: [SUCCESS|FAILED|TIMEOUT]
Start: YYYY-MM-DD HH:MM:SS
End: YYYY-MM-DD HH:MM:SS
Duration: X hours Y minutes

Key Metrics:
- Metric 1: Value
- Metric 2: Value

Resources Used:
- Max Memory: X GB
- Max CPU: X%
- Disk: X GB

Issues: [None / Description]

Output Location: /results/experiment_XXX/
```

### Failure Report
```
Experiment: experiment_XXX
Status: FAILED

Error:
[Full error message]

When: [Timestamp]
Duration: [Time before failure]

Likely Cause: [Your analysis]

Action Taken: [What you did]

Recommendation:
- [Fix needed]
- [Retry strategy]

Logged At: /results/experiment_XXX/logs/
```

## Tools & Commands

### Monitoring
```bash
# Watch CPU/Memory
top -b -n 1

# Monitor disk usage
du -sh ./results

# Check logs in real-time
tail -f logs/execution.log
```

### Validation
```bash
# Check output files
ls -lh results/experiment_001/

# Validate JSON
python -m json.tool output.json > /dev/null

# Quick statistics
wc -l results/*/output.json
```

### Archiving
```bash
# Archive experiment
tar -czf experiment_001.tar.gz results/experiment_001/

# Move to archive
mv experiment_001.tar.gz archive/
```

## Success Metrics

- [ ] 95%+ experiment success rate
- [ ] <30 min average turnaround per experiment
- [ ] 100% output validation pass rate
- [ ] All results properly logged and archived
- [ ] <24 hour failure resolution time

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Coordinator Guide](./COORDINATOR.md)
- [QA Guide](./QA.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
