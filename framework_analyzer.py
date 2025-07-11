#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Framework Analyzer - Анализатор структуры для создания универсального шаблона
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import re
import ast

@dataclass
class FrameworkComponent:
    """Компонент фреймворка"""
    name: str
    path: str
    component_type: str  # core, optional, project_specific
    dependencies: List[str]
    purpose: str
    extractable: bool
    template_vars: List[str]

@dataclass
class ProjectTemplate:
    """Шаблон проекта"""
    template_name: str
    description: str
    required_components: List[str]
    optional_components: List[str]
    config_params: Dict[str, Any]
    project_structure: Dict[str, Any]

class FrameworkAnalyzer:
    """Анализатор фреймворка для создания универсального шаблона"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.components: Dict[str, FrameworkComponent] = {}
        self.templates: Dict[str, ProjectTemplate] = {}
        
        # Паттерны для анализа кода
        self.import_pattern = re.compile(r'^from\s+(\S+)\s+import|^import\s+(\S+)', re.MULTILINE)
        self.config_pattern = re.compile(r'config\[(["\'])([^"\']+)\1\]')
        
    def analyze_framework_structure(self) -> Dict[str, Any]:
        """Анализ структуры фреймворка"""
        print("🔍 [Архитектор] Анализирую структуру Claude MultiAgent Framework...")
        
        analysis = {
            "core_framework_components": self._analyze_core_components(),
            "project_specific_components": self._analyze_project_components(),
            "configuration_layers": self._analyze_config_layers(),
            "template_variables": self._extract_template_variables(),
            "dependencies_map": self._build_dependencies_map(),
            "extractable_patterns": self._identify_extractable_patterns()
        }
        
        return analysis
    
    def _analyze_core_components(self) -> List[Dict]:
        """Анализ основных компонентов фреймворка"""
        core_components = []
        
        # MultiAgent Framework компоненты
        framework_dirs = [
            "monitoring",
            "reports", 
            "recommendations",
            "autonomous"
        ]
        
        for dir_name in framework_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
                
            for py_file in dir_path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                    
                component = self._analyze_python_file(py_file, "core")
                if component:
                    core_components.append(asdict(component))
                    self.components[component.name] = component
        
        return core_components
    
    def _analyze_project_components(self) -> List[Dict]:
        """Анализ специфичных для проекта компонентов"""
        project_components = []
        
        # Проект-специфичные директории
        project_dirs = [
            "bot",
            "services", 
            "db",
            "config"
        ]
        
        for dir_name in project_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
                
            for py_file in dir_path.glob("**/*.py"):
                if py_file.name.startswith("__"):
                    continue
                    
                component = self._analyze_python_file(py_file, "project_specific")
                if component:
                    project_components.append(asdict(component))
                    self.components[component.name] = component
        
        return project_components
    
    def _analyze_python_file(self, file_path: Path, component_type: str) -> Optional[FrameworkComponent]:
        """Анализ Python файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлечение импортов
            imports = self._extract_imports(content)
            
            # Извлечение переменных конфигурации
            config_vars = self._extract_config_variables(content)
            
            # Определение назначения компонента
            purpose = self._determine_purpose(file_path, content)
            
            # Определение извлекаемости
            extractable = self._is_extractable(file_path, content, component_type)
            
            relative_path = str(file_path.relative_to(self.project_root))
            
            return FrameworkComponent(
                name=file_path.stem,
                path=relative_path,
                component_type=component_type,
                dependencies=imports,
                purpose=purpose,
                extractable=extractable,
                template_vars=config_vars
            )
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа {file_path}: {e}")
            return None
    
    def _extract_imports(self, content: str) -> List[str]:
        """Извлечение импортов из кода"""
        imports = []
        for match in self.import_pattern.finditer(content):
            module = match.group(1) or match.group(2)
            if module and not module.startswith('.'):
                # Только внутренние зависимости проекта
                if any(framework_part in module for framework_part in 
                      ['monitoring', 'reports', 'recommendations', 'autonomous', 'config', 'services']):
                    imports.append(module)
        return list(set(imports))
    
    def _extract_config_variables(self, content: str) -> List[str]:
        """Извлечение переменных конфигурации"""
        config_vars = []
        
        # Поиск паттернов config["key"]
        for match in self.config_pattern.finditer(content):
            config_vars.append(match.group(2))
        
        # Поиск других паттернов конфигурации
        env_pattern = re.compile(r'os\.getenv\(["\']([^"\']+)["\']')
        for match in env_pattern.finditer(content):
            config_vars.append(f"ENV:{match.group(1)}")
        
        return list(set(config_vars))
    
    def _determine_purpose(self, file_path: Path, content: str) -> str:
        """Определение назначения компонента"""
        path_str = str(file_path).lower()
        
        if "monitoring" in path_str:
            if "performance" in file_path.name:
                return "Отслеживание производительности MCP"
            elif "cache" in file_path.name:
                return "Управление кэшированием запросов"
            elif "alert" in file_path.name:
                return "Система предупреждений"
            else:
                return "Мониторинг системы"
        
        elif "reports" in path_str:
            return "Автоматическая генерация отчетов"
        
        elif "recommendations" in path_str:
            return "ИИ-анализ и рекомендации оптимизации"
        
        elif "autonomous" in path_str:
            if "approval" in file_path.name:
                return "Интерфейс подтверждения изменений"
            elif "config" in file_path.name:
                return "Безопасное обновление конфигураций"
            else:
                return "Автономное самоулучшение"
        
        elif "bot" in path_str:
            return "Telegram бот (проект-специфичный)"
        
        elif "services" in path_str:
            return "Бизнес-логика проекта"
        
        elif "db" in path_str:
            return "Работа с базой данных"
        
        elif "config" in path_str:
            return "Конфигурация проекта"
        
        else:
            return "Вспомогательный компонент"
    
    def _is_extractable(self, file_path: Path, content: str, component_type: str) -> bool:
        """Определение возможности извлечения компонента в шаблон"""
        # Основные компоненты фреймворка всегда извлекаемы
        if component_type == "core":
            return True
        
        # Проверка зависимостей от проект-специфичных модулей
        telegram_imports = ['aiogram', 'telegram', 'bot.', 'services.']
        if any(imp in content for imp in telegram_imports):
            return False
        
        # Файлы конфигурации обычно требуют адаптации
        if "config" in str(file_path).lower():
            return False
        
        return True
    
    def _analyze_config_layers(self) -> Dict[str, Any]:
        """Анализ слоев конфигурации"""
        config_layers = {
            "framework_configs": [],
            "project_configs": [],
            "template_variables": []
        }
        
        # Поиск конфигурационных файлов
        for config_file in self.project_root.glob("**/*.json"):
            if "venv" in str(config_file):
                continue
                
            relative_path = str(config_file.relative_to(self.project_root))
            
            if any(framework_dir in relative_path for framework_dir in 
                  ["monitoring", "reports", "recommendations", "autonomous"]):
                config_layers["framework_configs"].append(relative_path)
            else:
                config_layers["project_configs"].append(relative_path)
        
        return config_layers
    
    def _extract_template_variables(self) -> List[Dict]:
        """Извлечение шаблонных переменных"""
        template_vars = []
        
        # Собираем все переменные конфигурации из компонентов
        all_vars = set()
        for component in self.components.values():
            all_vars.update(component.template_vars)
        
        # Анализируем каждую переменную
        for var in all_vars:
            var_info = {
                "name": var,
                "type": self._infer_variable_type(var),
                "required": self._is_variable_required(var),
                "default_value": self._get_default_value(var),
                "description": self._get_variable_description(var)
            }
            template_vars.append(var_info)
        
        return template_vars
    
    def _infer_variable_type(self, var: str) -> str:
        """Определение типа переменной"""
        var_lower = var.lower()
        
        if var.startswith("ENV:"):
            return "environment"
        elif "port" in var_lower or "timeout" in var_lower:
            return "integer"
        elif "enable" in var_lower or "debug" in var_lower:
            return "boolean"
        elif "url" in var_lower or "path" in var_lower:
            return "string"
        elif "rate" in var_lower or "threshold" in var_lower:
            return "float"
        else:
            return "string"
    
    def _is_variable_required(self, var: str) -> bool:
        """Определение обязательности переменной"""
        critical_vars = ["database_url", "api_key", "secret", "token"]
        return any(critical in var.lower() for critical in critical_vars)
    
    def _get_default_value(self, var: str) -> Any:
        """Получение значения по умолчанию"""
        var_lower = var.lower()
        
        if "enable" in var_lower:
            return True
        elif "debug" in var_lower:
            return False
        elif "port" in var_lower:
            return 8080
        elif "timeout" in var_lower:
            return 30
        elif "max_size" in var_lower:
            return 100
        else:
            return ""
    
    def _get_variable_description(self, var: str) -> str:
        """Получение описания переменной"""
        descriptions = {
            "max_response_time": "Максимальное время ответа MCP сервера (сек)",
            "max_tokens_per_request": "Лимит токенов на запрос",
            "cache_ttl_hours": "Время жизни кэша (часы)",
            "alert_email": "Email для уведомлений",
            "database_url": "URL подключения к базе данных",
            "debug_mode": "Режим отладки"
        }
        
        return descriptions.get(var, f"Конфигурационный параметр: {var}")
    
    def _build_dependencies_map(self) -> Dict[str, List[str]]:
        """Построение карты зависимостей"""
        dependencies_map = {}
        
        for name, component in self.components.items():
            dependencies_map[name] = {
                "direct_dependencies": component.dependencies,
                "reverse_dependencies": []
            }
        
        # Построение обратных зависимостей
        for name, component in self.components.items():
            for dep in component.dependencies:
                dep_name = dep.split('.')[-1]
                if dep_name in dependencies_map:
                    dependencies_map[dep_name]["reverse_dependencies"].append(name)
        
        return dependencies_map
    
    def _identify_extractable_patterns(self) -> Dict[str, List[str]]:
        """Идентификация извлекаемых паттернов"""
        patterns = {
            "core_framework": [],
            "optional_enhancements": [],
            "project_adapters": []
        }
        
        for name, component in self.components.items():
            if component.extractable and component.component_type == "core":
                patterns["core_framework"].append(name)
            elif component.extractable and component.component_type == "optional":
                patterns["optional_enhancements"].append(name)
            else:
                patterns["project_adapters"].append(name)
        
        return patterns
    
    def generate_template_structure(self) -> Dict[str, Any]:
        """Генерация структуры универсального шаблона"""
        print("🏗️ [Архитектор] Генерирую структуру универсального шаблона...")
        
        template_structure = {
            "template_info": {
                "name": "Claude MultiAgent Framework",
                "version": "1.0.0",
                "description": "Универсальный фреймворк автономного мультиагентного мониторинга и оптимизации",
                "author": "Claude MultiAgent System",
                "license": "MIT"
            },
            "project_types": self._define_project_types(),
            "core_components": self._get_core_template_components(),
            "optional_components": self._get_optional_components(),
            "configuration_schema": self._generate_config_schema(),
            "initialization_templates": self._create_initialization_templates(),
            "customization_points": self._identify_customization_points()
        }
        
        return template_structure
    
    def _define_project_types(self) -> Dict[str, ProjectTemplate]:
        """Определение типов проектов"""
        project_types = {}
        
        # Базовый мониторинг
        project_types["basic_monitoring"] = ProjectTemplate(
            template_name="Базовый мониторинг",
            description="Простой мониторинг MCP с алертами",
            required_components=["mcp_monitor", "alert_system"],
            optional_components=["performance_tracker", "cache_manager"],
            config_params={
                "monitoring_enabled": True,
                "alerts_enabled": True,
                "cache_enabled": False
            },
            project_structure={
                "monitoring/": ["mcp_monitor.py", "alert_system.py"],
                "config/": ["framework_config.json"]
            }
        )
        
        # Полный фреймворк
        project_types["full_framework"] = ProjectTemplate(
            template_name="Полный MultiAgent Framework", 
            description="Комплексная система с ИИ-оптимизацией и автономностью",
            required_components=[
                "mcp_monitor", "performance_tracker", "cache_manager", 
                "alert_system", "auto_reporter", "optimizer_ai",
                "self_optimizer", "approval_system", "config_updater"
            ],
            optional_components=[],
            config_params={
                "monitoring_enabled": True,
                "alerts_enabled": True, 
                "cache_enabled": True,
                "reports_enabled": True,
                "ai_optimization_enabled": True,
                "autonomous_mode": True
            },
            project_structure={
                "monitoring/": ["mcp_monitor.py", "performance_tracker.py", "cache_manager.py", "alert_system.py"],
                "reports/": ["auto_reporter.py", "templates/"],
                "recommendations/": ["optimizer_ai.py"],
                "autonomous/": ["self_optimizer.py", "approval_system.py", "config_updater.py"],
                "config/": ["framework_config.json"]
            }
        )
        
        # Web приложение
        project_types["web_application"] = ProjectTemplate(
            template_name="Web приложение с мониторингом",
            description="Мониторинг для Flask/Django приложений",
            required_components=["mcp_monitor", "performance_tracker", "alert_system"],
            optional_components=["auto_reporter", "cache_manager"],
            config_params={
                "web_dashboard_enabled": True,
                "api_monitoring": True,
                "database_monitoring": True
            },
            project_structure={
                "monitoring/": ["mcp_monitor.py", "performance_tracker.py", "alert_system.py"],
                "web/": ["dashboard.py", "api_monitor.py"],
                "config/": ["framework_config.json"]
            }
        )
        
        return {name: asdict(template) for name, template in project_types.items()}
    
    def _get_core_template_components(self) -> List[str]:
        """Получение основных компонентов шаблона"""
        return [name for name, component in self.components.items() 
                if component.extractable and component.component_type == "core"]
    
    def _get_optional_components(self) -> List[str]:
        """Получение опциональных компонентов"""
        return [name for name, component in self.components.items()
                if component.extractable and "optional" in component.purpose.lower()]
    
    def _generate_config_schema(self) -> Dict[str, Any]:
        """Генерация схемы конфигурации"""
        template_vars = self._extract_template_variables()
        
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for var in template_vars:
            var_name = var["name"].replace("ENV:", "")
            
            property_def = {
                "type": var["type"],
                "description": var["description"]
            }
            
            if var["default_value"] is not None:
                property_def["default"] = var["default_value"]
            
            schema["properties"][var_name] = property_def
            
            if var["required"]:
                schema["required"].append(var_name)
        
        return schema
    
    def _create_initialization_templates(self) -> Dict[str, str]:
        """Создание шаблонов инициализации"""
        return {
            "basic_init.py": """
# Базовая инициализация Claude MultiAgent Framework
from monitoring.mcp_monitor import mcp_monitor
from monitoring.alert_system import alert_system

def initialize_basic_monitoring():
    print("🚀 Инициализация базового мониторинга...")
    # Инициализация мониторинга
    return True
""",
            "full_init.py": """
# Полная инициализация Claude MultiAgent Framework
from monitoring.mcp_monitor import mcp_monitor
from monitoring.performance_tracker import performance_tracker
from monitoring.cache_manager import cache_manager
from monitoring.alert_system import alert_system
from reports.auto_reporter import auto_reporter
from recommendations.optimizer_ai import optimizer_ai
from autonomous.self_optimizer import self_optimizer

def initialize_full_framework():
    print("🚀 Инициализация полного MultiAgent Framework...")
    # Инициализация всех компонентов
    return True
"""
        }
    
    def _identify_customization_points(self) -> List[Dict]:
        """Идентификация точек кастомизации"""
        return [
            {
                "component": "mcp_monitor",
                "customization_point": "add_custom_metrics",
                "description": "Добавление пользовательских метрик мониторинга"
            },
            {
                "component": "alert_system", 
                "customization_point": "custom_alert_rules",
                "description": "Настройка правил предупреждений под проект"
            },
            {
                "component": "auto_reporter",
                "customization_point": "custom_report_templates",
                "description": "Создание пользовательских шаблонов отчетов"
            }
        ]
    
    def save_analysis(self, output_file: str):
        """Сохранение результатов анализа"""
        analysis = self.analyze_framework_structure()
        template_structure = self.generate_template_structure()
        
        result = {
            "analysis_timestamp": "2025-07-11",
            "framework_analysis": analysis,
            "template_structure": template_structure
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Анализ сохранен: {output_file}")
        return output_file

if __name__ == "__main__":
    analyzer = FrameworkAnalyzer("/home/dmin/projects/telegram_sticker_bot/telegram_sticker_bot")
    
    # Выполнение анализа
    analysis_file = analyzer.save_analysis("autonomous/framework_analysis.json")
    
    print("\n✅ [Архитектор] Анализ структуры завершен")
    print(f"📋 Результаты сохранены в: {analysis_file}")