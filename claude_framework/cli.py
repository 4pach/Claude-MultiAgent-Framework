"""
Command Line Interface for Claude MultiAgent Framework
"""

import click
import asyncio
from pathlib import Path
from loguru import logger
from claude_framework import Framework

@click.group()
@click.version_option(version="1.0.0")
def main():
    """Claude MultiAgent Framework CLI"""
    pass

@main.command()
@click.option("--name", required=True, help="Project name")
@click.option("--type", "project_type", required=True, 
              type=click.Choice(['telegram_bot', 'web_api', 'cli_tool', 'ml_service']),
              help="Project template type")
@click.option("--output-dir", default=".", help="Output directory")
@click.option("--config", help="Configuration file path")
def create(name: str, project_type: str, output_dir: str, config: str):
    """Create a new project from template"""
    click.echo(f"🧠 Creating {project_type} project: {name}")
    
    try:
        framework = Framework()
        
        # Create project using the framework
        result_path = asyncio.run(_create_project(framework, name, project_type, output_dir))
        
        click.echo(f"✅ Project created successfully at: {result_path}")
        click.echo(f"🚀 To start development:")
        click.echo(f"   cd {result_path}")
        click.echo(f"   pip install -r requirements.txt")
        click.echo(f"   python main.py")
        
    except Exception as e:
        click.echo(f"❌ Error creating project: {e}", err=True)
        exit(1)

async def _create_project(framework: Framework, name: str, project_type: str, output_dir: str) -> str:
    """Async project creation"""
    await framework.start()
    
    task = {
        'type': 'project_creation',
        'name': name,
        'template': project_type,
        'output_dir': output_dir
    }
    
    result = await framework.process_task(task)
    await framework.stop()
    
    return result.get('project_path', f"{output_dir}/{name}")

@main.command()
def monitor():
    """Show monitoring dashboard"""
    click.echo("📊 Claude MultiAgent Framework - Monitoring Dashboard")
    click.echo("=" * 50)
    click.echo("Feature coming soon...")

@main.command()
def optimize():
    """Run optimization analysis"""
    click.echo("🔧 Claude MultiAgent Framework - Optimization")
    click.echo("=" * 50)
    click.echo("Feature coming soon...")

if __name__ == "__main__":
    main()
