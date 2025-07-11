"""
Claude MultiAgent Framework

A comprehensive framework for building multi-agent systems with Claude Code.
Provides monitoring, optimization, templates, and autonomous coordination.
"""

__version__ = "1.0.0"
__author__ = "4pach"
__email__ = "contact@4pach.dev"

from .core import Framework
from .agents import BaseAgent
from .monitoring import track_mcp_call, MonitoringService
from .templates import (
    TelegramBot,
    FastAPIApp,
    CLITool,
    MLService,
    DesktopApp
)

__all__ = [
    "Framework",
    "BaseAgent", 
    "track_mcp_call",
    "MonitoringService",
    "TelegramBot",
    "FastAPIApp", 
    "CLITool",
    "MLService",
    "DesktopApp"
]
