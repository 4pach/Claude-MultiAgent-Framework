"""
Monitoring and MCP tracking for Claude MultiAgent Framework
"""

import time
import asyncio
from typing import Dict, Any, Callable
from functools import wraps
from loguru import logger

class MonitoringService:
    """Service for monitoring MCP calls and performance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.calls_log = []
        self.is_running = False
        
    async def start(self):
        """Start monitoring service"""
        self.is_running = True
        logger.info("Monitoring service started")
    
    async def stop(self):
        """Stop monitoring service"""
        self.is_running = False
        logger.info("Monitoring service stopped")
    
    def track_call(self, service: str, operation: str, duration: float, **kwargs):
        """Track an MCP call"""
        call_data = {
            'timestamp': time.time(),
            'service': service,
            'operation': operation,
            'duration': duration,
            'metadata': kwargs
        }
        
        self.calls_log.append(call_data)
        
        logger.debug(f"Tracked {service}.{operation} ({duration:.3f}s)")
    
    def get_stats(self, timeframe: str = "24h") -> Dict[str, Any]:
        """Get performance statistics"""
        total_calls = len(self.calls_log)
        avg_duration = sum(call['duration'] for call in self.calls_log) / max(total_calls, 1)
        
        return {
            'total_calls': total_calls,
            'avg_duration': avg_duration,
            'services': list(set(call['service'] for call in self.calls_log))
        }

def track_mcp_call(service: str, operation: str):
    """Decorator to track MCP calls"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log the call (would integrate with framework monitoring)
                logger.info(f"MCP Call: {service}.{operation} completed in {duration:.3f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"MCP Call: {service}.{operation} failed after {duration:.3f}s: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"MCP Call: {service}.{operation} completed in {duration:.3f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"MCP Call: {service}.{operation} failed after {duration:.3f}s: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
