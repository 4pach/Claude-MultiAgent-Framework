#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Templates - Шаблоны проектов для Claude MultiAgent Framework
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
import subprocess

from config_profiles import ProjectType, ConfigProfileManager, get_config_for_project

@dataclass
class ProjectTemplate:
    """Шаблон проекта"""
    name: str
    project_type: ProjectType
    description: str
    structure: Dict[str, List[str]]
    dependencies: List[str]
    dev_dependencies: List[str]
    setup_commands: List[str]
    example_code: Dict[str, str]
    documentation: Dict[str, str]

class ProjectTemplateGenerator:
    """Генератор шаблонов проектов"""
    
    def __init__(self, framework_source: str):
        self.framework_source = Path(framework_source)
        self.templates_dir = Path("project_templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Инициализация шаблонов
        self.templates = self._init_project_templates()
        
        # Менеджер профилей
        self.profile_manager = ConfigProfileManager()
    
    def _init_project_templates(self) -> Dict[str, ProjectTemplate]:
        """Инициализация шаблонов проектов"""
        templates = {}
        
        # ===== TELEGRAM BOT TEMPLATE =====
        templates["telegram_bot"] = ProjectTemplate(
            name="Telegram Bot с Claude MultiAgent Framework",
            project_type=ProjectType.TELEGRAM_BOT,
            description="Telegram бот с полным мониторингом и оптимизацией",
            structure={
                "bot/": ["main.py", "handlers.py", "keyboards.py", "states.py"],
                "bot/handlers/": ["start.py", "help.py", "settings.py"],
                "bot/middlewares/": ["monitoring.py", "error_handler.py"],
                "services/": ["user_service.py", "message_service.py"],
                "config/": ["bot_config.py", "framework_config.json"],
                "monitoring/": [],  # Копируется из фреймворка
                "autonomous/": [],  # Копируется из фреймворка
                "reports/": [],     # Копируется из фреймворка
                "locales/": ["ru.json", "en.json"],
                "tests/": ["test_handlers.py", "test_services.py"]
            },
            dependencies=[
                "aiogram>=3.2.0",
                "python-dotenv>=1.0.0",
                "aiosqlite>=0.19.0",
                "asyncpg>=0.28.0",
                "redis>=5.0.0",
                "aiohttp>=3.9.0"
            ],
            dev_dependencies=[
                "pytest>=7.4.0",
                "pytest-asyncio>=0.21.0",
                "black>=23.0.0",
                "flake8>=6.0.0",
                "mypy>=1.0.0"
            ],
            setup_commands=[
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                "python framework_init.py",
                "cp .env.example .env"
            ],
            example_code={
                "bot/main.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный модуль Telegram бота с Claude MultiAgent Framework
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.bot_config import BOT_TOKEN
from framework_init import initialize_framework
from bot.middlewares.monitoring import MonitoringMiddleware
from bot.handlers import start, help, settings

# Инициализация логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    
    # Инициализация Claude MultiAgent Framework
    if not initialize_framework("telegram_bot"):
        logger.error("Ошибка инициализации фреймворка")
        return
    
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключение middleware мониторинга
    dp.message.middleware(MonitoringMiddleware())
    
    # Регистрация хендлеров
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(settings.router)
    
    logger.info("🤖 Бот запущен с Claude MultiAgent Framework")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
''',
                "bot/middlewares/monitoring.py": '''# -*- coding: utf-8 -*-
"""
Middleware для интеграции с системой мониторинга
"""

from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
from aiogram.types import TelegramObject

from monitoring.mcp_monitor import mcp_monitor

class MonitoringMiddleware(BaseMiddleware):
    """Middleware для отслеживания всех запросов"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Логирование начала обработки
        agent = "telegram_bot"
        mcp_server = f"handler_{handler.__name__}"
        query = str(event)[:100]  # Первые 100 символов события
        
        request_id = mcp_monitor.log_request(agent, mcp_server, query)
        
        try:
            # Вызов хендлера
            result = await handler(event, data)
            
            # Логирование успешного результата
            mcp_monitor.log_response(
                request_id, 
                success=True,
                response_time=0.1,  # TODO: Замерить реальное время
                tokens_used=0,
                response_size=len(str(result))
            )
            
            return result
            
        except Exception as e:
            # Логирование ошибки
            mcp_monitor.log_response(
                request_id,
                success=False,
                response_time=0.1,
                tokens_used=0,
                response_size=0,
                error_message=str(e)
            )
            raise
'''
            },
            documentation={
                "README.md": """# Telegram Bot с Claude MultiAgent Framework

## Описание

Telegram бот с встроенной системой мониторинга, автоматической оптимизации и ИИ-анализом производительности.

## Возможности

- 🔍 Полный мониторинг всех хендлеров и middleware
- 🚨 Автоматические алерты при проблемах
- 📊 Ежедневные отчеты о работе бота
- 🤖 ИИ-рекомендации по оптимизации
- ⚡ Автоматическое кэширование частых запросов

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate     # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте переменные окружения:
   ```bash
   cp .env.example .env
   # Отредактируйте .env и добавьте BOT_TOKEN
   ```

5. Инициализируйте фреймворк:
   ```bash
   python framework_init.py
   ```

6. Запустите бота:
   ```bash
   python bot/main.py
   ```

## Мониторинг

Система автоматически отслеживает:
- Время обработки каждого сообщения
- Количество ошибок
- Использование памяти
- Скорость ответов API

Отчеты генерируются ежедневно в `reports/generated/`.

## Оптимизация

Фреймворк автоматически оптимизирует:
- Кэширование частых запросов
- Батчинг API вызовов
- Управление соединениями

## Разработка

Для запуска тестов:
```bash
pytest tests/
```

Для проверки кода:
```bash
flake8 bot/
mypy bot/
```
"""
            }
        )
        
        # ===== WEB API TEMPLATE =====
        templates["web_api"] = ProjectTemplate(
            name="Web API с Claude MultiAgent Framework",
            project_type=ProjectType.WEB_API,
            description="RESTful API с мониторингом производительности",
            structure={
                "app/": ["main.py", "config.py", "dependencies.py"],
                "app/api/": ["__init__.py", "endpoints.py"],
                "app/api/v1/": ["users.py", "auth.py", "health.py"],
                "app/core/": ["security.py", "database.py", "monitoring.py"],
                "app/models/": ["user.py", "token.py"],
                "app/services/": ["user_service.py", "auth_service.py"],
                "app/middleware/": ["monitoring.py", "error_handler.py", "rate_limiter.py"],
                "monitoring/": [],  # Копируется из фреймворка
                "reports/": [],     # Копируется из фреймворка
                "config/": ["api_config.py", "framework_config.json"],
                "tests/": ["test_api.py", "test_services.py"],
                "scripts/": ["migrate.py", "seed.py"]
            },
            dependencies=[
                "fastapi>=0.104.0",
                "uvicorn>=0.24.0",
                "pydantic>=2.0.0",
                "sqlalchemy>=2.0.0",
                "alembic>=1.12.0",
                "python-jose>=3.3.0",
                "passlib>=1.7.4",
                "python-multipart>=0.0.6",
                "httpx>=0.25.0",
                "redis>=5.0.0"
            ],
            dev_dependencies=[
                "pytest>=7.4.0",
                "pytest-asyncio>=0.21.0",
                "httpx>=0.25.0",
                "black>=23.0.0",
                "flake8>=6.0.0",
                "mypy>=1.0.0",
                "coverage>=7.0.0"
            ],
            setup_commands=[
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                "python framework_init.py",
                "alembic init alembic",
                "alembic revision --autogenerate -m 'Initial migration'",
                "alembic upgrade head"
            ],
            example_code={
                "app/main.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI приложение с Claude MultiAgent Framework
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import users, auth, health
from app.middleware.monitoring import MonitoringMiddleware
from app.core.database import engine, Base
from framework_init import initialize_framework

# Инициализация Claude MultiAgent Framework
initialize_framework("web_api")

# Создание FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Middleware
app.add_middleware(MonitoringMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(health.router, prefix=f"{settings.API_V1_STR}/health", tags=["health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    # Создание таблиц БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке"""
    await engine.dispose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                "app/middleware/monitoring.py": '''# -*- coding: utf-8 -*-
"""
Middleware для мониторинга API запросов
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from monitoring.mcp_monitor import mcp_monitor
from monitoring.performance_tracker import performance_tracker

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware для отслеживания производительности API"""
    
    async def dispatch(self, request: Request, call_next):
        # Начало замера времени
        start_time = time.time()
        
        # Логирование запроса
        agent = "web_api"
        mcp_server = f"{request.method}_{request.url.path}"
        query = f"{request.method} {request.url}"
        
        request_id = mcp_monitor.log_request(agent, mcp_server, query)
        
        try:
            # Обработка запроса
            response = await call_next(request)
            
            # Расчет времени выполнения
            process_time = time.time() - start_time
            
            # Логирование успешного ответа
            mcp_monitor.log_response(
                request_id,
                success=response.status_code < 400,
                response_time=process_time,
                tokens_used=0,
                response_size=int(response.headers.get("content-length", 0))
            )
            
            # Запись метрик производительности
            performance_tracker.record_performance(
                agent=agent,
                mcp_server=mcp_server,
                query=query,
                response_time=process_time,
                tokens_used=0,
                success=response.status_code < 400
            )
            
            # Добавление заголовков
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Логирование ошибки
            mcp_monitor.log_response(
                request_id,
                success=False,
                response_time=process_time,
                tokens_used=0,
                response_size=0,
                error_message=str(e)
            )
            
            raise
'''
            },
            documentation={
                "README.md": """# Web API с Claude MultiAgent Framework

## Описание

RESTful API на FastAPI с встроенным мониторингом производительности, автоматической оптимизацией и ИИ-анализом.

## Возможности

- 🚀 Высокопроизводительный API на FastAPI
- 🔍 Полный мониторинг всех endpoints
- 📊 Автоматические отчеты производительности
- 🤖 ИИ-оптимизация запросов к БД
- ⚡ Интеллектуальное кэширование
- 🔒 Встроенная аутентификация JWT

## API Endpoints

- `GET /api/v1/health` - Проверка состояния
- `POST /api/v1/auth/login` - Аутентификация
- `GET /api/v1/users` - Список пользователей
- `GET /api/v1/users/{id}` - Информация о пользователе

## Мониторинг

Автоматически отслеживается:
- Время ответа каждого endpoint
- Статус коды ответов
- Размер запросов и ответов
- Частота ошибок
- Нагрузка на БД

## Производительность

Фреймворк автоматически оптимизирует:
- Кэширование частых запросов
- Пулы соединений с БД
- Сжатие ответов
- Батчинг запросов
"""
            }
        )
        
        # ===== CLI TOOL TEMPLATE =====
        templates["cli_tool"] = ProjectTemplate(
            name="CLI Tool с Claude MultiAgent Framework",
            project_type=ProjectType.CLI_TOOL,
            description="Консольная утилита с мониторингом выполнения",
            structure={
                "cli/": ["main.py", "commands.py", "utils.py"],
                "cli/commands/": ["init.py", "run.py", "report.py"],
                "monitoring/": [],  # Копируется из фреймворка
                "config/": ["cli_config.py", "framework_config.json"],
                "tests/": ["test_commands.py", "test_utils.py"]
            },
            dependencies=[
                "click>=8.1.0",
                "rich>=13.0.0",
                "typer>=0.9.0",
                "python-dotenv>=1.0.0"
            ],
            dev_dependencies=[
                "pytest>=7.4.0",
                "black>=23.0.0",
                "flake8>=6.0.0",
                "mypy>=1.0.0"
            ],
            setup_commands=[
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                "pip install -e .",
                "python framework_init.py"
            ],
            example_code={
                "cli/main.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI приложение с Claude MultiAgent Framework
"""

import typer
from rich.console import Console
from rich.table import Table

from framework_init import initialize_framework
from monitoring.mcp_monitor import track_mcp_call
from cli.commands import init, run, report

# Инициализация
app = typer.Typer()
console = Console()

# Инициализация фреймворка
initialize_framework("cli_tool")

@app.command()
@track_mcp_call("cli_tool", "init_command")
def init(name: str = typer.Argument(..., help="Имя проекта")):
    """Инициализация нового проекта"""
    console.print(f"[green]Инициализация проекта: {name}[/green]")
    # Логика инициализации
    console.print("✅ Проект создан!")

@app.command()
@track_mcp_call("cli_tool", "run_command")  
def run(
    script: str = typer.Argument(..., help="Скрипт для выполнения"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Подробный вывод")
):
    """Запуск скрипта с мониторингом"""
    if verbose:
        console.print(f"[blue]Запуск скрипта: {script}[/blue]")
    
    # Выполнение скрипта
    console.print("🚀 Выполнение...")
    
@app.command()
def status():
    """Показать статус мониторинга"""
    from monitoring.performance_tracker import performance_tracker
    
    # Получение статистики
    stats = performance_tracker.get_overall_statistics()
    
    # Создание таблицы
    table = Table(title="Статистика выполнения")
    table.add_column("Метрика", style="cyan")
    table.add_column("Значение", style="green")
    
    table.add_row("Всего команд", str(stats.get("total_requests", 0)))
    table.add_row("Успешных", str(stats.get("successful_requests", 0)))
    table.add_row("Среднее время", f"{stats.get('avg_response_time', 0):.2f}s")
    
    console.print(table)

if __name__ == "__main__":
    app()
'''
            },
            documentation={
                "README.md": """# CLI Tool с Claude MultiAgent Framework

## Описание

Консольная утилита с встроенным мониторингом выполнения команд.

## Возможности

- 🎯 Отслеживание выполнения каждой команды
- 📊 Статистика использования
- 🚨 Уведомления об ошибках
- 📈 Отчеты о производительности

## Использование

```bash
# Инициализация проекта
mycli init myproject

# Запуск с мониторингом
mycli run script.py --verbose

# Просмотр статистики
mycli status
```
"""
            }
        )
        
        # ===== ML SERVICE TEMPLATE =====
        templates["ml_service"] = ProjectTemplate(
            name="ML Service с Claude MultiAgent Framework",
            project_type=ProjectType.ML_SERVICE,
            description="Сервис машинного обучения с мониторингом моделей",
            structure={
                "ml_service/": ["app.py", "config.py"],
                "ml_service/models/": ["base_model.py", "predictor.py", "trainer.py"],
                "ml_service/api/": ["inference.py", "training.py", "monitoring.py"],
                "ml_service/data/": ["preprocessor.py", "validator.py"],
                "ml_service/monitoring/": ["model_monitor.py", "drift_detector.py"],
                "monitoring/": [],  # Копируется из фреймворка
                "autonomous/": [],  # Копируется из фреймворка
                "models/": ["model_v1.pkl"],
                "data/": ["sample_data.csv"],
                "notebooks/": ["exploration.ipynb", "training.ipynb"],
                "tests/": ["test_models.py", "test_api.py"]
            },
            dependencies=[
                "fastapi>=0.104.0",
                "uvicorn>=0.24.0",
                "scikit-learn>=1.3.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
                "torch>=2.0.0",
                "transformers>=4.30.0",
                "mlflow>=2.8.0",
                "evidently>=0.4.0"
            ],
            dev_dependencies=[
                "jupyter>=1.0.0",
                "pytest>=7.4.0",
                "black>=23.0.0",
                "flake8>=6.0.0"
            ],
            setup_commands=[
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                "python framework_init.py",
                "mlflow ui --port 5000 &"
            ],
            example_code={
                "ml_service/monitoring/model_monitor.py": '''# -*- coding: utf-8 -*-
"""
Мониторинг ML моделей с Claude MultiAgent Framework
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime

from monitoring.mcp_monitor import mcp_monitor
from monitoring.performance_tracker import performance_tracker
from recommendations.optimizer_ai import optimizer_ai

class ModelMonitor:
    """Мониторинг производительности ML моделей"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.predictions_buffer = []
        self.ground_truth_buffer = []
    
    def track_prediction(self, 
                        input_data: np.ndarray,
                        prediction: Any,
                        model_version: str,
                        inference_time: float):
        """Отслеживание предсказания модели"""
        
        # Логирование в MCP Monitor
        request_id = mcp_monitor.log_request(
            agent=f"ml_model_{self.model_name}",
            mcp_server=f"inference_v{model_version}",
            query=f"shape={input_data.shape}"
        )
        
        mcp_monitor.log_response(
            request_id=request_id,
            success=True,
            response_time=inference_time,
            tokens_used=int(np.prod(input_data.shape)),  # Размер входных данных
            response_size=1
        )
        
        # Запись метрик производительности
        performance_tracker.record_performance(
            agent=f"ml_model_{self.model_name}",
            mcp_server=f"inference_v{model_version}",
            query="prediction",
            response_time=inference_time,
            tokens_used=int(np.prod(input_data.shape)),
            success=True
        )
        
        # Сохранение для анализа дрейфа
        self.predictions_buffer.append({
            "timestamp": datetime.now(),
            "prediction": prediction,
            "inference_time": inference_time,
            "input_shape": input_data.shape
        })
        
        # Периодический анализ
        if len(self.predictions_buffer) >= 100:
            self._analyze_model_performance()
    
    def _analyze_model_performance(self):
        """Анализ производительности модели"""
        # Получение рекомендаций от ИИ
        recommendations = optimizer_ai.generate_model_recommendations(
            model_name=self.model_name,
            predictions=self.predictions_buffer
        )
        
        if recommendations:
            print(f"🤖 Рекомендации для модели {self.model_name}:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        # Очистка буфера
        self.predictions_buffer = self.predictions_buffer[-50:]
    
    def track_accuracy(self, predictions: List[Any], ground_truth: List[Any]):
        """Отслеживание точности модели"""
        accuracy = sum(p == gt for p, gt in zip(predictions, ground_truth)) / len(predictions)
        
        # Алерт при падении точности
        if accuracy < 0.8:  # Порог из конфигурации
            from monitoring.alert_system import alert_system
            alert_system.send_alert(
                severity="HIGH",
                title=f"Падение точности модели {self.model_name}",
                message=f"Точность упала до {accuracy:.2%}"
            )
'''
            },
            documentation={
                "README.md": """# ML Service с Claude MultiAgent Framework

## Описание

Сервис машинного обучения с полным мониторингом моделей, отслеживанием дрейфа данных и автоматической оптимизацией.

## Возможности

- 🤖 Мониторинг inference времени
- 📊 Отслеживание точности моделей
- 🎯 Детекция дрейфа данных
- 📈 A/B тестирование моделей
- ⚡ Автоматическая оптимизация
- 🔍 Explainability метрики

## API

- `POST /predict` - Получить предсказание
- `GET /model/metrics` - Метрики модели
- `POST /model/feedback` - Обратная связь
- `GET /model/drift` - Статус дрейфа

## Мониторинг моделей

Автоматически отслеживается:
- Время inference
- Использование GPU/CPU
- Точность предсказаний
- Дрейф входных данных
- Распределение предсказаний
"""
            }
        )
        
        return templates
    
    def generate_project(self, project_name: str, project_type: str,
                        scale: str = "standard", output_dir: str = None) -> str:
        """Генерация проекта из шаблона"""
        if output_dir is None:
            output_dir = f"generated_projects/{project_name}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Получение шаблона
        template = self.templates.get(project_type)
        if not template:
            raise ValueError(f"Неизвестный тип проекта: {project_type}")
        
        print(f"🏗️ [Интегратор] Генерация проекта: {project_name}")
        print(f"   Тип: {project_type}")
        print(f"   Масштаб: {scale}")
        
        # Создание структуры директорий
        self._create_project_structure(output_path, template)
        
        # Копирование компонентов фреймворка
        self._copy_framework_components(output_path, project_type, scale)
        
        # Создание конфигурации
        self._create_project_config(output_path, project_name, project_type, scale)
        
        # Создание примеров кода
        self._create_example_code(output_path, template)
        
        # Создание документации
        self._create_documentation(output_path, template)
        
        # Создание файлов проекта
        self._create_project_files(output_path, template)
        
        print(f"✅ Проект создан: {output_path}")
        return str(output_path)
    
    def _create_project_structure(self, output_path: Path, template: ProjectTemplate):
        """Создание структуры директорий проекта"""
        for directory, files in template.structure.items():
            dir_path = output_path / directory.rstrip("/")
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Создание __init__.py для Python пакетов
            if directory.endswith("/") and not directory.startswith(("config/", "tests/", "scripts/", "data/", "models/", "notebooks/")):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("")
    
    def _copy_framework_components(self, output_path: Path, project_type: str, scale: str):
        """Копирование компонентов фреймворка"""
        # Получение конфигурации для типа проекта
        config = get_config_for_project(project_type, scale)
        
        if not config:
            return
        
        components = config.get("framework", {}).get("components", {})
        
        # Копирование включенных компонентов
        for component, enabled in components.items():
            if enabled:
                self._copy_component(component, output_path)
    
    def _copy_component(self, component_name: str, output_path: Path):
        """Копирование одного компонента фреймворка"""
        component_mappings = {
            "mcp_monitor": "monitoring/mcp_monitor.py",
            "performance_tracker": "monitoring/performance_tracker.py",
            "cache_manager": "monitoring/cache_manager.py",
            "alert_system": "monitoring/alert_system.py",
            "auto_reporter": "reports/auto_reporter.py",
            "optimizer_ai": "recommendations/optimizer_ai.py",
            "self_optimizer": "autonomous/self_optimizer.py",
            "approval_system": "autonomous/approval_system.py",
            "config_updater": "autonomous/config_updater.py"
        }
        
        if component_name in component_mappings:
            source_file = self.framework_source / component_mappings[component_name]
            if source_file.exists():
                target_file = output_path / component_mappings[component_name]
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
    
    def _create_project_config(self, output_path: Path, project_name: str,
                              project_type: str, scale: str):
        """Создание конфигурации проекта"""
        # Получение конфигурации из профиля
        config = get_config_for_project(project_type, scale)
        
        # Добавление метаданных проекта
        config["project"] = {
            "name": project_name,
            "type": project_type,
            "scale": scale,
            "created": "2025-07-11",
            "framework_version": "1.0.0"
        }
        
        # Сохранение конфигурации
        config_dir = output_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "framework_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _create_example_code(self, output_path: Path, template: ProjectTemplate):
        """Создание примеров кода"""
        for file_path, code in template.example_code.items():
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(code)
    
    def _create_documentation(self, output_path: Path, template: ProjectTemplate):
        """Создание документации"""
        for file_path, content in template.documentation.items():
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def _create_project_files(self, output_path: Path, template: ProjectTemplate):
        """Создание файлов проекта"""
        # requirements.txt
        requirements = template.dependencies + [
            "# Claude MultiAgent Framework",
            "aiosqlite>=0.19.0",
            "numpy>=1.24.0",
            "scikit-learn>=1.3.0",
            "matplotlib>=3.7.0",
            "jinja2>=3.1.0",
            "schedule>=1.2.0",
            "jsonschema>=4.17.0"
        ]
        
        req_file = output_path / "requirements.txt"
        req_file.write_text("\n".join(requirements))
        
        # requirements-dev.txt
        if template.dev_dependencies:
            dev_req_file = output_path / "requirements-dev.txt"
            dev_req_file.write_text("\n".join(template.dev_dependencies))
        
        # .env.example
        env_example = """# Environment variables
DEBUG=True
LOG_LEVEL=INFO

# API Keys (if needed)
API_KEY=your-api-key-here

# Database (if needed)
DATABASE_URL=sqlite:///./app.db

# Claude MultiAgent Framework
MONITORING_ENABLED=True
ALERTS_ENABLED=True
AI_OPTIMIZATION_ENABLED=True
"""
        (output_path / ".env.example").write_text(env_example)
        
        # .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
env/

# Environment
.env

# Claude MultiAgent Framework
monitoring/performance.db
monitoring/cache/
logs/
reports/generated/
autonomous/optimizations/
autonomous/config_backups/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.db
*.log
"""
        (output_path / ".gitignore").write_text(gitignore)
        
        # framework_init.py
        init_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Инициализация Claude MultiAgent Framework
"""

import json
from pathlib import Path

def initialize_framework(project_type: str = None) -> bool:
    """Инициализация фреймворка"""
    print("🚀 Инициализация Claude MultiAgent Framework...")
    
    # Загрузка конфигурации
    config_file = Path("config/framework_config.json")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"📋 Проект: {config['project']['name']}")
        print(f"🏷️ Тип: {config['project']['type']}")
        print(f"📊 Масштаб: {config['project']['scale']}")
        
        # Инициализация компонентов
        components = config.get('framework', {}).get('components', {})
        for component, enabled in components.items():
            if enabled:
                print(f"✅ {component}: активен")
        
        print("✅ Фреймворк инициализирован!")
        return True
    else:
        print("❌ Конфигурация не найдена")
        return False

if __name__ == "__main__":
    initialize_framework()
'''
        (output_path / "framework_init.py").write_text(init_script)

# Функция для быстрого создания проекта
def create_project_from_template(project_name: str, project_type: str,
                               scale: str = "standard") -> str:
    """Создание проекта из шаблона"""
    generator = ProjectTemplateGenerator("/home/dmin/projects/telegram_sticker_bot/telegram_sticker_bot")
    return generator.generate_project(project_name, project_type, scale)

if __name__ == "__main__":
    # Демонстрация создания проектов
    print("🚀 Демонстрация создания проектов из шаблонов\n")
    
    # Создание Telegram бота
    telegram_bot_path = create_project_from_template(
        "MyAwesomeBot",
        "telegram_bot",
        "advanced"
    )
    
    print(f"\n✅ Telegram бот создан: {telegram_bot_path}")
    
    # Создание Web API
    web_api_path = create_project_from_template(
        "MyAPI",
        "web_api", 
        "standard"
    )
    
    print(f"\n✅ Web API создан: {web_api_path}")