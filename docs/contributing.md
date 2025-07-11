---
title: Contributing
layout: default
nav_order: 6
---

# 🤝 Contributing

We welcome contributions to Claude MultiAgent Framework! This guide will help you get started.

## Ways to Contribute

### 🐛 Bug Reports
- Use the [bug report template](https://github.com/4pach/Claude-MultiAgent-Framework/issues/new?template=bug_report.md)
- Include steps to reproduce
- Provide environment details
- Add screenshots if applicable

### 🚀 Feature Requests
- Use the [feature request template](https://github.com/4pach/Claude-MultiAgent-Framework/issues/new?template=feature_request.md)
- Describe the use case
- Explain why it would be valuable
- Provide implementation ideas if you have them

### 💻 Code Contributions
- Fork the repository
- Create a feature branch
- Make your changes
- Add tests
- Submit a pull request

### 📖 Documentation
- Improve existing documentation
- Add examples
- Fix typos
- Translate documentation

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/Claude-MultiAgent-Framework.git
cd Claude-MultiAgent-Framework
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_framework

# Run specific test file
pytest tests/test_agents.py
```

### 4. Code Style

We use several tools to maintain code quality:

```bash
# Format code
black claude_framework/
black tests/

# Sort imports
isort claude_framework/
isort tests/

# Lint code
flake8 claude_framework/
flake8 tests/

# Type checking
mypy claude_framework/
```

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run tests
pytest

# Run full test suite
pytest tests/

# Test specific functionality
pytest tests/test_your_feature.py
```

### 4. Submit Pull Request

- Use the pull request template
- Describe what your PR does
- Link to related issues
- Ensure CI passes

## Code Style Guide

### Python Code Style

We follow PEP 8 with some specific conventions:

```python
# Good example
class MyAgent(BaseAgent):
    # Agent that processes data
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
    
    async def process(self, data: dict) -> dict:
        # Process data and return result
        result = await self._internal_process(data)
        return result
```

### Commit Messages

Use conventional commit format:

```bash
# Feature
feat: add new optimization algorithm

# Bug fix
fix: resolve memory leak in monitoring service

# Documentation
docs: update API reference with new endpoints

# Tests
test: add unit tests for agent coordination

# Refactor
refactor: simplify configuration loading logic
```

## Getting Help

- Check existing issues and discussions
- Ask questions in GitHub Discussions
- Email support for private matters

## License

By contributing to Claude MultiAgent Framework, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Claude MultiAgent Framework! Your help makes the project better for everyone.
