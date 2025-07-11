#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude MultiAgent Framework Installer
Автоматический инсталлятор фреймворка

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import os
import sys
import subprocess
import platform
import shutil
import json
import urllib.request
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

# Цвета для консольного вывода
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colorize(text: str, color: str) -> str:
    """Добавление цвета к тексту"""
    return f"{color}{text}{Colors.END}"

class FrameworkInstaller:
    """Инсталлятор Claude MultiAgent Framework"""
    
    def __init__(self):
        self.system_info = self._detect_system()
        self.installation_dir = None
        self.project_name = None
        self.project_type = None
        self.project_scale = None
        self.install_mode = "interactive"  # interactive, silent, config
        
        # Конфигурация по умолчанию
        self.config = {
            "create_venv": True,
            "install_dependencies": True,
            "initialize_git": True,
            "create_example": True,
            "run_tests": False
        }
    
    def _detect_system(self) -> Dict[str, str]:
        """Определение информации о системе"""
        return {
            "os": platform.system(),
            "arch": platform.machine(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "python_executable": sys.executable
        }
    
    def print_banner(self):
        """Отображение баннера инсталлятора"""
        banner = f"""
{colorize('╔' + '═' * 60 + '╗', Colors.CYAN)}
{colorize('║', Colors.CYAN)} {colorize('Claude MultiAgent Framework Installer', Colors.BOLD + Colors.WHITE)} {colorize('║', Colors.CYAN)}
{colorize('║', Colors.CYAN)} {' ' * 26} v1.0.0 {' ' * 26} {colorize('║', Colors.CYAN)}
{colorize('╚' + '═' * 60 + '╝', Colors.CYAN)}

{colorize('🤖 Универсальный фреймворк для автономного мониторинга', Colors.WHITE)}
{colorize('   и оптимизации проектов с помощью ИИ', Colors.WHITE)}

{colorize('Система:', Colors.YELLOW)} {self.system_info['os']} {self.system_info['arch']}
{colorize('Python:', Colors.YELLOW)} {self.system_info['python_version']}
"""
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Проверка системных требований"""
        print(f"\n{colorize('🔍 Проверка системных требований...', Colors.BLUE)}")
        
        requirements_met = True
        
        # Проверка версии Python
        if sys.version_info < (3, 8):
            print(f"{colorize('❌ Python 3.8+ требуется', Colors.RED)} (текущая: {self.system_info['python_version']})")
            requirements_met = False
        else:
            print(f"{colorize('✅ Python версия', Colors.GREEN)}: {self.system_info['python_version']}")
        
        # Проверка pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print(f"{colorize('✅ pip доступен', Colors.GREEN)}")
        except subprocess.CalledProcessError:
            print(f"{colorize('❌ pip не найден', Colors.RED)}")
            requirements_met = False
        
        # Проверка git (опционально)
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            print(f"{colorize('✅ git доступен', Colors.GREEN)}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{colorize('⚠️ git не найден (опционально)', Colors.YELLOW)}")
        
        # Проверка свободного места (минимум 100MB)
        if shutil.disk_usage(".")[2] < 100 * 1024 * 1024:
            print(f"{colorize('❌ Недостаточно свободного места', Colors.RED)} (требуется 100MB)")
            requirements_met = False
        else:
            print(f"{colorize('✅ Достаточно свободного места', Colors.GREEN)}")
        
        return requirements_met
    
    def interactive_setup(self):
        """Интерактивная настройка проекта"""
        print(f"\n{colorize('📋 Настройка проекта', Colors.BLUE)}")
        
        # Имя проекта
        while True:
            self.project_name = input(f"{colorize('Введите имя проекта:', Colors.CYAN)} ").strip()
            if self.project_name and self.project_name.replace("_", "").replace("-", "").isalnum():
                break
            print(f"{colorize('❌ Имя должно содержать только буквы, цифры, _ и -', Colors.RED)}")
        
        # Тип проекта
        project_types = {
            "1": ("telegram_bot", "Telegram Bot"),
            "2": ("web_api", "Web API"),
            "3": ("cli_tool", "CLI Tool"),
            "4": ("data_pipeline", "Data Pipeline"),
            "5": ("microservice", "Microservice"),
            "6": ("ml_service", "ML Service"),
            "7": ("desktop_app", "Desktop App"),
            "8": ("iot_device", "IoT Device")
        }
        
        print(f"\n{colorize('Выберите тип проекта:', Colors.CYAN)}")
        for key, (code, name) in project_types.items():
            print(f"  {key}. {name}")
        
        while True:
            choice = input(f"{colorize('Ваш выбор (1-8):', Colors.CYAN)} ").strip()
            if choice in project_types:
                self.project_type = project_types[choice][0]
                break
            print(f"{colorize('❌ Выберите число от 1 до 8', Colors.RED)}")
        
        # Масштаб проекта
        scales = {
            "1": ("minimal", "Минимальный (базовый мониторинг)"),
            "2": ("standard", "Стандартный (мониторинг + алерты)"),
            "3": ("advanced", "Продвинутый (+ ИИ оптимизация)"),
            "4": ("enterprise", "Корпоративный (полный функционал)")
        }
        
        print(f"\n{colorize('Выберите масштаб проекта:', Colors.CYAN)}")
        for key, (code, name) in scales.items():
            print(f"  {key}. {name}")
        
        while True:
            choice = input(f"{colorize('Ваш выбор (1-4):', Colors.CYAN)} ").strip()
            if choice in scales:
                self.project_scale = scales[choice][0]
                break
            print(f"{colorize('❌ Выберите число от 1 до 4', Colors.RED)}")
        
        # Директория установки
        default_dir = os.path.join(os.getcwd(), self.project_name)
        install_dir = input(f"{colorize('Директория установки', Colors.CYAN)} [{default_dir}]: ").strip()
        self.installation_dir = Path(install_dir) if install_dir else Path(default_dir)
        
        # Дополнительные опции
        print(f"\n{colorize('Дополнительные опции:', Colors.CYAN)}")
        
        self.config["create_venv"] = self._ask_yes_no(
            "Создать виртуальное окружение?", True
        )
        
        self.config["install_dependencies"] = self._ask_yes_no(
            "Установить зависимости автоматически?", True
        )
        
        self.config["initialize_git"] = self._ask_yes_no(
            "Инициализировать Git репозиторий?", True
        )
        
        self.config["create_example"] = self._ask_yes_no(
            "Создать пример кода для начала работы?", True
        )
        
        self.config["run_tests"] = self._ask_yes_no(
            "Запустить тесты после установки?", False
        )
    
    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Задать вопрос да/нет"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} [{default_str}]: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'да', 'д']
    
    def create_project_structure(self):
        """Создание структуры проекта"""
        print(f"\n{colorize('🏗️ Создание структуры проекта...', Colors.BLUE)}")
        
        # Создание основной директории
        self.installation_dir.mkdir(parents=True, exist_ok=True)
        print(f"{colorize('✅ Создана директория:', Colors.GREEN)} {self.installation_dir}")
        
        # Использование готового генератора шаблонов
        try:
            # Импорт модуля генерации (если доступен)
            sys.path.append(str(Path(__file__).parent))
            from project_templates import create_project_from_template
            
            # Генерация проекта
            project_path = create_project_from_template(
                self.project_name,
                self.project_type,
                self.project_scale
            )
            
            # Перемещение в нужную директорию
            generated_path = Path(project_path)
            if generated_path.exists() and generated_path != self.installation_dir:
                # Копирование файлов
                for item in generated_path.rglob("*"):
                    if item.is_file():
                        relative_path = item.relative_to(generated_path)
                        target_path = self.installation_dir / relative_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_path)
                
                # Удаление временной директории
                shutil.rmtree(generated_path, ignore_errors=True)
            
            print(f"{colorize('✅ Структура проекта создана', Colors.GREEN)}")
            
        except ImportError:
            # Fallback: создание базовой структуры
            self._create_basic_structure()
    
    def _create_basic_structure(self):
        """Создание базовой структуры проекта (fallback)"""
        basic_structure = {
            "monitoring": ["__init__.py"],
            "reports": ["__init__.py"],
            "recommendations": ["__init__.py"],
            "autonomous": ["__init__.py"],
            "config": ["framework_config.json"],
            "logs": [".gitkeep"],
            "tests": ["__init__.py"]
        }
        
        for directory, files in basic_structure.items():
            dir_path = self.installation_dir / directory
            dir_path.mkdir(exist_ok=True)
            
            for file_name in files:
                file_path = dir_path / file_name
                if file_name == ".gitkeep":
                    file_path.touch()
                elif file_name.endswith(".py"):
                    file_path.write_text(f'"""{directory} package"""')
                elif file_name.endswith(".json"):
                    file_path.write_text('{}')
        
        print(f"{colorize('✅ Базовая структура создана', Colors.GREEN)}")
    
    def setup_virtual_environment(self):
        """Настройка виртуального окружения"""
        if not self.config["create_venv"]:
            return
        
        print(f"\n{colorize('🐍 Создание виртуального окружения...', Colors.BLUE)}")
        
        venv_path = self.installation_dir / "venv"
        
        try:
            # Создание venv
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True, cwd=self.installation_dir)
            
            print(f"{colorize('✅ Виртуальное окружение создано', Colors.GREEN)}")
            
            # Обновление pip в venv
            if self.system_info["os"] == "Windows":
                pip_executable = venv_path / "Scripts" / "pip.exe"
                python_executable = venv_path / "Scripts" / "python.exe"
            else:
                pip_executable = venv_path / "bin" / "pip"
                python_executable = venv_path / "bin" / "python"
            
            subprocess.run([
                str(pip_executable), "install", "--upgrade", "pip"
            ], check=True, cwd=self.installation_dir)
            
            print(f"{colorize('✅ pip обновлен в виртуальном окружении', Colors.GREEN)}")
            
            # Сохранение путей для дальнейшего использования
            self.venv_python = str(python_executable)
            self.venv_pip = str(pip_executable)
            
        except subprocess.CalledProcessError as e:
            print(f"{colorize('❌ Ошибка создания виртуального окружения:', Colors.RED)} {e}")
            print(f"{colorize('Продолжаем с системным Python...', Colors.YELLOW)}")
            self.venv_python = sys.executable
            self.venv_pip = sys.executable + " -m pip"
    
    def install_dependencies(self):
        """Установка зависимостей"""
        if not self.config["install_dependencies"]:
            return
        
        print(f"\n{colorize('📦 Установка зависимостей...', Colors.BLUE)}")
        
        # Основные зависимости фреймворка
        framework_deps = [
            "aiosqlite>=0.19.0",
            "numpy>=1.24.0",
            "scikit-learn>=1.3.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "jinja2>=3.1.0",
            "schedule>=1.2.0",
            "jsonschema>=4.17.0"
        ]
        
        # Дополнительные зависимости по типу проекта
        project_deps = {
            "telegram_bot": [
                "aiogram>=3.2.0",
                "python-dotenv>=1.0.0",
                "aiohttp>=3.9.0"
            ],
            "web_api": [
                "fastapi>=0.104.0",
                "uvicorn>=0.24.0",
                "pydantic>=2.0.0",
                "httpx>=0.25.0"
            ],
            "cli_tool": [
                "click>=8.1.0",
                "rich>=13.0.0",
                "typer>=0.9.0"
            ],
            "ml_service": [
                "torch>=2.0.0",
                "transformers>=4.30.0",
                "mlflow>=2.8.0",
                "pandas>=2.0.0"
            ]
        }
        
        all_deps = framework_deps + project_deps.get(self.project_type, [])
        
        try:
            # Определение команды pip
            pip_cmd = self.venv_pip if hasattr(self, 'venv_pip') else [sys.executable, "-m", "pip"]
            if isinstance(pip_cmd, str):
                pip_cmd = pip_cmd.split()
            
            # Установка зависимостей
            for dep in all_deps:
                print(f"  Установка {dep}...")
                subprocess.run(
                    pip_cmd + ["install", dep],
                    check=True,
                    capture_output=True,
                    cwd=self.installation_dir
                )
            
            print(f"{colorize('✅ Зависимости установлены', Colors.GREEN)}")
            
        except subprocess.CalledProcessError as e:
            print(f"{colorize('❌ Ошибка установки зависимостей:', Colors.RED)} {e}")
            print(f"{colorize('Попробуйте установить вручную:', Colors.YELLOW)}")
            print(f"cd {self.installation_dir}")
            print("pip install -r requirements.txt")
    
    def initialize_git(self):
        """Инициализация Git репозитория"""
        if not self.config["initialize_git"]:
            return
        
        print(f"\n{colorize('📚 Инициализация Git репозитория...', Colors.BLUE)}")
        
        try:
            # Инициализация git
            subprocess.run(["git", "init"], check=True, 
                         capture_output=True, cwd=self.installation_dir)
            
            # Добавление файлов
            subprocess.run(["git", "add", "."], check=True,
                         capture_output=True, cwd=self.installation_dir)
            
            # Первый коммит
            subprocess.run([
                "git", "commit", "-m", f"Initial commit: {self.project_name} with Claude MultiAgent Framework"
            ], check=True, capture_output=True, cwd=self.installation_dir)
            
            print(f"{colorize('✅ Git репозиторий инициализирован', Colors.GREEN)}")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{colorize('⚠️ Git недоступен, пропускаем...', Colors.YELLOW)}")
    
    def create_example_code(self):
        """Создание примера кода"""
        if not self.config["create_example"]:
            return
        
        print(f"\n{colorize('📝 Создание примера кода...', Colors.BLUE)}")
        
        example_file = self.installation_dir / "example.py"
        
        example_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования {self.project_name}
Создан Claude MultiAgent Framework Installer
"""

from framework_init import initialize_framework

def main():
    """Основная функция примера"""
    print("🚀 Запуск {self.project_name}")
    
    # Инициализация фреймворка
    if initialize_framework("{self.project_type}"):
        print("✅ Фреймворк инициализирован успешно!")
        
        # Пример использования мониторинга
        try:
            from monitoring.mcp_monitor import track_mcp_call
            
            @track_mcp_call("example_agent", "example_server")
            def example_function():
                print("🔧 Выполняется функция с мониторингом...")
                return "Успех!"
            
            result = example_function()
            print(f"📊 Результат: {{result}}")
            
        except ImportError:
            print("ℹ️ Мониторинг будет доступен после полной настройки")
    
    else:
        print("❌ Ошибка инициализации фреймворка")

if __name__ == "__main__":
    main()
'''
        
        example_file.write_text(example_code)
        print(f"{colorize('✅ Пример создан:', Colors.GREEN)} example.py")
    
    def run_tests(self):
        """Запуск тестов"""
        if not self.config["run_tests"]:
            return
        
        print(f"\n{colorize('🧪 Запуск тестов...', Colors.BLUE)}")
        
        try:
            python_cmd = self.venv_python if hasattr(self, 'venv_python') else sys.executable
            
            # Проверка импорта фреймворка
            subprocess.run([
                python_cmd, "-c", "import framework_init; print('✅ Framework import OK')"
            ], check=True, cwd=self.installation_dir)
            
            # Запуск example.py
            example_file = self.installation_dir / "example.py"
            if example_file.exists():
                subprocess.run([
                    python_cmd, "example.py"
                ], check=True, cwd=self.installation_dir)
            
            print(f"{colorize('✅ Тесты прошли успешно', Colors.GREEN)}")
            
        except subprocess.CalledProcessError as e:
            print(f"{colorize('⚠️ Обнаружены проблемы:', Colors.YELLOW)} {e}")
            print(f"{colorize('Проект установлен, но требуется дополнительная настройка', Colors.YELLOW)}")
    
    def print_completion_info(self):
        """Отображение информации о завершении установки"""
        print(f"\n{colorize('🎉 Установка завершена!', Colors.GREEN + Colors.BOLD)}")
        print(f"{colorize('='*50, Colors.CYAN)}")
        
        print(f"\n{colorize('📁 Проект создан в:', Colors.CYAN)} {self.installation_dir}")
        print(f"{colorize('🏷️ Тип проекта:', Colors.CYAN)} {self.project_type}")
        print(f"{colorize('📊 Масштаб:', Colors.CYAN)} {self.project_scale}")
        
        print(f"\n{colorize('🚀 Для начала работы:', Colors.YELLOW)}")
        print(f"cd {self.installation_dir}")
        
        if self.config["create_venv"]:
            if self.system_info["os"] == "Windows":
                print("venv\\Scripts\\activate")
            else:
                print("source venv/bin/activate")
        
        if self.config["create_example"]:
            print("python example.py")
        
        print(f"\n{colorize('📚 Полезные команды:', Colors.YELLOW)}")
        print("python framework_init.py  # Инициализация фреймворка")
        print("python -m monitoring.mcp_monitor  # Запуск мониторинга")
        
        if self.project_type == "web_api":
            print("uvicorn app.main:app --reload  # Запуск API")
        elif self.project_type == "telegram_bot":
            print("python bot/main.py  # Запуск бота")
        
        print(f"\n{colorize('💡 Документация:', Colors.CYAN)} docs/usage_guide.md")
        print(f"{colorize('🐛 Поддержка:', Colors.CYAN)} https://github.com/claude-multiagent-framework")
        
        print(f"\n{colorize('Удачной разработки! 🤖', Colors.GREEN + Colors.BOLD)}")
    
    def install(self):
        """Основной процесс установки"""
        self.print_banner()
        
        if not self.check_prerequisites():
            print(f"\n{colorize('❌ Установка прервана из-за неудовлетворенных требований', Colors.RED)}")
            return False
        
        if self.install_mode == "interactive":
            self.interactive_setup()
        
        # Основные этапы установки
        try:
            self.create_project_structure()
            self.setup_virtual_environment()
            self.install_dependencies()
            self.initialize_git()
            self.create_example_code()
            self.run_tests()
            
            self.print_completion_info()
            return True
            
        except KeyboardInterrupt:
            print(f"\n{colorize('⚠️ Установка прервана пользователем', Colors.YELLOW)}")
            return False
        except Exception as e:
            print(f"\n{colorize('❌ Ошибка установки:', Colors.RED)} {e}")
            return False

def main():
    """Главная функция инсталлятора"""
    parser = argparse.ArgumentParser(description="Claude MultiAgent Framework Installer")
    parser.add_argument("--name", help="Имя проекта")
    parser.add_argument("--type", choices=[
        "telegram_bot", "web_api", "cli_tool", "data_pipeline",
        "microservice", "ml_service", "desktop_app", "iot_device"
    ], help="Тип проекта")
    parser.add_argument("--scale", choices=["minimal", "standard", "advanced", "enterprise"], 
                       help="Масштаб проекта")
    parser.add_argument("--dir", help="Директория установки")
    parser.add_argument("--silent", action="store_true", help="Тихая установка")
    parser.add_argument("--no-venv", action="store_true", help="Не создавать виртуальное окружение")
    parser.add_argument("--no-deps", action="store_true", help="Не устанавливать зависимости")
    parser.add_argument("--no-git", action="store_true", help="Не инициализировать Git")
    
    args = parser.parse_args()
    
    installer = FrameworkInstaller()
    
    # Настройка из аргументов командной строки
    if args.silent:
        installer.install_mode = "silent"
        
        # Проверка обязательных параметров для тихой установки
        if not all([args.name, args.type, args.scale]):
            print(f"{colorize('❌ Для тихой установки требуются параметры: --name, --type, --scale', Colors.RED)}")
            return 1
        
        installer.project_name = args.name
        installer.project_type = args.type
        installer.project_scale = args.scale
        installer.installation_dir = Path(args.dir) if args.dir else Path(os.getcwd()) / args.name
    
    # Применение опций
    if args.no_venv:
        installer.config["create_venv"] = False
    if args.no_deps:
        installer.config["install_dependencies"] = False
    if args.no_git:
        installer.config["initialize_git"] = False
    
    # Запуск установки
    success = installer.install()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())