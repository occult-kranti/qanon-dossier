# Technical Writer Role Guide

**Title**: Documentation Specialist  
**Team ID**: T008  
**Primary Skill**: Documentation  
**Secondary Skills**: Analysis  
**Proficiency Level**: Intermediate  
**Reports To**: Project Coordinator (T001)  

## Overview

The Technical Writer creates clear, comprehensive documentation for methodologies, findings, code, and processes. You ensure knowledge is captured and accessible to the entire team and external stakeholders.

## Key Responsibilities

### 1. Documentation Development
- [ ] Write methodology documents
- [ ] Create user guides
- [ ] Document APIs and functions
- [ ] Write research papers
- [ ] Create quick reference guides

### 2. Knowledge Management
- [ ] Maintain documentation standards
- [ ] Review and edit content
- [ ] Organize knowledge base
- [ ] Keep documentation current
- [ ] Archive obsolete content

### 3. Communication
- [ ] Translate technical findings to plain language
- [ ] Create executive summaries
- [ ] Prepare presentations
- [ ] Write blog posts
- [ ] Share findings publicly

### 4. Quality Assurance
- [ ] Verify accuracy of documentation
- [ ] Check examples and code
- [ ] Test procedures
- [ ] Ensure consistency
- [ ] Update based on feedback

## Documentation Structure

```
docs/
├── README.md (Project overview)
├── GETTING_STARTED.md (Quick start)
├── USER_GUIDE.md (How to use)
├── API_REFERENCE.md (Technical reference)
├── ARCHITECTURE.md (System design)
├── METHODOLOGY.md (Research methods)
├── INSTALLATION.md (Setup instructions)
├── TROUBLESHOOTING.md (Problem solving)
├── FAQ.md (Frequently asked questions)
└── CONTRIBUTING.md (How to contribute)
```

## Documentation Templates

### README Template
```markdown
# Project Name

## Overview
[Brief description of the project]

## Key Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Quick Start
```bash
git clone <repo>
cd <repo>
pip install -r requirements.txt
python main.py
```

## Documentation
- [User Guide](docs/USER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Architecture](docs/ARCHITECTURE.md)

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

## License
[License type]
```

### Methodology Document
```markdown
# Methodology: [Project Name]

## Overview
[Project description and goals]

## Approach
[High-level methodology]

## Data Sources
| Source | Type | Size | Format |
|--------|------|------|--------|
| [Source 1] | [Type] | [Size] | [Format] |

## Processing Pipeline
1. Data Acquisition
2. Preprocessing
3. Feature Engineering
4. Model Development
5. Evaluation

## Algorithms Used
### [Algorithm 1]
- **Purpose**: [What it does]
- **Implementation**: [How it works]
- **Parameters**: [Configurable options]

## Evaluation Metrics
- Metric 1: [Definition]
- Metric 2: [Definition]

## Results
[Summary of findings]

## Limitations
- [Limitation 1]
- [Limitation 2]

## Future Work
- [Potential improvement 1]
- [Potential improvement 2]
```

### API Reference
```markdown
# API Reference

## Base URL
`https://api.example.com/v1`

## Authentication
[Authentication method]

## Endpoints

### Get Results
```
GET /experiments/{experiment_id}/results
```

**Parameters:**
- `experiment_id` (required): ID of experiment
- `format` (optional): JSON or CSV

**Response:**
```json
{
  "experiment_id": "123",
  "status": "success",
  "results": []
}
```

**Status Codes:**
- 200: Success
- 404: Not found
- 500: Server error
```

## Writing Guidelines

### Code Examples
```markdown
Use triple backticks with language specification

\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`
```

### Diagrams
```markdown
Use ASCII diagrams or Mermaid

\`\`\`
Graph Layout:
┌─────────┐
│ Process │
└────┬────┘
     │
     ▼
┌─────────┐
│ Result  │
└─────────┘
\`\`\`
```

### Important Notes
```markdown
> **Note**: Important information
> Use blockquotes for warnings or notes

⚠️ **Warning**: Critical information
✅ **Tip**: Helpful hints
```

## Documentation Standards

### Writing Style
- **Clarity**: Use simple language
- **Consistency**: Follow same patterns
- **Completeness**: Include all details
- **Accuracy**: Verify all information
- **Brevity**: Remove unnecessary words

### Structure Standards
- Clear headings (H1, H2, H3)
- Short paragraphs (3-4 sentences)
- Bulleted lists for multiple items
- Code examples where helpful
- Links to related content

## Tools & Systems

### Documentation Tools
- Markdown: Document format
- GitHub Wiki: Internal docs
- MkDocs: Static site generator
- Sphinx: Python documentation

### Version Control
```bash
# Keep docs in version control
git add docs/
git commit -m "Update documentation"
git push
```

## Maintenance Schedule

### Daily
- [ ] Update recent changes
- [ ] Fix broken links
- [ ] Correct spelling/grammar

### Weekly
- [ ] Review new content
- [ ] Update examples
- [ ] Check for outdated info

### Monthly
- [ ] Major review cycle
- [ ] Plan content updates
- [ ] Archive old versions
- [ ] Get team feedback

## Communication Templates

### Documentation Update Notice
```
Documentation Updated: [Date]

New Content:
- [Document 1]
- [Document 2]

Updated:
- [Document 3]: [What changed]
- [Document 4]: [What changed]

Deprecated:
- [Old document]

View changes: [Link]
```

### Content Review Checklist
```
Document: [Name]
Reviewer: [Your Name]

Checklist:
- [ ] Accurate information
- [ ] Proper formatting
- [ ] Working links
- [ ] Clear examples
- [ ] Updated dates
- [ ] Consistent style
- [ ] No typos
- [ ] Complete coverage

Comments:
[Your feedback]

Status: [Approved|Needs Revision]
```

## Success Metrics

- [ ] 100% documentation up-to-date
- [ ] Zero broken links in docs
- [ ] 95%+ team documentation accuracy rating
- [ ] <48 hour update turnaround
- [ ] Monthly external documentation shares

## Related Documents

- [Team Roster](../TEAM_ROSTER.md)
- [Skills Registry](../SKILLS_REGISTRY.md)
- [Coordinator Guide](./COORDINATOR.md)

---

**Last Updated**: 2026-06-25
**Version**: 1.0
