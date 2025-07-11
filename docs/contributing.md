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

### 5. Pre-commit Hooks

Install pre-commit hooks to automatically run checks:

```bash
pip install pre-commit
pre-commit install
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
# Good
class MyAgent(BaseAgent):
    # Agent that processes data
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
    
    async def process(self, data: dict) -> dict:
        # Process data and return result
        result = await self._internal_process(data)
        return result

# Bad
class myagent(BaseAgent):
    def __init__(self,config):
        super().__init__()
        self.config=config
    
    def process(self,data):
        result=self._internal_process(data)
        return result
```

### Documentation Style

Use clear, concise documentation:

```python
def analyze_performance(self, timeframe: str = "24h") -> dict:
    # Analyze system performance over specified timeframe
    # Args: timeframe - Time period to analyze (e.g., "1h", "24h", "7d")
    # Returns: Dictionary containing performance metrics
    # Raises: ValueError if timeframe format is invalid
    pass
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

## Testing Guidelines

### Unit Tests

```python
import pytest
from claude_framework import BaseAgent

class TestBaseAgent:
    def test_agent_initialization(self):
        agent = BaseAgent()
        assert agent.role == "BaseAgent"
        assert agent.status == "ready"
    
    @pytest.mark.asyncio
    async def test_agent_process(self):
        agent = BaseAgent()
        result = await agent.process({"test": "data"})
        assert result is not None
```

### Integration Tests

```python
import pytest
from claude_framework import Framework

class TestFrameworkIntegration:
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        framework = Framework()
        
        # Test agent creation
        agent = framework.create_agent("architect")
        assert agent is not None
        
        # Test task processing
        result = await agent.process({"task": "test"})
        assert result["status"] == "completed"
```

### Test Coverage

Aim for high test coverage:

```bash
# Check coverage
pytest --cov=claude_framework --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Documentation Guidelines

### API Documentation

Use docstrings for all public methods:

```python
def create_agent(self, agent_type: str, config: dict = None) -> BaseAgent:
    # Create a new agent instance
    # Args: agent_type - Type of agent to create (e.g., "architect", "engineer")
    #       config - Optional configuration dictionary
    # Returns: Configured agent instance
    # Raises: ValueError if agent_type is not supported
    pass
```

### README Updates

When adding new features, update the README:

1. Add feature to the feature list
2. Update installation instructions if needed
3. Add usage examples
4. Update the changelog

## Release Process

### Version Numbers

We use semantic versioning (SemVer):

- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features, backward compatible
- **Patch** (1.0.1): Bug fixes, backward compatible

### Creating Releases

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create release notes
4. Tag the release
5. Create GitHub release

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

### Getting Help

- Check existing issues and discussions
- Ask questions in GitHub Discussions
- Join our Discord server
- Email support for private matters

### Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file
- Release notes
- GitHub contributors section
- Special thanks in major releases

## License

By contributing to Claude MultiAgent Framework, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Claude MultiAgent Framework! Your help makes the project better for everyone.
