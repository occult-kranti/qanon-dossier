# Data Analyst Role Guide

**Title**: Analysis Specialist  
**Team ID**: T005  
**Primary Skill**: Analysis & Visualization  
**Secondary Skills**: Documentation  
**Proficiency Level**: Intermediate  
**Reports To**: Project Coordinator (T001)  

## Overview

The Data Analyst transforms experiment results into actionable insights, creates compelling visualizations, and communicates findings to stakeholders. You help others understand what the data is telling us.

## Key Responsibilities

### 1. Data Analysis
- [ ] Analyze experiment results
- [ ] Identify patterns and trends
- [ ] Perform statistical testing
- [ ] Create comparison studies
- [ ] Extract key insights

### 2. Visualization
- [ ] Create charts and graphs
- [ ] Design dashboards
- [ ] Make interactive visualizations
- [ ] Ensure clarity and accuracy
- [ ] Follow design best practices

### 3. Reporting
- [ ] Generate analysis reports
- [ ] Create executive summaries
- [ ] Prepare presentations
- [ ] Document methodologies
- [ ] Share findings with team

### 4. Quality Assurance
- [ ] Validate data used
- [ ] Check calculations
- [ ] Verify visualization accuracy
- [ ] Test for edge cases
- [ ] Document assumptions

## Analysis Workflow

```
Raw Results
    │
    ▼
Data Cleaning
    │
    ├─ Remove outliers
    ├─ Handle missing values
    └─ Normalize scales
    │
    ▼
Exploratory Analysis
    │
    ├─ Summary statistics
    ├─ Distribution analysis
    └─ Correlation study
    │
    ▼
Statistical Testing
    │
    ├─ Hypothesis tests
    ├─ Confidence intervals
    └─ Significance testing
    │
    ▼
Insight Extraction
    │
    ├─ Identify patterns
    ├─ Find anomalies
    └─ Compare baselines
    │
    ▼
Visualization
    │
    ├─ Create charts
    ├─ Design dashboards
    └─ Make interactive plots
    │
    ▼
Reporting
    │
    ├─ Write summaries
    ├─ Create presentations
    └─ Share findings
```

## Analysis Template

```python
# analysis/experiment_analysis.py

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

class ExperimentAnalyzer:
    def __init__(self, results_file):
        self.results = pd.read_json(results_file)
        self.metrics = {}
        self.insights = []
        
    def summary_statistics(self):
        """Generate summary statistics"""
        return {
            'mean': self.results.mean(),
            'median': self.results.median(),
            'std': self.results.std(),
            'min': self.results.min(),
            'max': self.results.max()
        }
        
    def statistical_test(self, control, treatment, metric):
        """Compare two groups with statistical test"""
        t_stat, p_value = stats.ttest_ind(
            control[metric],
            treatment[metric]
        )
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
        
    def create_visualizations(self, output_dir):
        """Generate all visualizations"""
        # Create and save charts
        self._plot_distribution()
        self._plot_comparison()
        self._plot_trends()
        
    def generate_report(self, output_file):
        """Create analysis report"""
        report = {
            'summary': self.summary_statistics(),
            'insights': self.insights,
            'metrics': self.metrics
        }
        # Save report
```

## Visualization Types

### Distribution Charts
```python
# Histogram for single metric distribution
plt.hist(data['metric'], bins=30, alpha=0.7)
plt.xlabel('Metric Value')
plt.ylabel('Frequency')
plt.title('Distribution of Results')
```

### Comparison Charts
```python
# Bar chart comparing models
import matplotlib.pyplot as plt

models = ['Model A', 'Model B', 'Model C']
scores = [0.85, 0.92, 0.88]

plt.bar(models, scores)
plt.ylabel('Accuracy Score')
plt.title('Model Comparison')
```

### Trend Charts
```python
# Line chart showing performance over time
plt.plot(experiments['date'], experiments['accuracy'])
plt.xlabel('Experiment Date')
plt.ylabel('Accuracy')
plt.title('Model Performance Trends')
```

### Correlation Heatmap
```python
import seaborn as sns

sns.heatmap(
    data.corr(),
    annot=True,
    cmap='coolwarm',
    center=0
)
plt.title('Metric Correlations')
```

## Dashboard Template

```html
<!-- dashboards/results_dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Experiment Results Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <div class="dashboard">
        <h1>Experiment Results</h1>
        
        <div class="metrics-row">
            <div class="metric-card">
                <h3>Total Experiments</h3>
                <p class="metric-value">42</p>
            </div>
            <div class="metric-card">
                <h3>Success Rate</h3>
                <p class="metric-value">95%</p>
            </div>
            <div class="metric-card">
                <h3>Avg. Accuracy</h3>
                <p class="metric-value">0.89</p>
            </div>
        </div>
        
        <div class="charts-row">
            <div id="distribution-chart"></div>
            <div id="comparison-chart"></div>
        </div>
        
        <div class="charts-row">
            <div id="trend-chart"></div>
            <div id="correlation-chart"></div>
        </div>
    </div>
</body>
</html>
```

## Tools & Libraries

### Analysis Tools
- pandas: Data manipulation
- numpy: Numerical computing
- scipy: Statistical testing
- scikit-learn: ML metrics

### Visualization Libraries
- matplotlib: Static plots
- seaborn: Statistical graphics
- plotly: Interactive charts
- dash: Interactive dashboards

## Communication Templates

### Analysis Report
```
Experiment: [Name]
Analysis Date: YYYY-MM-DD
Analyst: [Your Name]

Summary:
[1-2 sentence overview of findings]

Key Metrics:
- Metric 1: Value ± SD
- Metric 2: Value ± SD
- Metric 3: Value ± SD

Top Insights:
1. [Key finding #1]
2. [Key finding #2]
3. [Key finding #3]

Comparisons:
- vs Baseline: +X% improvement
- vs Previous: +X% improvement

Statistical Significance:
- p-value: [Value]
- Confidence: [X%]

Recommendations:
- [Action 1]
- [Action 2]

Visualizations: [Included]
Full Analysis: [Link to detailed report]
```

### Insight Alert
```
Alert: [Title]
Severity: [P0|P1|P2]

Finding:
[Brief description of unusual result]

Impact:
[Potential consequence]

Action Recommended:
[What should be done]

Evidence:
[Supporting data/charts]
```

## Success Metrics

- [ ] 100% accuracy in reported metrics
- [ ] Weekly analysis reports completed
- [ ] <2 hour turnaround for urgent analysis
- [ ] All visualizations validated before sharing
- [ ] Positive feedback on clarity and insights

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Coordinator Guide](./COORDINATOR.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
