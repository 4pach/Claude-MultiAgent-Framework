---
title: API Reference
layout: default
nav_order: 4
---

# 📚 API Reference

Complete API documentation for Claude MultiAgent Framework.

## Core Classes

### BaseAgent

Base class for all agents in the framework.

```python
from claude_framework import BaseAgent

class MyAgent(BaseAgent):
    role = "CustomRole"
    
    async def process(self, data):
        return await self.handle_task(data)
```

#### Methods

- `async process(data)` - Main processing method
- `track_performance()` - Enable performance tracking
- `get_status()` - Get agent status
- `configure(config)` - Configure agent settings

### MonitoringService

Handles all monitoring and analytics.

```python
from claude_framework.monitoring import MonitoringService

monitor = MonitoringService()
stats = monitor.get_stats(timeframe="24h")
```

#### Methods

- `get_stats(timeframe)` - Get performance statistics
- `track_call(service, operation)` - Track MCP calls
- `set_alert(condition, action)` - Configure alerts
- `export_metrics(format)` - Export metrics data

### OptimizationEngine

Provides AI-powered optimization recommendations.

```python
from claude_framework.optimization import OptimizationEngine

optimizer = OptimizationEngine()
recommendations = optimizer.analyze_performance()
```

#### Methods

- `analyze_performance()` - Analyze current performance
- `suggest_optimizations()` - Get improvement suggestions
- `apply_optimization(recommendation)` - Apply optimization
- `detect_anomalies()` - Detect performance anomalies

## Project Templates

### TelegramBot

Template for creating Telegram bots.

```python
from claude_framework.templates import TelegramBot

class MyBot(TelegramBot):
    async def handle_message(self, message):
        response = await self.ai_service.process(message.text)
        return response
```

### WebAPI

Template for FastAPI web services.

```python
from claude_framework.templates import WebAPI

app = WebAPI("MyAPI")

@app.post("/analyze")
async def analyze_data(data: DataModel):
    return await ai_analyzer.process(data)
```

### MLService

Template for ML services with MLflow integration.

```python
from claude_framework.templates import MLService

@MLService.log_experiment
def train_model(config):
    model = create_model(config)
    return model.train()
```

## Configuration

### Agent Configuration

```python
# config/agents.py
AGENT_CONFIG = {
    'architect': {
        'enabled': True,
        'max_concurrent_tasks': 3,
        'timeout': 30
    },
    'engineer': {
        'enabled': True,
        'max_concurrent_tasks': 5,
        'timeout': 60
    }
}
```

### Monitoring Configuration

```python
# config/monitoring.py
MONITORING_CONFIG = {
    'enabled': True,
    'database': 'sqlite:///monitoring.db',
    'retention_days': 30,
    'alerts': {
        'high_latency': {
            'threshold': 5.0,
            'action': 'email'
        }
    }
}
```

## CLI Commands

### Project Creation

```bash
claude-framework create --name PROJECT_NAME --type TEMPLATE_TYPE
```

Options:
- `--name`: Project name
- `--type`: Template type (telegram_bot, web_api, cli_tool, ml_service, etc.)
- `--output-dir`: Output directory
- `--config`: Custom configuration file

### Monitoring

```bash
claude-framework monitor --stats
```

Options:
- `--stats`: Show performance statistics
- `--alerts`: Show active alerts
- `--export`: Export metrics to file

### Optimization

```bash
claude-framework optimize --analyze
```

Options:
- `--analyze`: Analyze current performance
- `--recommend`: Get optimization recommendations
- `--apply`: Apply specific optimization

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLAUDE_FRAMEWORK_CONFIG` | Configuration file path | `config/config.py` |
| `CLAUDE_FRAMEWORK_DEBUG` | Enable debug mode | `False` |
| `CLAUDE_FRAMEWORK_LOG_LEVEL` | Log level | `INFO` |
| `CLAUDE_FRAMEWORK_DB_URL` | Database URL | `sqlite:///framework.db` |

## Error Handling

The framework provides comprehensive error handling:

```python
from claude_framework.exceptions import (
    AgentError,
    MonitoringError,
    OptimizationError
)

try:
    result = await agent.process(data)
except AgentError as e:
    logger.error(f"Agent error: {e}")
except MonitoringError as e:
    logger.error(f"Monitoring error: {e}")
```

## Examples

### Basic Usage

```python
from claude_framework import Framework

# Initialize framework
framework = Framework()

# Create and run agent
agent = framework.create_agent('architect')
result = await agent.process(task_data)
```

### With Monitoring

```python
from claude_framework import Framework, track_performance

framework = Framework(monitoring=True)

@track_performance
async def process_data(data):
    # Your processing logic
    return processed_data
```

### Custom Configuration

```python
from claude_framework import Framework

config = {
    'agents': {'architect': {'enabled': True}},
    'monitoring': {'enabled': True}
}

framework = Framework(config=config)
```
