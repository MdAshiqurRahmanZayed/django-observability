# Contributing to Django Observability Stack

Thank you for your interest in contributing! This guide will help you get started.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [PR Description Template](#pr-description-template)
- [Commit Message Format](#commit-message-format)
- [Code Style](#code-style)
- [Testing](#testing)

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

---

## How to Contribute

### 🐛 Bug Reports

**Before reporting:**
- Check existing issues
- Verify the bug exists in the latest version
- Collect relevant logs and screenshots

**Issue template:**

```markdown
## Bug Description
A clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., macOS 14]
- Docker: [e.g., 24.0]
- Branch: [e.g., main]

## Logs
```
Paste relevant logs here
```

## Screenshots
If applicable, add screenshots.
```

### 💡 Feature Requests

**Issue template:**

```markdown
## Feature Description
A clear description of the feature.

## Use Case
Why is this feature needed?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
Other approaches you've thought about.

## Additional Context
Any other relevant information.
```

### 📝 Documentation

- Fix typos and grammar
- Add examples and explanations
- Improve clarity and structure
- Add screenshots where helpful

### 🔧 Code Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a PR

---

## Development Setup

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR-USERNAME/django-observability.git
cd django-observability
```

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
# or
git checkout -b docs/your-docs-update
```

### 3. Start Services

```bash
cp django_app/.env.example django_app/.env
docker compose -f django_app/docker-compose.yml up -d
```

### 4. Make Changes

Edit files, test locally, verify everything works.

### 5. Test

```bash
# Verify all services are running
docker compose -f django_app/docker-compose.yml ps

# Test endpoints
curl http://localhost:9000/metrics
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
```

---

## PR Description Template

Use this template when creating Pull Requests:

```markdown
## Description

Brief description of what this PR does.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🔧 Configuration change
- [ ] ♻️ Refactoring (no functional changes)

## Changes Made

- Change 1
- Change 2
- Change 3

## Related Issues

Closes #123
Fixes #456
Related to #789

## Testing

Describe how you tested your changes:

- [ ] Tested locally with Docker
- [ ] Verified all services start correctly
- [ ] Tested specific functionality: [describe]
- [ ] No breaking changes to existing features

## Screenshots (if applicable)

Add screenshots for UI changes.

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have added comments where necessary
- [ ] I have updated documentation accordingly
- [ ] My changes generate no new warnings
- [ ] I have tested my changes locally
- [ ] Any dependent changes have been merged

## Additional Notes

Any additional information that reviewers should know.
```

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add Prometheus alert rules` |
| `fix` | Bug fix | `fix: resolve Loki connection timeout` |
| `docs` | Documentation | `docs: update getting started guide` |
| `style` | Code style | `style: format Python files` |
| `refactor` | Refactoring | `refactor: simplify Docker setup` |
| `test` | Testing | `test: add integration tests` |
| `chore` | Maintenance | `chore: update dependencies` |
| `ci` | CI/CD | `ci: add GitHub Actions workflow` |
| `perf` | Performance | `perf: optimize Prometheus queries` |

### Scopes

| Scope | Description |
|-------|-------------|
| `django` | Django application |
| `prometheus` | Prometheus configuration |
| `grafana` | Grafana dashboards |
| `loki` | Loki configuration |
| `alertmanager` | Alertmanager settings |
| `docker` | Docker configuration |
| `docs` | Documentation |
| `mcp` | MCP Server |
| `nginx` | Nginx configuration |

### Examples

```bash
# Feature
git commit -m "feat(prometheus): add custom alert rules for database"

# Bug fix
git commit -m "fix(loki): resolve log parsing issue for JSON format"

# Documentation
git commit -m "docs: add troubleshooting guide for common issues"

# Configuration
git commit -m "chore(docker): update PostgreSQL to version 16"

# Breaking change
git commit -m "feat(django)!: migrate to Django 5.0

BREAKING CHANGE: Requires Python 3.12+"
```

---

## Code Style

### Python

- Follow PEP 8
- Use type hints where possible
- Add docstrings for functions
- Keep functions small and focused

### Docker

- Use official base images
- Minimize layers
- Use multi-stage builds where appropriate
- Add health checks

### Documentation

- Use clear, concise language
- Add code examples
- Include prerequisites
- Provide troubleshooting steps

### YAML/Configuration

- Use 2-space indentation
- Add comments for complex settings
- Group related settings together

---

## Testing

### Local Testing

```bash
# Start all services
docker compose -f django_app/docker-compose.yml up -d

# Test Django
curl http://localhost:9000/metrics | head -5

# Test Prometheus
curl http://localhost:9090/-/healthy

# Test Grafana
curl http://localhost:3000/api/health

# Test Loki
curl http://localhost:3100/ready

# Test Alertmanager
curl http://localhost:9093/-/healthy
```

### Documentation Testing

```bash
# Build documentation
mkdocs build --strict

# Serve locally
mkdocs serve
```

---

## Questions?

- 💬 [GitHub Discussions](https://github.com/MdAshiqurRahmanZayed/django-observability/discussions)
- 🐛 [Issue Tracker](https://github.com/MdAshiqurRahmanZayed/django-observability/issues)

---

Thank you for contributing! 🎉
