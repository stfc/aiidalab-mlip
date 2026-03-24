# AiiDAlab-MLIP GitHub Milestones and Issue Plan

This plan converts the product roadmap into GitHub milestones, labels, and issue templates.

## Milestones

### M1 - Runtime Stabilization and MVP Inference
Target: 2 weeks

Scope:
- Resolve runtime compatibility matrix (AiiDAlab image, Python, aiida-mlip, AiiDA core)
- Complete Single Point end-to-end workflow submission and retrieval
- Add environment diagnostics (profile, code, dependencies)
- Basic error handling and validation

Exit criteria:
- Single Point runs successfully from UI to results for reference structures
- CI passes on supported matrix
- Setup and troubleshooting docs updated

### M2 - Geometry Optimization and Results UX
Target: 2 weeks

Scope:
- Complete Geometry Optimization workflow submission and restart behavior
- Add robust results page (energy, forces, convergence details)
- Improve process/job status tracking and retry/cancel UX

Exit criteria:
- Geometry Optimization workflow stable for reference datasets
- Results view supports successful and failed workflow states
- Integration tests cover upload -> run -> results

### M3 - Reliability, CI/CD, and Beta Release
Target: 2 weeks

Scope:
- Add full test pyramid (unit, integration, e2e smoke)
- Add release checklist and changelog discipline
- Add staging deployment workflow
- Security and dependency scanning in CI

Exit criteria:
- Beta tag released with complete release notes
- Staging deployment verified by smoke tests
- Vulnerability and license checks integrated

### M4 - Production Deployment and Operations
Target: 1-2 weeks

Scope:
- Production deployment documentation and scripts
- Monitoring and operational playbooks
- User support and issue triage process

Exit criteria:
- Production deployment completed and validated
- Operational dashboard and alert thresholds defined
- Post-release incident and rollback runbook available

### M5 - Advanced Features (Post-GA)
Target: rolling

Scope:
- Molecular Dynamics workflow completion
- Custom model upload and compatibility checks
- Batch structure submissions and advanced analysis exports

Exit criteria:
- Feature complete according to acceptance criteria in linked issues

## Labels

Create these labels to keep triage and planning clean:

Type labels:
- type: feature
- type: bug
- type: docs
- type: test
- type: chore
- type: release
- type: deployment

Area labels:
- area: ui
- area: workflow
- area: aiida
- area: aiida-mlip-integration
- area: results
- area: docs
- area: ci
- area: infra

Priority labels:
- priority: critical
- priority: high
- priority: medium
- priority: low

Status labels:
- status: blocked
- status: needs-info
- status: ready
- status: in-progress
- status: review

## Starter Issue Backlog

Create these as initial issues and assign to milestones.

### M1
- Define and publish compatibility matrix for runtime stack
- Implement environment doctor checks in app startup flow
- Complete Single Point submission via aiida-mlip builder
- Add pre-submit input validation for structure and model compatibility
- Add user-friendly error mapping for common runtime failures
- Add integration test for Single Point happy path

### M2
- Complete Geometry Optimization workflow and parameter mapping
- Add process status polling and refresh strategy
- Build unified results widget for energy and force summaries
- Add restart-from-failure handling for optimization workflows
- Add end-to-end test for Geometry Optimization

### M3
- Add release checklist and release candidate workflow
- Add dependency vulnerability scan in CI
- Add license compliance check in CI
- Add staging deployment guide and smoke tests
- Add changelog process and version tagging policy

### M4
- Create production deployment runbook
- Add monitoring metrics and failure alerts documentation
- Define rollback strategy and verify in staging
- Create issue triage and support SLA process

### M5
- Implement Molecular Dynamics workflow end-to-end
- Add custom model upload and validation
- Add batch submission for multiple structures
- Add export support for trajectories and summaries

## Issue Workflow

1. Triage new issues within 48 hours.
2. Add labels: one type, one area, one priority, one status.
3. Assign a milestone before implementation starts.
4. Link PRs to issues using Closes #<id>.
5. Require acceptance criteria completion before closing.

## Pull Request Standards

Each PR should include:
- Linked issue
- Problem statement
- Scope of change
- Test evidence
- Screenshots for UI changes
- Risk notes and rollback notes for workflow changes

## Suggested GitHub Project Views

Backlog view:
- Group by milestone
- Sort by priority then updated date

Active Sprint view:
- Filter status: in-progress or review
- Group by area

Release Readiness view:
- Filter milestone M3 or current release
- Show only type: release, deployment, bug

## Release Gate Checklist

Before GA release:
- All critical and high priority bugs closed or explicitly deferred
- CI green on supported runtime matrix
- User and installation docs updated
- Smoke test completed in staging
- Rollback playbook verified
