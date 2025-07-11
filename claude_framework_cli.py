#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude MultiAgent Framework CLI
Интерфейс командной строки для управления фреймворком

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import os
import sys
import json
import click
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(str(Path(__file__).parent))

try:
    from project_templates import create_project_from_template
    from config_profiles import get_config_for_project, create_project_config
    from config_validator import validate_project_config, config_validator
except ImportError as e:
    print(f"⚠️ Предупреждение: некоторые модули недоступны: {e}")
    print("Некоторые функции могут быть ограничены.")

console = Console()

class FrameworkCLI:
    """CLI для Claude MultiAgent Framework"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.current_project = self._detect_current_project()
    
    def _detect_current_project(self) -> Optional[Dict]:
        """Определение текущего проекта"""
        config_file = Path("config/framework_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def show_banner(self):
        """Отображение баннера CLI"""
        banner_text = Text()
        banner_text.append("Claude MultiAgent Framework", style="bold cyan")
        banner_text.append(f" v{self.version}", style="dim")
        
        panel = Panel(
            banner_text,
            title="🤖 Framework CLI",
            border_style="cyan",
            box=box.ROUNDED
        )
        console.print(panel)

@click.group()
@click.version_option(version="1.0.0", prog_name="Claude MultiAgent Framework CLI")
@click.pass_context
def cli(ctx):
    """Claude MultiAgent Framework - CLI для управления проектами"""
    ctx.ensure_object(dict)
    ctx.obj['cli'] = FrameworkCLI()

@cli.command()
@click.option('--name', '-n', required=True, help='Имя проекта')
@click.option('--type', '-t', 'project_type', 
              type=click.Choice([
                  'telegram_bot', 'web_api', 'cli_tool', 'data_pipeline',
                  'microservice', 'ml_service', 'desktop_app', 'iot_device'
              ]), required=True, help='Тип проекта')
@click.option('--scale', '-s', 
              type=click.Choice(['minimal', 'standard', 'advanced', 'enterprise']),
              default='standard', help='Масштаб проекта')
@click.option('--dir', '-d', 'output_dir', help='Директория для создания проекта')
@click.option('--no-install', is_flag=True, help='Не устанавливать зависимости')
@click.option('--no-git', is_flag=True, help='Не инициализировать Git')
def create(name, project_type, scale, output_dir, no_install, no_git):
    """Создать новый проект с Claude MultiAgent Framework"""
    
    console.print(f"🏗️ Создание проекта: [bold]{name}[/bold]")
    console.print(f"📋 Тип: [cyan]{project_type}[/cyan]")
    console.print(f"📊 Масштаб: [yellow]{scale}[/yellow]")
    
    try:
        # Создание проекта
        if 'create_project_from_template' in globals():
            project_path = create_project_from_template(name, project_type, scale)
            
            if output_dir:
                import shutil
                target_path = Path(output_dir) / name
                if target_path.exists():
                    console.print(f"[red]❌ Директория {target_path} уже существует[/red]")
                    return
                
                shutil.move(project_path, target_path)
                project_path = str(target_path)
        else:
            # Fallback: базовое создание
            project_path = output_dir or f"./generated_projects/{name}"
            Path(project_path).mkdir(parents=True, exist_ok=True)
            
            # Создание базовых файлов
            (Path(project_path) / "framework_init.py").write_text(
                f'print("Проект {name} создан!")'
            )
        
        console.print(f"✅ Проект создан: [green]{project_path}[/green]")
        
        # Дополнительные действия
        if not no_install:
            console.print("📦 Установка зависимостей...")
            # TODO: запуск установки зависимостей
        
        if not no_git:
            console.print("📚 Инициализация Git...")
            # TODO: инициализация Git
        
        # Инструкции
        console.print("\n🚀 [bold]Для начала работы:[/bold]")
        console.print(f"cd {project_path}")
        console.print("python framework_init.py")
        
    except Exception as e:
        console.print(f"[red]❌ Ошибка создания проекта: {e}[/red]")

@cli.command()
@click.option('--project-type', '-t', help='Фильтр по типу проекта')
def list_profiles(project_type):
    """Показать доступные профили конфигурации"""
    
    try:
        if 'profile_manager' in globals():
            from config_profiles import profile_manager, ProjectType
            
            # Получение списка профилей
            project_type_enum = None
            if project_type:
                try:
                    project_type_enum = ProjectType(project_type)
                except ValueError:
                    console.print(f"[red]❌ Неизвестный тип проекта: {project_type}[/red]")
                    return
            
            profiles = profile_manager.list_profiles(project_type_enum)
            
            # Создание таблицы
            table = Table(title="Доступные профили конфигурации")
            table.add_column("Имя профиля", style="cyan")
            table.add_column("Тип проекта", style="green")
            table.add_column("Масштаб", style="yellow")
            table.add_column("Описание", style="white")
            
            for profile_name in profiles:
                profile = profile_manager.get_profile(profile_name)
                if profile:
                    table.add_row(
                        profile_name,
                        profile.project_type.value,
                        profile.scale_profile.value,
                        profile.name
                    )
            
            console.print(table)
        else:
            console.print("[yellow]⚠️ Модуль профилей недоступен[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Ошибка получения профилей: {e}[/red]")

@cli.command()
@click.argument('config_file', required=False)
def validate(config_file):
    """Валидация конфигурации проекта"""
    
    if not config_file:
        # Поиск конфигурации в текущем проекте
        config_file = "config/framework_config.json"
        if not Path(config_file).exists():
            console.print("[red]❌ Конфигурационный файл не найден[/red]")
            console.print("Укажите путь к файлу или запустите в директории проекта")
            return
    
    console.print(f"🔍 Валидация конфигурации: [cyan]{config_file}[/cyan]")
    
    try:
        if 'validate_project_config' in globals():
            is_valid = validate_project_config(config_file)
            
            if is_valid:
                console.print("[green]✅ Конфигурация корректна![/green]")
            else:
                console.print("[red]❌ Обнаружены проблемы в конфигурации[/red]")
        else:
            console.print("[yellow]⚠️ Модуль валидации недоступен[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Ошибка валидации: {e}[/red]")

@cli.command()
@click.option('--name', '-n', required=True, help='Имя конфигурации')
@click.option('--type', '-t', 'config_type', required=True, help='Тип проекта')
@click.option('--scale', '-s', default='standard', help='Масштаб проекта')
@click.option('--output', '-o', help='Файл для сохранения')
def generate_config(name, config_type, scale, output):
    """Генерация конфигурации для проекта"""
    
    console.print(f"⚙️ Генерация конфигурации: [bold]{name}[/bold]")
    
    try:
        if 'create_project_config' in globals():
            config_file = create_project_config(name, config_type, scale)
            
            if output:
                import shutil
                shutil.move(config_file, output)
                config_file = output
            
            console.print(f"✅ Конфигурация создана: [green]{config_file}[/green]")
        else:
            console.print("[yellow]⚠️ Модуль генерации конфигурации недоступен[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Ошибка генерации: {e}[/red]")

@cli.command()
def status():
    """Показать статус текущего проекта"""
    
    # Определение текущего проекта
    config_file = Path("config/framework_config.json")
    
    if not config_file.exists():
        console.print("[yellow]⚠️ Не найдена конфигурация фреймворка[/yellow]")
        console.print("Запустите команду в директории проекта или создайте новый проект")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Создание панели статуса
        project_info = config.get('project', {})
        framework_info = config.get('framework', {})
        
        status_text = Text()
        status_text.append(f"Проект: ", style="bold")
        status_text.append(f"{project_info.get('name', 'Unknown')}\n", style="cyan")
        status_text.append(f"Тип: ", style="bold")
        status_text.append(f"{project_info.get('type', 'Unknown')}\n", style="green")
        status_text.append(f"Масштаб: ", style="bold")
        status_text.append(f"{project_info.get('scale', 'Unknown')}\n", style="yellow")
        status_text.append(f"Версия: ", style="bold")
        status_text.append(f"{project_info.get('version', 'Unknown')}", style="white")
        
        panel = Panel(
            status_text,
            title="📊 Статус проекта",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(panel)
        
        # Статус компонентов
        components = framework_info.get('components', {})
        if components:
            table = Table(title="Компоненты фреймворка")
            table.add_column("Компонент", style="cyan")
            table.add_column("Статус", style="white")
            
            for component, enabled in components.items():
                status_icon = "✅ Включен" if enabled else "❌ Отключен"
                status_style = "green" if enabled else "red"
                table.add_row(component, f"[{status_style}]{status_icon}[/{status_style}]")
            
            console.print(table)
        
        # Проверка файлов
        console.print("\n🔍 [bold]Проверка файлов:[/bold]")
        
        essential_files = [
            "framework_init.py",
            "requirements.txt",
            "README.md"
        ]
        
        for file_name in essential_files:
            if Path(file_name).exists():
                console.print(f"✅ {file_name}")
            else:
                console.print(f"❌ [red]{file_name}[/red]")
        
    except Exception as e:
        console.print(f"[red]❌ Ошибка получения статуса: {e}[/red]")

@cli.command()
@click.option('--component', '-c', help='Инициализировать конкретный компонент')
def init(component):
    """Инициализация фреймворка в текущем проекте"""
    
    console.print("🚀 Инициализация Claude MultiAgent Framework...")
    
    try:
        # Поиск framework_init.py
        init_file = Path("framework_init.py")
        if init_file.exists():
            # Запуск инициализации
            result = subprocess.run(
                [sys.executable, "framework_init.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("✅ [green]Фреймворк инициализирован успешно![/green]")
                if result.stdout:
                    console.print(result.stdout)
            else:
                console.print("[red]❌ Ошибка инициализации[/red]")
                if result.stderr:
                    console.print(f"[red]{result.stderr}[/red]")
        else:
            console.print("[red]❌ Файл framework_init.py не найден[/red]")
            console.print("Убедитесь, что вы находитесь в директории проекта")
    
    except Exception as e:
        console.print(f"[red]❌ Ошибка инициализации: {e}[/red]")

@cli.command()
def install():
    """Запуск интерактивного инсталлятора"""
    
    console.print("🔧 Запуск интерактивного инсталлятора...")
    
    # Поиск скрипта установки
    install_script = Path("install.py")
    if install_script.exists():
        try:
            subprocess.run([sys.executable, str(install_script)], check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Ошибка установки: {e}[/red]")
    else:
        console.print("[red]❌ Скрипт установки не найден[/red]")
        console.print("Загрузите install.py с официального репозитория")

@cli.command()
@click.option('--format', 'output_format', 
              type=click.Choice(['table', 'json', 'yaml']),
              default='table', help='Формат вывода')
def list_templates(output_format):
    """Показать доступные шаблоны проектов"""
    
    templates_info = [
        {
            "name": "telegram_bot",
            "description": "Telegram бот с мониторингом",
            "scales": ["minimal", "advanced"]
        },
        {
            "name": "web_api",
            "description": "RESTful API на FastAPI",
            "scales": ["standard", "enterprise"]
        },
        {
            "name": "cli_tool",
            "description": "Консольная утилита",
            "scales": ["minimal"]
        },
        {
            "name": "data_pipeline",
            "description": "Pipeline обработки данных",
            "scales": ["standard"]
        },
        {
            "name": "microservice",
            "description": "Микросервис",
            "scales": ["standard"]
        },
        {
            "name": "ml_service",
            "description": "ML сервис",
            "scales": ["advanced"]
        }
    ]
    
    if output_format == 'table':
        table = Table(title="Доступные шаблоны проектов")
        table.add_column("Шаблон", style="cyan")
        table.add_column("Описание", style="white")
        table.add_column("Доступные масштабы", style="yellow")
        
        for template in templates_info:
            scales_str = ", ".join(template["scales"])
            table.add_row(
                template["name"],
                template["description"], 
                scales_str
            )
        
        console.print(table)
        
    elif output_format == 'json':
        import json
        console.print(json.dumps(templates_info, indent=2, ensure_ascii=False))
        
    elif output_format == 'yaml':
        try:
            import yaml
            console.print(yaml.dump(templates_info, default_flow_style=False, allow_unicode=True))
        except ImportError:
            console.print("[red]❌ PyYAML не установлен[/red]")

@cli.command()
def version():
    """Показать версию фреймворка"""
    
    # Создание информационной панели
    version_text = Text()
    version_text.append("Claude MultiAgent Framework\n", style="bold cyan")
    version_text.append(f"Версия: 1.0.0\n", style="white")
    version_text.append("Автор: Claude MultiAgent System\n", style="dim")
    version_text.append("Дата: 2025-07-11", style="dim")
    
    panel = Panel(
        version_text,
        title="ℹ️ Информация",
        border_style="blue",
        box=box.ROUNDED
    )
    console.print(panel)

if __name__ == '__main__':
    cli()