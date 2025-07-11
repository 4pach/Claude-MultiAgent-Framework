"""
Base agent class for Claude MultiAgent Framework
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger

class BaseAgent(ABC):
    """Base class for all framework agents"""
    
    def __init__(self, framework=None, config: Optional[Dict[str, Any]] = None):
        self.framework = framework
        self.config = config or {}
        self.role = self.__class__.__name__.lower()
        self.status = "ready"
        
        logger.debug(f"Initialized {self.role} agent")
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data according to agent's role"""
        pass
    
    def get_status(self) -> str:
        """Get current agent status"""
        return self.status
    
    async def coordinate_with(self, other_agent: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with another agent"""
        if self.framework:
            agent = self.framework.get_agent(other_agent)
            if agent:
                return await agent.process(data)
        
        logger.warning(f"Could not coordinate with {other_agent}")
        return {}
