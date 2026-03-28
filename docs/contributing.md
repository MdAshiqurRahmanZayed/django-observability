# Contributing Guide

We welcome contributions from the community! This guide explains how to contribute to the Django Observability Stack.

---

## Ways to Contribute

| Type | Description | How |
|------|-------------|-----|
| 🐛 **Bug Reports** | Found something broken? | [Create Issue](https://github.com/MdAshiqurRahmanZayed/django-observability/issues/new?template=bug_report.md) |
| 💡 **Feature Requests** | Have an idea? | [Create Issue](https://github.com/MdAshiqurRahmanZayed/django-observability/issues/new?template=feature_request.md) |
| 📝 **Documentation** | Improve guides | [Fork & PR](https://github.com/MdAshiqurRahmanZayed/django-observability/fork) |
| 🔧 **Code** | Fix bugs, add features | [Fork & PR](https://github.com/MdAshiqurRahmanZayed/django-observability/fork) |

---

## Getting Started

### 1. Fork the Repository

Go to [github.com/MdAshiqurRahmanZayed/django-observability](https://github.com/MdAshiqurRahmanZayed/django-observability) and click "Fork".

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/django-observability.git
cd django-observability
```

### 3. Create a Branch

```bash
# For features
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/your-bug-fix

# For documentation
git checkout -b docs/your-docs-update
```

### 4. Make Changes

Edit the files you want to change.

### 5. Test Locally

```bash
# Start services
docker compose -f django_app/docker-compose.yml up -d

# Verify
curl http://localhost:9000/metrics
curl http://localhost:9090/-/healthy
```

### 6. Commit & Push

```bash
git add .
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
```

### 7. Create Pull Request

Go to your fork on GitHub and click "New Pull Request".

---

## PR Description Template

Use this template when creating a Pull Request:

```markdown
## Description

Brief description of the changes.

## Type of Change

- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📝 Documentation
- [ ] 🔧 Configuration
- [ ] ♻️ Refactoring

## Changes

- Change 1
- Change 2
- Change 3

## Related Issues

Closes #123

## Testing

- [ ] Tested locally
- [ ] All services running
- [ ] No breaking changes

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Code formatting |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance |

### Examples

```bash
feat(prometheus): add custom alert rules
fix(loki): resolve log parsing issue
docs: update getting started guide
chore(docker): update PostgreSQL to version 16
```

---

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Add docstrings

### Docker

- Use official images
- Add health checks
- Minimize layers

### Documentation

- Clear and concise
- Include examples
- Add troubleshooting

---

## Testing

### Test Your Changes

```bash
# Start stack
docker compose -f django_app/docker-compose.yml up -d

# Test endpoints
curl http://localhost:9000/metrics
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
curl http://localhost:3100/ready
```

### Build Documentation

```bash
mkdocs build --strict
```

---

## Questions?

- 💬 [GitHub Discussions](https://github.com/MdAshiqurRahmanZayed/django-observability/discussions)
- 🐛 [Issue Tracker](https://github.com/MdAshiqurRahmanZayed/django-observability/issues)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
