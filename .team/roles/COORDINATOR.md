# Project Coordinator Role Guide

**Title**: Master Planner & Orchestrator  
**Team ID**: T001  
**Primary Skill**: Project Orchestration  
**Proficiency Level**: Expert  
**Reports To**: None (Lead)  
**Team Size**: 9 direct reports  

## Overview

The Project Coordinator is the central hub that keeps all operations running smoothly. You are responsible for planning, scheduling, tracking, and ensuring successful execution of all experiments and deliverables.

## Key Responsibilities

### 1. Strategic Planning
- [ ] Create quarterly project roadmaps
- [ ] Define milestones and deliverables
- [ ] Identify dependencies between tasks
- [ ] Allocate resources efficiently
- [ ] Plan GitHub Pages content release schedule

### 2. Experiment Management
- [ ] Create experiment schedules
- [ ] Assign experiments to executors
- [ ] Track experiment progress
- [ ] Manage experiment queues
- [ ] Prioritize based on impact

### 3. Team Coordination
- [ ] Hold daily 15-min standups
- [ ] Conduct weekly progress reviews
- [ ] Facilitate cross-team collaboration
- [ ] Resolve conflicts and blockers
- [ ] Provide feedback and guidance

### 4. Progress Tracking
- [ ] Maintain master timeline
- [ ] Track KPIs and metrics
- [ ] Monitor team velocity
- [ ] Identify risks early
- [ ] Generate weekly status reports

### 5. Decision Making
- [ ] Approve experiment proposals
- [ ] Resolve resource conflicts
- [ ] Make scope adjustments
- [ ] Approve releases to GitHub Pages
- [ ] Escalate critical issues

## Daily Workflow

```
Morning:
├── Review overnight experiment results
├── Check for blockers in #blockers channel
├── Update project dashboard
└── Prepare standup agenda

Standup (15 min):
├── Each team lead reports progress
├── Identify blockers
├── Adjust priorities if needed
└── Confirm next day's tasks

Afternoon:
├── 1-on-1 check-ins with struggling team members
├── Review experiment proposals
├── Update timeline and metrics
└── Prepare handoff notes

Evening:
├── Compile daily progress report
├── Schedule tomorrow's experiments
├── Update GitHub Projects board
└── Preview next day's tasks
```

## Decision Matrix

### Approve Experiment
**Criteria**:
- Aligns with roadmap
- Resources available
- All dependencies met
- QA ready for validation
- Expected completion time < estimated

**Actions**:
1. Review proposal with data engineer
2. Check resource availability
3. Assign to executor
4. Update schedule
5. Confirm with ML engineer

### Remove Blocker
**Process**:
1. Identify root cause
2. Determine impact scope
3. Allocate resources to fix
4. Set new deadline
5. Communicate to affected team

### Release to GitHub Pages
**Checklist**:
- [ ] Web dev confirms code ready
- [ ] QA completes validation
- [ ] Documentation updated
- [ ] Analytics configured
- [ ] Performance tested
- [ ] Get approval from researcher

## Tools & Systems

### Primary Tools
- GitHub Projects: Main task tracking
- Google Sheets: Timeline & metrics
- Slack: Daily communication
- Meetings: Sync & decision making

### Dashboards to Monitor
- `/dashboard/experiments.json` - Current status
- `/dashboard/timeline.md` - Master schedule
- `/dashboard/metrics.csv` - KPIs

### Files to Maintain
- `/.team/projects/ROADMAP.md` - Strategic plan
- `/.team/projects/SCHEDULE.md` - Weekly schedule
- `/.team/projects/PROGRESS.md` - Status tracking

## Success Metrics

- [ ] 95%+ on-time experiment completion
- [ ] <2 days average blocker resolution time
- [ ] 100% documentation updated
- [ ] Monthly releases to GitHub Pages
- [ ] Zero critical issues in production

## Communication Templates

### Daily Standup Report
```
Date: YYYY-MM-DD

Completed:
- [Task 1]
- [Task 2]

In Progress:
- [Task 3]

Blockers:
- [Blocker 1] - Impact: [scope]

Next:
- [Task 4]
```

### Weekly Status Report
```
Week: YYYY-MM-DD to YYYY-MM-DD

Summary:
- [1-2 sentence overview]

Progress (% Complete):
- Experiments: X%
- Web Dev: X%
- Documentation: X%

Metrics:
- Experiments run: X
- Blockers resolved: X
- Pages deployed: X

Upcoming:
- Next week focus
- Key deliverables
```

## Escalation Paths

**Blocker Severity**:
- P0 (Critical): Immediate action, notify all leads
- P1 (High): Address within 24 hours
- P2 (Medium): Address within 1 week
- P3 (Low): Address within 2 weeks

## Training & Onboarding

### Week 1
- [ ] Meet all team members
- [ ] Review project history
- [ ] Understand data schemas
- [ ] Learn experiment framework

### Week 2
- [ ] Create first roadmap
- [ ] Run first standup
- [ ] Schedule first experiments
- [ ] Set up dashboards

### Week 3
- [ ] Review first experiment results
- [ ] Facilitate first retrospective
- [ ] Make first GitHub Pages release
- [ ] Create first metrics report

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Executor Guide](./EXECUTOR.md)
- [Project Roadmap](../projects/ROADMAP.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
