---
title: Claude MultiAgent Framework
layout: default
nav_order: 1
---

# 🧠 Claude MultiAgent Framework

**Full Claude Multi-Agent Development Framework with MCP, VibeCoding, Templates and Monitoring**

{: .fs-6 .fw-300 }

[Get Started](#quick-start){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/4pach/Claude-MultiAgent-Framework){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## ✨ What is Claude MultiAgent Framework?

Claude MultiAgent Framework is the **first production-ready framework** specifically designed for **Claude Code** development with:

- 🧠 **Multi-Agent Architecture** - 6 specialized sub-agents working together
- 📊 **Comprehensive Monitoring** - Real-time MCP call tracking and analytics
- 🔄 **Autonomous Optimization** - ML-powered self-improvement
- 🚀 **Production Ready** - Project templates and best practices

---

## 🎯 Why Use This Framework?

### The Problem with Claude Code Development
- **No visibility** into MCP calls and performance
- **Manual setup** for every new project
- **No cost tracking** or optimization
- **Repetitive boilerplate** code

### Our Solution
- **Automatic MCP monitoring** - see every call, cost, and performance metric
- **Instant project templates** - start coding in 30 seconds
- **ML-powered optimization** - reduce costs automatically
- **Built-in best practices** - no more boilerplate

---

## 🚀 Quick Start

### One-Command Installation

```bash
curl -sSL https://raw.githubusercontent.com/4pach/Claude-MultiAgent-Framework/main/install.sh | bash
```

### Create Your First Project

```bash
# 🤖 Telegram Bot with AI features
claude-framework create --name MyBot --type telegram_bot

# 🚀 FastAPI with auto-monitoring
claude-framework create --name MyAPI --type web_api

# 🧠 ML service with monitoring
claude-framework create --name MyML --type ml_service
```

---

## 🏗️ Architecture

The framework uses a **multi-agent architecture** with specialized roles:

| Agent | Role | Responsibility |
|-------|------|---------------|
| 🧠 **Architect** | Design & Planning | System architecture, project planning |
| 🧪 **Engineer** | Development & Testing | Code implementation, debugging |
| 📦 **Integrator** | External APIs & MCP | Third-party integrations |
| 🛡️ **Critic** | Security & Analysis | Risk assessment, validation |
| 🧭 **Manager** | Task Coordination | Workflow management |
| 💰 **Optimizer** | Performance & Cost | Resource optimization |

---

## 📦 Templates

Choose from professional project templates:

- 🤖 **Telegram Bot** - AI-powered bot with monitoring
- 🚀 **Web API** - Production FastAPI with auto-docs
- 🖥️ **CLI Tool** - Rich command-line interface
- 🧠 **ML Service** - MLflow integration

---

## 💡 Examples

### Basic Usage

```python
from claude_framework import Framework, track_mcp_call

# Initialize framework
framework = Framework()

@track_mcp_call("my_service", "process_data")
async def process_data(data):
    # Your code with automatic monitoring
    return processed_data
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/4pach/Claude-MultiAgent-Framework/blob/main/CONTRIBUTING.md) for details.

---

## 💖 Support

Support the project development:

[![Sponsor on Boosty](https://img.shields.io/badge/Sponsor-Boosty-orange)](https://boosty.to/4pach)
