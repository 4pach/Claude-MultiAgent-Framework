#!/usr/bin/env python3
"""
Setup script for Claude MultiAgent Framework
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Claude MultiAgent Framework - Full Multi-Agent Development Framework"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "click>=8.0.0",
            "pydantic>=2.0.0",
            "sqlalchemy>=2.0.0",
            "aiosqlite>=0.19.0",
            "httpx>=0.24.0",
            "loguru>=0.7.0",
            "scikit-learn>=1.3.0",
            "numpy>=1.24.0",
            "jinja2>=3.1.0"
        ]

setup(
    name="claude-multiagent-framework",
    version="1.0.0",
    author="4pach",
    author_email="contact@4pach.dev",
    description="Full Claude Multi-Agent Development Framework with MCP, VibeCoding, Templates, CI/CD and Monitoring",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/4pach/Claude-MultiAgent-Framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "claude-framework=claude_framework.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="claude ai multi-agent framework mcp monitoring optimization",
    project_urls={
        "Bug Reports": "https://github.com/4pach/Claude-MultiAgent-Framework/issues",
        "Source": "https://github.com/4pach/Claude-MultiAgent-Framework",
        "Documentation": "https://4pach.github.io/Claude-MultiAgent-Framework/",
        "Sponsor": "https://boosty.to/4pach",
    },
)
