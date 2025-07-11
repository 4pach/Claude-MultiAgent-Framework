#!/bin/bash
# Claude MultiAgent Framework Installer
# One-command installation script

set -e

echo "🧠 Claude MultiAgent Framework Installer"
echo "========================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📦 Downloading Claude MultiAgent Framework..."

# Download the latest release
curl -L -o framework.tar.gz "https://github.com/4pach/Claude-MultiAgent-Framework/archive/refs/heads/main.tar.gz"
tar -xzf framework.tar.gz
cd Claude-MultiAgent-Framework-main

echo "🔧 Installing dependencies..."

# Install framework
pip3 install -e . --user

echo "🎯 Setting up CLI command..."

# Add to PATH if not already there
CLI_PATH="$HOME/.local/bin"
if [[ ":$PATH:" != *":$CLI_PATH:"* ]]; then
    echo "export PATH="$CLI_PATH:\$PATH"" >> "$HOME/.bashrc"
    echo "Added $CLI_PATH to PATH in .bashrc"
fi

# Create symbolic link for easy access
if [ -f "$CLI_PATH/claude-framework" ]; then
    echo "✅ CLI command 'claude-framework' is ready!"
else
    echo "⚠️  CLI command may need shell restart. Run: source ~/.bashrc"
fi

# Cleanup
cd ..
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Quick start:"
echo "  claude-framework create --name MyProject --type telegram_bot"
echo ""
echo "Documentation: https://github.com/4pach/Claude-MultiAgent-Framework"
echo "Support: https://boosty.to/4pach"
echo ""
