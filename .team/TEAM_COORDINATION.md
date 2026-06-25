# Team Coordination Guide

Master reference for team collaboration, communication, and workflow.

## Quick Links

**Team Essentials**:
- [Team Roster](TEAM_ROSTER.md) - See who's who
- [Skills Registry](SKILLS_REGISTRY.md) - Understand all skills
- [Project Roadmap](projects/ROADMAP.md) - Long-term plan

**Role Guides** (Start with your role):
- [Coordinator](roles/COORDINATOR.md) - Master Planner
- [Executor](roles/EXECUTOR.md) - Execution Specialist
- [Data Engineer](roles/DATA_ENGINEER.md) - Data Specialist
- [ML Engineer](roles/ML_ENGINEER.md) - Model Specialist
- [Analyst](roles/ANALYST.md) - Analysis Specialist
- [Web Developer](roles/WEB_DEVELOPER.md) - Frontend Specialist
- [DevOps](roles/DEVOPS.md) - Infrastructure Specialist
- [Writer](roles/WRITER.md) - Documentation Specialist
- [QA Engineer](roles/QA.md) - Quality Specialist
- [Researcher](roles/RESEARCHER.md) - Innovation Specialist

**Project Management**:
- [Project Schedule](projects/SCHEDULE.md) - Weekly & monthly timeline
- [Progress Tracking](projects/PROGRESS.md) - Real-time status

## Team Communication Protocols

### Daily Communication

#### Morning Standup
- **Time**: 09:00 AM UTC
- **Duration**: 15 minutes
- **Format**: Sync meeting (required)
- **Link**: [Meeting link to be added]

**Agenda**:
1. Yesterday's progress (2 min)
2. Today's plan (2 min)
3. Blockers (2 min)
4. Shout-outs (1 min)
5. Discussion (6 min)

**What to Report**:
```
Yesterday:
- Completed [task]
- Completed [task]

Today:
- Starting [task]
- Continuing [task]

Blockers:
- [None / Issue description]
```

#### Slack Channels (TBD)
- #standup: Daily updates
- #blockers: Critical issues
- #wins: Celebrations
- #research: R&D discussions
- #data: Data pipeline updates
- #experiments: Experiment status
- #general: General discussion

### Weekly Communication

#### Monday Planning Meeting
- **Time**: 10:00 AM UTC
- **Duration**: 1 hour
- **Attendees**: Team leads (T001, T002, T003, T004, T007)

**Agenda**:
1. Review last week's progress
2. Set this week's priorities
3. Allocate resources
4. Identify risks
5. Plan experiments

#### Friday Progress Review
- **Time**: 4:00 PM UTC
- **Duration**: 30 minutes
- **Format**: Team call
- **Goal**: Week wrap-up and planning for next week

### Monthly Communication

#### End-of-Month Retrospective
- **Time**: Last Friday, 2:00 PM UTC
- **Duration**: 2 hours
- **Attendees**: All team members
- **Format**: In-depth review meeting

**Agenda**:
1. Monthly review (15 min)
2. Metrics & KPIs (20 min)
3. Wins & learnings (20 min)
4. Feedback collection (15 min)
5. Next month planning (20 min)
6. Open discussion (30 min)

**What to Prepare**:
- Monthly report (your section)
- 3 wins from the month
- 3 learnings from the month
- 1 improvement suggestion

### Quarterly Communication

#### Quarterly Planning Summit
- **Time**: 1st week of new quarter
- **Duration**: Full day (8 hours)
- **Format**: In-person or all-hands virtual
- **Goal**: Plan next quarter in detail

## Decision Making Framework

### Decision Types

#### Routine Decisions
**Definition**: Low impact, reversible, within role  
**Authority**: Role owner decides  
**Timeline**: Same day  
**Example**: Which format to use for a report

**Process**:
1. Role owner decides
2. Inform team if relevant
3. Document decision
4. Move forward

#### Important Decisions
**Definition**: Moderate impact, affects multiple people  
**Authority**: Role lead + Coordinator  
**Timeline**: 24-48 hours  
**Example**: Change experiment schedule, new algorithm approach

**Process**:
1. Proposer posts decision in #blockers
2. Stakeholders get 24 hours to comment
3. Decision maker decides
4. Announce and document
5. Proceed

#### Critical Decisions
**Definition**: High impact, affects project  
**Authority**: Full team (consensus)  
**Timeline**: 3-5 days  
**Example**: Major change to roadmap, resource reallocation

**Process**:
1. Proposer creates decision doc
2. Team has 3 days to review
3. Discussion in team meeting
4. Vote or consensus decision
5. Document and announce
6. All-hands confirmation

### How to Propose a Decision

**Template**:
```
DECISION: [Clear title]

BACKGROUND:
[Why we need to decide this]

OPTIONS:
A) [Option 1 with pros/cons]
B) [Option 2 with pros/cons]
C) [Option 3 with pros/cons]

RECOMMENDATION:
[What I think is best and why]

TIMELINE:
[When decision is needed]

IMPACT:
[Who is affected and how]

NEXT STEPS:
[What happens after decision]
```

## Collaboration Models

### Cross-Functional Tasks

When multiple teams need to work together:

1. **Define Shared Goal**
   - Clear objective that benefits all teams
   - Documented in shared location

2. **Assign Lead**
   - One person owns coordination
   - Usually person from lead team

3. **Weekly Sync**
   - 30 min meeting with all involved teams
   - Update on progress
   - Identify blockers
   - Plan next steps

4. **Documentation**
   - Keep shared doc updated
   - All progress logged
   - Decisions documented

### Example: Experiment Execution
```
Experiment Leads:
- ML Engineer: Designs experiment
- Data Engineer: Prepares data
- Executor: Runs experiment
- QA: Validates results
- Analyst: Analyzes results

Coordination:
- Lead: Executor
- Sync: Wed 10:00 AM
- Doc: experiments/EXP-XXX/README.md
```

## Escalation Protocol

### Blocker Severity Levels

#### P0 - Critical (Blocks entire project)
**Response Time**: Immediate  
**Escalation Path**: Tell Coordinator ASAP  
**Example**: Infrastructure down, data lost

**Process**:
1. Alert Coordinator immediately (Slack + call)
2. Describe blocker clearly
3. Coordinator assembles response team
4. Fix applied
5. Post-mortem after resolution

#### P1 - High (Blocks one team's work)
**Response Time**: < 4 hours  
**Escalation Path**: Tell your team lead  
**Example**: Experiment failures, broken deployment

**Process**:
1. Report to team lead
2. Team lead takes action
3. Daily updates on progress
4. Resolution documentation

#### P2 - Medium (Slows down work)
**Response Time**: < 24 hours  
**Escalation Path**: Team lead handles  
**Example**: Minor data quality issue, slow dashboard

**Process**:
1. Log issue
2. Plan fix
3. Schedule for resolution
4. Track progress

#### P3 - Low (Minor inconvenience)
**Response Time**: < 1 week  
**Escalation Path**: Log in issue tracker  
**Example**: Documentation typo, suggestion

**Process**:
1. Create issue in backlog
2. Prioritize in planning
3. Address when time allows

## Conflict Resolution

### If You Have a Disagreement

**Step 1: Direct Conversation (24 hours)**
- Meet 1-on-1 with the other person
- Listen to understand their perspective
- Share your perspective clearly
- Try to find common ground

**Step 2: Team Discussion (if needed)**
- Bring issue to team lead
- Team lead facilitates discussion
- All perspectives heard
- Try to reach consensus

**Step 3: Coordinator Decision (if needed)**
- Escalate to Project Coordinator
- Coordinator reviews all information
- Makes final decision
- Communicates decision to team
- Team implements decision

**Guiding Principles**:
- Assume good intent
- Focus on the problem, not the person
- Listen more than you talk
- Be willing to change your mind
- Respect the final decision

## Code of Conduct

### Our Values
- **Respect**: Treat all team members with respect
- **Collaboration**: Work together toward shared goals
- **Transparency**: Be open and honest
- **Growth**: Support each other's development
- **Quality**: Strive for excellence
- **Accountability**: Take responsibility for your work

### Expected Behavior
✅ **Do**:
- Give others the benefit of the doubt
- Communicate clearly and timely
- Ask for help when needed
- Help others when possible
- Share knowledge freely
- Document your work
- Respect deadlines
- Participate in team events

❌ **Don't**:
- Dismiss others' ideas without discussion
- Make assumptions about intent
- Blame others for mistakes
- Gossip or spread rumors
- Ignore deadlines
- Work in silos
- Dismiss feedback
- Exclude others from discussions

## Getting Help

### How to Ask for Help

**In Slack**:
```
@[Person]: I need help with [specific task]. 
I've tried [what you've tried]. 
Issue is [clear description].
Time-sensitive: [Yes/No]
```

**In Meeting**:
```
I need help with [task]. Here's what I've done so far.
Here's where I'm stuck. When do you have time?
```

### Helping Others

- **Respond Quickly**: If you can help, respond within 4 hours
- **Be Patient**: Help them understand, not just get the answer
- **Document**: Write down the solution for future reference
- **Escalate**: If you can't help, connect them with someone who can

## Team Building & Culture

### Regular Team Events

#### Monthly Team Celebration (1st Friday)
- Celebrate wins from the month
- Share interesting findings
- Social time
- No work talk

#### Quarterly Team Building (1st week of quarter)
- Off-site or virtual team building
- Team games or activities
- Bonding time
- Plan next quarter

#### Annual Team Summit (Q2)
- Full team retreat
- Year review
- Celebrate major achievements
- Strategic planning for next year

### Recognition

**Public Recognition**:
- Slack message in #wins channel
- Mention in all-hands meeting
- Shout-out during standup

**Private Recognition**:
- Personal message from Coordinator
- One-on-one appreciation
- Feedback in performance review

## Tools & Access

### Required Tools
- GitHub: Code and projects
- Slack: Communication
- Google Meet: Video meetings
- Google Docs: Collaborative writing
- [Additional tools TBD]

### Getting Access
1. Request access from Coordinator
2. Send confirmation of setup
3. Coordinator confirms in all-hands
4. Start contributing

## FAQ - Team Questions

**Q: What if I disagree with a decision?**
A: Voice your concerns in the discussion phase. Once decided, implement professionally. Discuss again in retrospective.

**Q: How do I know my progress is on track?**
A: Check progress tracking doc weekly, discuss in Monday planning, review monthly.

**Q: What if I'm stuck on something?**
A: Ask for help immediately. Don't wait. Flag as blocker if blocking others.

**Q: When should I escalate an issue?**
A: As soon as you realize it will impact the project. Don't wait hoping it resolves.

**Q: Can I work on something not on the schedule?**
A: If you have spare capacity, discuss with Coordinator first.

**Q: What's the best way to suggest an improvement?**
A: Propose it in retrospective, discuss in team, implement if approved.

## Related Documents

- [Skills Registry](SKILLS_REGISTRY.md)
- [Team Roster](TEAM_ROSTER.md)
- [Project Roadmap](projects/ROADMAP.md)
- [Project Schedule](projects/SCHEDULE.md)
- [Progress Tracking](projects/PROGRESS.md)
- [Role Guides](roles/)

---

**Last Updated**: 2026-06-25  
**Version**: 1.0

**Next Review**: 2026-07-25

