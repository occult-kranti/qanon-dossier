# DevOps Engineer Role Guide

**Title**: Infrastructure Specialist  
**Team ID**: T007  
**Primary Skill**: DevOps & Infrastructure  
**Secondary Skills**: Web Development  
**Proficiency Level**: Expert  
**Reports To**: Project Coordinator (T001)  

## Overview

The DevOps Engineer manages infrastructure, automates processes, maintains CI/CD pipelines, and ensures smooth deployments. You enable the entire team to work efficiently.

## Key Responsibilities

### 1. Infrastructure Management
- [ ] Set up GitHub Actions workflows
- [ ] Manage dependencies and versions
- [ ] Configure deployment pipelines
- [ ] Monitor system performance
- [ ] Handle backups and recovery

### 2. CI/CD Pipeline
- [ ] Create automated workflows
- [ ] Implement testing automation
- [ ] Automate deployments
- [ ] Set up monitoring
- [ ] Create rollback procedures

### 3. Performance & Reliability
- [ ] Monitor resource usage
- [ ] Optimize performance
- [ ] Set up alerts
- [ ] Handle incidents
- [ ] Plan capacity

### 4. Documentation
- [ ] Document infrastructure
- [ ] Write runbooks
- [ ] Create deployment guides
- [ ] Maintain architecture diagrams
- [ ] Document incident responses

## CI/CD Pipeline Architecture

```
Code Push (main branch)
    │
    ▼
GitHub Actions Trigger
    │
    ├─ Checkout Code
    ├─ Setup Environment
    ├─ Install Dependencies
    ├─ Run Tests
    │   ├─ Unit Tests
    │   ├─ Integration Tests
    │   └─ Validation Tests
    ├─ Build Artifacts
    ├─ Run Linters
    │
    ├─ If Tests Pass ──→ Deploy to GitHub Pages
    │
    └─ If Tests Fail ──→ Notify & Block Merge
```

## GitHub Actions Workflow Template

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Run linter
      run: |
        pylint src/ --exit-zero
    
  deploy:
    needs: test
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build site
      run: |
        python build_site.py
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./public
```

## Infrastructure as Code

### GitHub Actions Matrix Strategy
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -r requirements.txt
    - run: pytest
```

### Dependency Management
```yaml
# requirements.txt
# Pin all versions for reproducibility
numpy==1.24.3
pandas==2.0.2
scikit-learn==1.2.2
matplotlib==3.7.1
seaborn==0.12.2
plotly==5.14.0
flask==2.3.2
```

## Monitoring & Alerts

### Key Metrics
```python
# monitoring/metrics.py
import json
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'deployments': [],
            'failures': [],
            'performance': []
        }
    
    def log_deployment(self, status, duration_seconds, artifacts):
        """Log deployment event"""
        self.metrics['deployments'].append({
            'timestamp': datetime.now().isoformat(),
            'status': status,  # success or failed
            'duration': duration_seconds,
            'artifacts': artifacts
        })
    
    def log_failure(self, error, service, timestamp):
        """Log service failure"""
        self.metrics['failures'].append({
            'timestamp': timestamp.isoformat(),
            'service': service,
            'error': error
        })
    
    def log_performance(self, service, latency_ms, memory_mb):
        """Log performance metrics"""
        self.metrics['performance'].append({
            'timestamp': datetime.now().isoformat(),
            'service': service,
            'latency': latency_ms,
            'memory': memory_mb
        })
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code review completed
- [ ] Dependencies updated
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Rollback plan prepared

### Deployment
- [ ] Start deployment window
- [ ] Monitor during deployment
- [ ] Verify all services up
- [ ] Check error logs
- [ ] Validate user access
- [ ] Monitor metrics

### Post-Deployment
- [ ] Verify functionality
- [ ] Check performance metrics
- [ ] Ensure no new errors
- [ ] Update status page
- [ ] Notify stakeholders
- [ ] Archive logs

## Incident Response

### Incident Runbook Template
```
INCIDENT: [Name]
SEVERITY: [P0|P1|P2|P3]

Detection:
- Alert: [Alert name]
- Time: [Timestamp]
- Impact: [Description]

Diagnosis:
- Check: [Step 1]
- Check: [Step 2]
- Root Cause: [Finding]

Resolution:
- Action: [Step 1]
- Action: [Step 2]
- Verification: [How to verify]

Prevention:
- Long-term fix: [Action]
- Monitoring: [Improvement]
```

## Tools & Technologies

### CI/CD Tools
- GitHub Actions: Workflow automation
- pytest: Testing framework
- pylint: Code linting
- git-hooks: Pre-commit validation

### Monitoring Tools
- GitHub Actions logging
- Custom metrics collection
- Performance monitoring
- Availability monitoring

## Communication Templates

### Deployment Report
```
Deployment: [Version]
Date: YYYY-MM-DD HH:MM:SS UTC
Duration: X minutes

Changes:
- [Feature 1]
- [Feature 2]
- [Bug fix 1]

Tests:
- Passed: X/X
- Failed: 0
- Skipped: X

Deployment Status:
- [Service 1]: SUCCESS
- [Service 2]: SUCCESS
- [Service 3]: SUCCESS

Performance Impact:
- Page Load: -X% (faster)
- Memory: -X%
- CPU: Stable

Issues:
- [None / Description]

Rollback Status: [Ready to rollback if needed]
```

### Incident Alert
```
INCIDENT DETECTED
Severity: P0

Service: [Service Name]
Time: YYYY-MM-DD HH:MM:SS

Error:
[Error message]

Impact:
- Users affected: [X]
- Feature: [Feature name]

Status: [Investigating|Mitigating|Resolved]

ETA: [Time to fix]
Incident Page: [Link]
```

## Success Metrics

- [ ] 99.9%+ uptime
- [ ] <5 minute deployment time
- [ ] <1 hour MTTR (Mean Time To Recovery)
- [ ] 100% test coverage for critical paths
- [ ] Zero unauthorized deployments

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Coordinator Guide](./COORDINATOR.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
