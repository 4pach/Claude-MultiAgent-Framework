"""
Core framework functionality for Claude MultiAgent Framework
"""

import asyncio
from typing import Dict, List, Optional, Any
from loguru import logger
from .agents import BaseAgent, Architect, Engineer, Integrator, Critic, Manager, Optimizer
from .monitoring import MonitoringService
from .config import FrameworkConfig

class Framework:
    """Main framework class that coordinates multi-agent operations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the framework with configuration"""
        self.config = FrameworkConfig(config or {})
        self.agents: Dict[str, BaseAgent] = {}
        self.monitoring = MonitoringService(self.config.monitoring)
        self.is_running = False
        
        # Initialize default agents
        self._initialize_agents()
        
        logger.info("Claude MultiAgent Framework initialized")
    
    def _initialize_agents(self):
        """Initialize the six core agents"""
        agent_classes = {
            'architect': Architect,
            'engineer': Engineer, 
            'integrator': Integrator,
            'critic': Critic,
            'manager': Manager,
            'optimizer': Optimizer
        }
        
        for name, agent_class in agent_classes.items():
            if self.config.agents.get(name, {}).get('enabled', True):
                self.agents[name] = agent_class(
                    framework=self,
                    config=self.config.agents.get(name, {})
                )
                logger.debug(f"Initialized {name} agent")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task through the multi-agent system"""
        logger.info(f"Processing task: {task.get('type', 'unknown')}")
        
        # Manager coordinates the task
        manager = self.get_agent('manager')
        if not manager:
            raise RuntimeError("Manager agent not available")
        
        result = await manager.coordinate_task(task)
        
        # Optimizer reviews and suggests improvements
        optimizer = self.get_agent('optimizer')
        if optimizer:
            await optimizer.optimize_result(result)
        
        return result
    
    async def start(self):
        """Start the framework"""
        self.is_running = True
        await self.monitoring.start()
        logger.info("Framework started")
    
    async def stop(self):
        """Stop the framework"""
        self.is_running = False
        await self.monitoring.stop()
        logger.info("Framework stopped")
    
    def create_project(self, name: str, template: str, **kwargs) -> str:
        """Create a new project from template"""
        engineer = self.get_agent('engineer')
        if not engineer:
            raise RuntimeError("Engineer agent not available")
        
        return engineer.create_project(name, template, **kwargs)
