---
title: Quick Start Guide
layout: default
nav_order: 2
---

# 🚀 Quick Start Guide

Get up and running with Claude MultiAgent Framework in minutes.

## Prerequisites

- Python 3.8 or higher
- Git
- Claude Code (recommended)

## Installation

### Method 1: One-Command Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/4pach/Claude-MultiAgent-Framework/main/install.sh | bash
```

### Method 2: Manual Installation

```bash
git clone https://github.com/4pach/Claude-MultiAgent-Framework.git
cd Claude-MultiAgent-Framework
python install.py
```

### Method 3: Windows

```cmd
curl -O https://raw.githubusercontent.com/4pach/Claude-MultiAgent-Framework/main/install.bat
install.bat
```

## Your First Project

### 1. Create a Telegram Bot

```bash
claude-framework create --name MyBot --type telegram_bot
cd MyBot
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit your configuration
nano .env
```

### 3. Run Your Bot

```bash
python main.py
```

## Next Steps

- [Architecture Guide](architecture.md) - Understand the multi-agent system
- [API Reference](api.md) - Complete API documentation
- [Examples](examples.md) - Real-world usage examples

## Troubleshooting

### Common Issues

**Installation fails**
```bash
# Ensure Python 3.8+ is installed
python --version

# Try with python3
python3 install.py
```

**Permission errors**
```bash
# On Linux/macOS
chmod +x install.sh
./install.sh

# Or use sudo if needed
sudo ./install.sh
```

**Missing dependencies**
```bash
# Install manually
pip install -r requirements.txt
```

## Getting Help

- 🐛 [Report Issues](https://github.com/4pach/Claude-MultiAgent-Framework/issues)
- 💬 [GitHub Discussions](https://github.com/4pach/Claude-MultiAgent-Framework/discussions)
- 📧 [Contact Support](mailto:support@4pach.dev)
