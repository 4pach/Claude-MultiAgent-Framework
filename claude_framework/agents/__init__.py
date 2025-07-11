"""
Agent implementations for Claude MultiAgent Framework
"""

from .base import BaseAgent
from .architect import Architect
from .engineer import Engineer
from .integrator import Integrator
from .critic import Critic
from .manager import Manager
from .optimizer import Optimizer

__all__ = [
    'BaseAgent',
    'Architect', 
    'Engineer',
    'Integrator',
    'Critic',
    'Manager',
    'Optimizer'
]
