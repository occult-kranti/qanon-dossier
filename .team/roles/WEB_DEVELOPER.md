# Web Developer Role Guide

**Title**: Frontend Specialist  
**Team ID**: T006  
**Primary Skill**: Web Development  
**Secondary Skills**: DevOps & Infrastructure  
**Proficiency Level**: Intermediate  
**Reports To**: Project Coordinator (T001)  

## Overview

The Web Developer builds and maintains interactive dashboards, visualizations, and web applications hosted on GitHub Pages. You make data come alive for end users.

## Key Responsibilities

### 1. Frontend Development
- [ ] Build responsive web interfaces
- [ ] Integrate data visualizations
- [ ] Create interactive dashboards
- [ ] Implement user interactions
- [ ] Optimize performance

### 2. Dashboard Design
- [ ] Design information architecture
- [ ] Create wireframes
- [ ] Implement layouts
- [ ] Ensure accessibility
- [ ] Test usability

### 3. Data Integration
- [ ] Connect to data sources
- [ ] Implement data pipelines
- [ ] Real-time data updates
- [ ] Handle errors gracefully
- [ ] Cache for performance

### 4. Deployment
- [ ] Deploy to GitHub Pages
- [ ] Manage versioning
- [ ] Handle rollbacks
- [ ] Monitor uptime
- [ ] Optimize assets

## Dashboard Architecture

```
GitHub Pages
    │
    ├─ index.html (Home)
    ├─ experiments.html (Results Dashboard)
    ├─ analytics.html (Analysis Dashboard)
    ├─ research.html (Research Hub)
    └─ timeline.html (Timeline View)
    │
    ├─ assets/
    │   ├─ app.js (Main app logic)
    │   ├─ components.js (Reusable components)
    │   ├─ charts.js (Chart generation)
    │   ├─ api.js (Data fetching)
    │   └─ style.css (Styling)
    │
    └─ data/
        ├─ experiments.json
        ├─ metrics.json
        └─ results.json
```

## Frontend Components

### Dashboard Component Template
```html
<!-- components/dashboard.html -->
<div class="dashboard">
    <header>
        <h1>Results Dashboard</h1>
        <nav>
            <a href="#metrics">Metrics</a>
            <a href="#charts">Charts</a>
            <a href="#details">Details</a>
        </nav>
    </header>
    
    <main>
        <section id="metrics" class="metrics-section">
            <div class="metric-card">
                <h3>Total Experiments</h3>
                <p class="value" id="total-experiments">--</p>
            </div>
        </section>
        
        <section id="charts" class="charts-section">
            <div id="distribution-chart"></div>
            <div id="comparison-chart"></div>
        </section>
    </main>
</div>
```

### JavaScript Logic
```javascript
// assets/app.js

class Dashboard {
    constructor() {
        this.data = null;
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.renderMetrics();
        this.renderCharts();
    }
    
    async loadData() {
        const response = await fetch('data/experiments.json');
        this.data = await response.json();
    }
    
    renderMetrics() {
        document.getElementById('total-experiments').textContent 
            = this.data.experiments.length;
    }
    
    renderCharts() {
        // Use D3.js or Plotly for visualizations
        this.createDistributionChart();
        this.createComparisonChart();
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    new Dashboard();
});
```

## Chart Integration

### Using D3.js
```javascript
// Create a simple bar chart
const data = [
    {model: 'Model A', accuracy: 0.85},
    {model: 'Model B', accuracy: 0.92},
    {model: 'Model C', accuracy: 0.88}
];

const width = 800, height = 400;
const svg = d3.select('#chart')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('x', (d, i) => i * 200)
    .attr('y', d => height - d.accuracy * 400)
    .attr('width', 150)
    .attr('height', d => d.accuracy * 400);
```

### Using Plotly
```javascript
// Create an interactive plot
const trace = {
    x: ['Model A', 'Model B', 'Model C'],
    y: [0.85, 0.92, 0.88],
    type: 'bar'
};

const layout = {
    title: 'Model Comparison',
    xaxis: {title: 'Model'},
    yaxis: {title: 'Accuracy'}
};

Plotly.newPlot('chart', [trace], layout);
```

## Styling Guide

### CSS Architecture
```css
/* assets/style.css */

/* Variables */
:root {
    --primary-color: #2c3e50;
    --accent-color: #3498db;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
}

/* Layout */
.dashboard {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}

.metrics-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Responsive */
@media (max-width: 768px) {
    .dashboard {
        grid-template-columns: 1fr;
    }
}
```

## Performance Optimization

### Asset Optimization
```javascript
// Lazy load visualizations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            loadChart(entry.target);
            observer.unobserve(entry.target);
        }
    });
});

document.querySelectorAll('.chart').forEach(chart => {
    observer.observe(chart);
});
```

### Data Caching
```javascript
class DataCache {
    constructor(ttl = 5 * 60 * 1000) {
        this.cache = new Map();
        this.ttl = ttl;
    }
    
    async get(key, fetchFn) {
        if (this.cache.has(key)) {
            const cached = this.cache.get(key);
            if (Date.now() - cached.time < this.ttl) {
                return cached.data;
            }
        }
        
        const data = await fetchFn();
        this.cache.set(key, {data, time: Date.now()});
        return data;
    }
}
```

## Deployment Process

### GitHub Pages Deployment
```bash
# Build static site
npm run build

# Deploy to gh-pages branch
git add .
git commit -m "Update dashboard"
git push origin main

# GitHub Actions will auto-deploy to GitHub Pages
```

### Pre-Deployment Checklist
- [ ] All links tested
- [ ] Responsive design verified
- [ ] Performance metrics check
- [ ] Accessibility audit passed
- [ ] Cross-browser testing done
- [ ] Analytics configured
- [ ] 404 page configured

## Tools & Stack

### Core Technologies
- HTML5: Markup
- CSS3: Styling
- JavaScript ES6+: Interactivity
- Git: Version control

### Libraries
- D3.js: Data visualization
- Plotly: Interactive charts
- Bootstrap: Responsive design
- Axios: HTTP requests

## Communication Templates

### Deployment Notification
```
Dashboard Update: [Version]
Deployed: [Date & Time]

Changes:
- [Feature 1]
- [Feature 2]
- [Bug fix 1]

Performance:
- Page Load: Xms
- Interactions: Responsive
- Mobile: Optimized

Issues:
- [Known issue, if any]

Rollback Plan:
[Link to previous version]
```

### Performance Report
```
Dashboard: [Name]
Reporting Period: [Date Range]

Metrics:
- Avg Page Load: Xms
- User Sessions: X
- Bounce Rate: X%
- Avg Time on Page: X min

Top Pages:
1. [Page Name]: X visits
2. [Page Name]: X visits

Performance Issues:
- [Issue 1]
- [Issue 2]

Optimizations Applied:
- [Optimization 1]
- [Optimization 2]
```

## Success Metrics

- [ ] <3s page load time
- [ ] 95%+ mobile responsiveness
- [ ] 0 broken links or assets
- [ ] 95%+ accessibility score
- [ ] Monthly releases without issues

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Coordinator Guide](./COORDINATOR.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
