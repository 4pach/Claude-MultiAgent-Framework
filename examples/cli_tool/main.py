#!/usr/bin/env python3
"""
CLI Tool example using Claude MultiAgent Framework
"""

import click
import asyncio
from claude_framework import Framework, track_mcp_call
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
framework = Framework()

@click.group()
def cli():
    """Claude MultiAgent Framework CLI Example"""
    pass

@cli.command()
@click.argument('text')
@click.option('--agent', default='architect', help='Agent to use for processing')
@track_mcp_call("cli_tool", "process_text")
def process(text: str, agent: str):
    """Process text using specified agent"""
    
    async def _process():
        await framework.start()
        
        agent_instance = framework.get_agent(agent)
        if not agent_instance:
            console.print(f"❌ Agent '{agent}' not found", style="red")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(f"Processing with {agent} agent...", total=None)
            
            result = await agent_instance.process({
                'type': 'text_processing',
                'text': text
            })
            
            progress.update(task, completed=True)
        
        console.print("✅ Processing complete!", style="green")
        console.print(f"Result: {result}")
        
        await framework.stop()
    
    asyncio.run(_process())

@cli.command()
def agents():
    """List available agents"""
    
    async def _list_agents():
        await framework.start()
        
        console.print("🤖 Available Agents:", style="bold blue")
        for name, agent in framework.agents.items():
            status = agent.get_status()
            console.print(f"  • {name}: {status}")
        
        await framework.stop()
    
    asyncio.run(_list_agents())

@cli.command()  
def monitor():
    """Show monitoring statistics"""
    
    async def _show_stats():
        await framework.start()
        
        if framework.monitoring:
            stats = framework.monitoring.get_stats()
            
            console.print("📊 Monitoring Statistics:", style="bold green")
            console.print(f"  Total calls: {stats.get('total_calls', 0)}")
            console.print(f"  Average duration: {stats.get('avg_duration', 0):.3f}s")
            console.print(f"  Services: {', '.join(stats.get('services', []))}")
        else:
            console.print("❌ Monitoring not available", style="red")
        
        await framework.stop()
    
    asyncio.run(_show_stats())

if __name__ == "__main__":
    cli()
