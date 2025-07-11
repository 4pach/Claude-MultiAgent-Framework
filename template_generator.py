#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Generator - Генератор универсального шаблона проекта
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from datetime import datetime

@dataclass
class TemplateConfig:
    """Конфигурация шаблона"""
    project_name: str
    project_type: str
    framework_components: List[str]
    custom_variables: Dict[str, Any]
    output_directory: str

class TemplateGenerator:
    """Генератор универсального шаблона проекта"""
    
    def __init__(self, source_project_root: str):
        self.source_root = Path(source_project_root)
        self.template_root = Path("universal_template")
        
        # Загрузка результатов анализа
        self.analysis_data = self.load_analysis()
        
        # Переменные для замены в шаблонах
        self.template_variables = {
            "{{PROJECT_NAME}}": "",
            "{{PROJECT_TYPE}}": "",
            "{{AUTHOR}}": "Claude MultiAgent System",
            "{{DATE}}": datetime.now().strftime("%Y-%m-%d"),
            "{{VERSION}}": "1.0.0"
        }
        
    def load_analysis(self) -> Dict:
        """Загрузка результатов анализа фреймворка"""
        analysis_file = self.source_root / "autonomous" / "framework_analysis.json"
        
        if not analysis_file.exists():
            raise FileNotFoundError("Файл анализа не найден. Запустите framework_analyzer.py")
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_universal_template(self, template_config: TemplateConfig):
        """Создание универсального шаблона"""
        print(f"🏗️ [Архитектор] Создание универсального шаблона: {template_config.project_name}")
        
        # Подготовка переменных шаблона
        self.template_variables.update({
            "{{PROJECT_NAME}}": template_config.project_name,
            "{{PROJECT_TYPE}}": template_config.project_type
        })
        self.template_variables.update(template_config.custom_variables)
        
        output_path = Path(template_config.output_directory)
        output_path.mkdir(exist_ok=True)
        
        # Создание базовой структуры
        self._create_base_structure(output_path, template_config)
        
        # Копирование основных компонентов
        self._copy_framework_components(output_path, template_config)
        
        # Создание конфигурационных файлов
        self._create_configuration_files(output_path, template_config)
        
        # Создание инициализационных скриптов
        self._create_initialization_scripts(output_path, template_config)
        
        # Создание документации
        self._create_documentation(output_path, template_config)
        
        # Создание примеров использования
        self._create_usage_examples(output_path, template_config)
        
        print(f"✅ [Архитектор] Шаблон создан: {output_path}")
        return output_path
    
    def _create_base_structure(self, output_path: Path, config: TemplateConfig):
        """Создание базовой структуры проекта"""
        project_structure = self.analysis_data["template_structure"]["project_types"][config.project_type]["project_structure"]
        
        # Создание директорий
        for directory, files in project_structure.items():
            dir_path = output_path / directory.rstrip("/")
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Создание файла __init__.py для Python пакетов
            if directory.endswith("/") and directory != "config/":
                init_file = dir_path / "__init__.py"
                init_file.write_text(f'"""\\n{directory.rstrip("/")} package - Часть {config.project_name}\\n"""')
        
        # Создание корневых файлов
        self._create_root_files(output_path, config)
    
    def _create_root_files(self, output_path: Path, config: TemplateConfig):
        """Создание корневых файлов проекта"""
        
        # .gitignore
        gitignore_content = """
# Python
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

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Claude MultiAgent Framework
monitoring/performance.db
monitoring/cache/
logs/
autonomous/optimizations/
autonomous/config_backups/
reports/generated/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        (output_path / ".gitignore").write_text(gitignore_content.strip())
        
        # requirements.txt
        requirements_content = """
# Claude MultiAgent Framework dependencies
aiosqlite>=0.19.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
jinja2>=3.1.0
schedule>=1.2.0
jsonschema>=4.17.0
"""
        (output_path / "requirements.txt").write_text(requirements_content.strip())
        
        # README.md
        readme_content = f"""
# {config.project_name}

Проект на основе **Claude MultiAgent Framework** - универсального фреймворка автономного мультиагентного мониторинга и оптимизации.

## Возможности

- 🔍 **Мониторинг производительности** - Отслеживание MCP запросов в реальном времени
- 🚨 **Система предупреждений** - Многоуровневые алерты с email уведомлениями
- 💾 **Интеллектуальное кэширование** - Автоматическая оптимизация запросов
- 📊 **Автоматические отчеты** - HTML отчеты с графиками и аналитикой
- 🤖 **ИИ-оптимизация** - ML-анализ паттернов и рекомендации
- ⚡ **Автономное самоулучшение** - Автоматическое применение оптимизаций

## Быстрый старт

1. **Установка зависимостей:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Инициализация фреймворка:**
   ```python
   from framework_init import initialize_framework
   initialize_framework('{config.project_type}')
   ```

3. **Интеграция с проектом:**
   ```python
   # Добавьте в ваш код
   from monitoring.mcp_monitor import track_mcp_call
   
   @track_mcp_call("my_agent", "mcp_server")
   def my_function():
       # Ваш код
       pass
   ```

## Архитектура

### 🧠 Мультиагентная система

Фреймворк использует специализированные виртуальные суб-агенты:

- **🧠 Архитектор** — Проектирует архитектуру и анализирует зависимости
- **🧪 Инженер** — Реализует код и выполняет тесты
- **📦 Интегратор** — Интегрирует с внешними API и сервисами
- **🛡️ Критик** — Оценивает риски и предлагает улучшения
- **🧭 Менеджер** — Отслеживает прогресс и координирует задачи

### 📁 Структура

```
{config.project_name}/
├── monitoring/          # Система мониторинга
├── reports/            # Автоматические отчеты
├── recommendations/    # ИИ-рекомендации
├── autonomous/         # Автономное самоулучшение
├── config/            # Конфигурация
└── examples/          # Примеры использования
```

## Конфигурация

Основные настройки в `config/framework_config.json`:

```json
{{
  "monitoring_enabled": true,
  "alerts_enabled": true,
  "cache_enabled": true,
  "ai_optimization_enabled": true
}}
```

## Лицензия

MIT License - см. LICENSE файл для подробностей.

---

🤖 *Сгенерировано Claude MultiAgent Framework*
"""
        (output_path / "README.md").write_text(readme_content.strip())
    
    def _copy_framework_components(self, output_path: Path, config: TemplateConfig):
        """Копирование компонентов фреймворка"""
        print("📦 [Интегратор] Копирование компонентов фреймворка...")
        
        # Получение списка компонентов для типа проекта
        project_template = self.analysis_data["template_structure"]["project_types"][config.project_type]
        required_components = project_template["required_components"]
        optional_components = project_template.get("optional_components", [])
        
        all_components = required_components + [c for c in optional_components if c in config.framework_components]
        
        # Копирование каждого компонента
        for component_name in all_components:
            self._copy_single_component(component_name, output_path)
    
    def _copy_single_component(self, component_name: str, output_path: Path):
        """Копирование одного компонента"""
        # Поиск компонента в анализе
        all_components = (self.analysis_data["framework_analysis"]["core_framework_components"] + 
                         self.analysis_data["framework_analysis"]["project_specific_components"])
        
        component_info = None
        for comp in all_components:
            if comp["name"] == component_name:
                component_info = comp
                break
        
        if not component_info:
            print(f"⚠️ Компонент {component_name} не найден")
            return
        
        # Копирование файла компонента
        source_path = self.source_root / component_info["path"]
        target_path = output_path / component_info["path"]
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        if source_path.exists():
            # Чтение и обработка содержимого
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Применение шаблонных переменных
            processed_content = self._process_template_variables(content)
            
            # Сохранение обработанного файла
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            print(f"✅ Скопирован: {component_info['path']}")
        else:
            print(f"❌ Файл не найден: {source_path}")
    
    def _process_template_variables(self, content: str) -> str:
        """Обработка переменных шаблона в содержимом файла"""
        processed_content = content
        
        for variable, value in self.template_variables.items():
            processed_content = processed_content.replace(variable, str(value))
        
        return processed_content
    
    def _create_configuration_files(self, output_path: Path, config: TemplateConfig):
        """Создание конфигурационных файлов"""
        print("⚙️ [Архитектор] Создание конфигурационных файлов...")
        
        config_dir = output_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Основная конфигурация фреймворка
        project_template = self.analysis_data["template_structure"]["project_types"][config.project_type]
        framework_config = {
            "project": {
                "name": config.project_name,
                "type": config.project_type,
                "version": "1.0.0",
                "created": datetime.now().isoformat()
            },
            "framework": project_template["config_params"],
            "custom": config.custom_variables
        }
        
        with open(config_dir / "framework_config.json", 'w', encoding='utf-8') as f:
            json.dump(framework_config, f, ensure_ascii=False, indent=2)
        
        # Конфигурация мониторинга
        monitoring_config = {
            "cache": {
                "max_size_mb": 100,
                "ttl_hours": 24,
                "cleanup_interval_minutes": 60
            },
            "performance": {
                "max_response_time": 10.0,
                "max_tokens_per_request": 1000,
                "tracking_enabled": True
            }
        }
        
        with open(config_dir / "monitoring_config.json", 'w', encoding='utf-8') as f:
            json.dump(monitoring_config, f, ensure_ascii=False, indent=2)
        
        # Конфигурация алертов
        alert_config = {
            "thresholds": {
                "max_response_time": 10.0,
                "max_tokens_per_request": 1000,
                "min_success_rate": 0.9,
                "max_failure_streak": 3
            },
            "notification": {
                "enabled": True,
                "console_output": True,
                "file_logging": True,
                "email_alerts": False
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": []
            }
        }
        
        with open(config_dir / "alert_config.json", 'w', encoding='utf-8') as f:
            json.dump(alert_config, f, ensure_ascii=False, indent=2)
    
    def _create_initialization_scripts(self, output_path: Path, config: TemplateConfig):
        """Создание скриптов инициализации"""
        print("🚀 [Инженер] Создание скриптов инициализации...")
        
        # Основной инициализационный скрипт
        init_script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Framework Initialization - Инициализация {config.project_name}
Основан на Claude MultiAgent Framework

Автор: {self.template_variables["{{AUTHOR}}"]}
Дата: {self.template_variables["{{DATE}}"]}
"""

import json
from pathlib import Path
from typing import Dict, Any

def load_framework_config() -> Dict[str, Any]:
    """Загрузка конфигурации фреймворка"""
    config_file = Path("config/framework_config.json")
    
    if not config_file.exists():
        raise FileNotFoundError("Конфигурационный файл не найден: config/framework_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_framework(project_type: str = "{config.project_type}") -> bool:
    """Инициализация Claude MultiAgent Framework"""
    print("🚀 Инициализация {config.project_name}...")
    
    try:
        # Загрузка конфигурации
        config = load_framework_config()
        print(f"📋 Проект: {{config['project']['name']}}")
        print(f"🏷️ Тип: {{config['project']['type']}}")
        
        # Инициализация компонентов в зависимости от типа проекта'''
        
        # Добавление инициализации компонентов
        project_template = self.analysis_data["template_structure"]["project_types"][config.project_type]
        required_components = project_template["required_components"]
        
        for component in required_components:
            init_script += f'''
        
        # Инициализация {component}
        try:
            print(f"🔧 Инициализация {component}...")
            # Здесь будет код инициализации компонента
            print(f"✅ {component} готов")
        except Exception as e:
            print(f"❌ Ошибка инициализации {component}: {{e}}")
            return False'''
        
        init_script += '''
        
        print("✅ Claude MultiAgent Framework инициализирован успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

def get_framework_status() -> Dict[str, Any]:
    """Получение статуса фреймворка"""
    return {
        "initialized": True,
        "components_active": [],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    initialize_framework()
'''
        
        (output_path / "framework_init.py").write_text(init_script)
    
    def _create_documentation(self, output_path: Path, config: TemplateConfig):
        """Создание документации"""
        print("📚 [Архитектор] Создание документации...")
        
        docs_dir = output_path / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Руководство по использованию
        usage_guide = f"""
# Руководство по использованию {config.project_name}

## Обзор

{config.project_name} создан на основе **Claude MultiAgent Framework** - универсального фреймворка для автономного мониторинга и оптимизации.

## Основные компоненты

### 🔍 Система мониторинга

Автоматическое отслеживание всех MCP вызовов:

```python
from monitoring.mcp_monitor import track_mcp_call

@track_mcp_call("agent_name", "mcp_server")
def my_function():
    # Ваш код
    pass
```

### 🚨 Система предупреждений

Настройка алертов через конфигурацию:

```json
{{
  "thresholds": {{
    "max_response_time": 10.0,
    "max_tokens_per_request": 1000
  }}
}}
```

### 📊 Автоматические отчеты

Генерация HTML отчетов с графиками:

```python
from reports.auto_reporter import auto_reporter

# Генерация ежедневного отчета
report_path = auto_reporter.generate_daily_report()
```

## Интеграция с проектом

1. **Импорт фреймворка:**
   ```python
   from framework_init import initialize_framework
   initialize_framework()
   ```

2. **Добавление мониторинга:**
   ```python
   from monitoring.mcp_monitor import mcp_monitor
   
   # Логирование MCP вызова
   mcp_monitor.log_request("agent", "server", "query")
   ```

3. **Использование кэша:**
   ```python
   from monitoring.cache_manager import cache_manager
   
   # Проверка кэша
   cached_result = cache_manager.get_cached_response("key")
   ```

## Конфигурация

Основные настройки в `config/framework_config.json`.

Для изменения параметров мониторинга:
- `monitoring_config.json` - настройки производительности
- `alert_config.json` - правила предупреждений

## Автономные возможности

Фреймворк может самостоятельно оптимизироваться:

```python
from autonomous.self_optimizer import self_optimizer

# Автоматическая оптимизация
self_optimizer.continuous_analysis()
```

## Поддержка

Для получения помощи обратитесь к документации Claude MultiAgent Framework.
"""
        
        (docs_dir / "usage_guide.md").write_text(usage_guide.strip())
        
        # API документация
        api_docs = """
# API Документация

## Основные модули

### monitoring.mcp_monitor

#### `track_mcp_call(agent: str, server: str)`
Декоратор для отслеживания MCP вызовов.

#### `log_request(agent: str, server: str, query: str) -> str`
Логирование запроса к MCP серверу.

### monitoring.performance_tracker

#### `record_performance(agent: str, server: str, **metrics)`
Запись метрик производительности.

### monitoring.alert_system

#### `check_metrics(agent: str, server: str, metrics: dict)`
Проверка метрик на превышение порогов.

### autonomous.self_optimizer

#### `continuous_analysis()`
Запуск непрерывного анализа для оптимизации.

## Примеры использования

См. директорию `examples/` для полных примеров.
"""
        
        (docs_dir / "api_reference.md").write_text(api_docs.strip())
    
    def _create_usage_examples(self, output_path: Path, config: TemplateConfig):
        """Создание примеров использования"""
        print("💡 [Инженер] Создание примеров использования...")
        
        examples_dir = output_path / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        # Базовый пример
        basic_example = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый пример использования {config.project_name}
"""

from framework_init import initialize_framework
from monitoring.mcp_monitor import track_mcp_call

def main():
    """Основная функция примера"""
    
    # Инициализация фреймворка
    if not initialize_framework():
        print("❌ Ошибка инициализации")
        return
    
    # Пример функции с мониторингом
    @track_mcp_call("example_agent", "example_server") 
    def example_function():
        print("🔧 Выполнение функции с мониторингом...")
        return "Success"
    
    # Вызов функции
    result = example_function()
    print(f"📊 Результат: {{result}}")

if __name__ == "__main__":
    main()
'''
        
        (examples_dir / "basic_usage.py").write_text(basic_example)
        
        # Пример с отчетами
        reports_example = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример генерации отчетов в {config.project_name}
"""

from framework_init import initialize_framework

def generate_reports_example():
    """Пример генерации отчетов"""
    
    # Инициализация
    initialize_framework()
    
    try:
        from reports.auto_reporter import auto_reporter
        
        print("📊 Генерация отчетов...")
        
        # Ежедневный отчет
        daily_report = auto_reporter.generate_daily_report()
        print(f"✅ Ежедневный отчет: {{daily_report}}")
        
        # Еженедельный отчет  
        weekly_report = auto_reporter.generate_weekly_report()
        print(f"✅ Еженедельный отчет: {{weekly_report}}")
        
    except ImportError:
        print("⚠️ Модуль отчетов не включен в данный тип проекта")

if __name__ == "__main__":
    generate_reports_example()
'''
        
        (examples_dir / "reports_example.py").write_text(reports_example)

def create_project_template(project_name: str, project_type: str, 
                          framework_components: List[str] = None,
                          custom_variables: Dict[str, Any] = None,
                          output_directory: str = None) -> str:
    """Удобная функция для создания проекта из шаблона"""
    
    if framework_components is None:
        framework_components = []
    
    if custom_variables is None:
        custom_variables = {}
    
    if output_directory is None:
        output_directory = f"generated_projects/{project_name}"
    
    config = TemplateConfig(
        project_name=project_name,
        project_type=project_type,
        framework_components=framework_components,
        custom_variables=custom_variables,
        output_directory=output_directory
    )
    
    generator = TemplateGenerator("/home/dmin/projects/telegram_sticker_bot/telegram_sticker_bot")
    return str(generator.create_universal_template(config))

if __name__ == "__main__":
    # Пример создания проекта
    print("🚀 Создание примера универсального шаблона...")
    
    project_path = create_project_template(
        project_name="MyMonitoringProject",
        project_type="full_framework",
        framework_components=["mcp_monitor", "alert_system", "auto_reporter"],
        custom_variables={"email_notifications": True},
        output_directory="universal_template_demo"
    )
    
    print(f"✅ Пример шаблона создан: {project_path}")