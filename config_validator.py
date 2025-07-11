#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Validator - Система валидации конфигураций
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class ValidationSeverity(Enum):
    """Уровень критичности ошибки валидации"""
    ERROR = "error"      # Критическая ошибка, блокирует запуск
    WARNING = "warning"  # Предупреждение, может работать с ограничениями
    INFO = "info"        # Информационное сообщение

@dataclass
class ValidationResult:
    """Результат валидации"""
    is_valid: bool
    severity: ValidationSeverity
    field: str
    message: str
    suggested_fix: Optional[str] = None

class ConfigValidator:
    """Валидатор конфигураций Claude MultiAgent Framework"""
    
    def __init__(self):
        self.schemas = self._init_validation_schemas()
        self.business_rules = self._init_business_rules()
        
    def _init_validation_schemas(self) -> Dict[str, Dict]:
        """Инициализация JSON схем валидации"""
        return {
            "framework_config": {
                "type": "object",
                "required": ["project", "framework"],
                "properties": {
                    "project": {
                        "type": "object",
                        "required": ["name", "type", "scale"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 100,
                                "pattern": "^[a-zA-Z0-9_-]+$"
                            },
                            "type": {
                                "type": "string",
                                "enum": [
                                    "telegram_bot", "web_api", "cli_tool",
                                    "data_pipeline", "microservice", 
                                    "desktop_app", "ml_service", "iot_device"
                                ]
                            },
                            "scale": {
                                "type": "string",
                                "enum": ["minimal", "standard", "advanced", "enterprise"]
                            },
                            "version": {"type": "string"},
                            "created": {"type": "string"}
                        }
                    },
                    "framework": {
                        "type": "object",
                        "required": ["components"],
                        "properties": {
                            "components": {
                                "type": "object",
                                "properties": {
                                    "mcp_monitor": {"type": "boolean"},
                                    "performance_tracker": {"type": "boolean"},
                                    "cache_manager": {"type": "boolean"},
                                    "alert_system": {"type": "boolean"},
                                    "auto_reporter": {"type": "boolean"},
                                    "optimizer_ai": {"type": "boolean"},
                                    "self_optimizer": {"type": "boolean"},
                                    "approval_system": {"type": "boolean"},
                                    "config_updater": {"type": "boolean"}
                                }
                            }
                        }
                    },
                    "monitoring": {
                        "type": "object",
                        "properties": {
                            "response_time_threshold": {
                                "type": "number",
                                "minimum": 0.1,
                                "maximum": 300.0
                            },
                            "track_performance": {"type": "boolean"},
                            "log_level": {
                                "type": "string",
                                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                            }
                        }
                    },
                    "alerts": {
                        "type": "object",
                        "properties": {
                            "email_notifications": {"type": "boolean"},
                            "slack_notifications": {"type": "boolean"},
                            "telegram_notifications": {"type": "boolean"},
                            "alert_on_errors": {"type": "boolean"},
                            "max_alerts_per_hour": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100
                            }
                        }
                    },
                    "optimization": {
                        "type": "object",
                        "properties": {
                            "auto_optimize": {"type": "boolean"},
                            "cache_enabled": {"type": "boolean"},
                            "max_cache_size_mb": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 1000
                            },
                            "cache_ttl_hours": {
                                "type": "number",
                                "minimum": 0.1,
                                "maximum": 168
                            }
                        }
                    }
                }
            },
            
            "monitoring_config": {
                "type": "object",
                "properties": {
                    "cache": {
                        "type": "object",
                        "properties": {
                            "max_size_mb": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 1000
                            },
                            "ttl_hours": {
                                "type": "number",
                                "minimum": 0.1,
                                "maximum": 168
                            },
                            "cleanup_interval_minutes": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 1440
                            }
                        }
                    },
                    "performance": {
                        "type": "object",
                        "properties": {
                            "max_response_time": {
                                "type": "number",
                                "minimum": 0.1,
                                "maximum": 300
                            },
                            "max_tokens_per_request": {
                                "type": "integer",
                                "minimum": 50,
                                "maximum": 10000
                            },
                            "tracking_enabled": {"type": "boolean"}
                        }
                    }
                }
            },
            
            "alert_config": {
                "type": "object",
                "properties": {
                    "thresholds": {
                        "type": "object",
                        "properties": {
                            "max_response_time": {
                                "type": "number",
                                "minimum": 0.1,
                                "maximum": 60
                            },
                            "max_tokens_per_request": {
                                "type": "integer",
                                "minimum": 100,
                                "maximum": 5000
                            },
                            "min_success_rate": {
                                "type": "number",
                                "minimum": 0.1,
                                "maximum": 1.0
                            },
                            "max_failure_streak": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100
                            }
                        }
                    },
                    "notification": {
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean"},
                            "console_output": {"type": "boolean"},
                            "file_logging": {"type": "boolean"},
                            "email_alerts": {"type": "boolean"}
                        }
                    },
                    "email": {
                        "type": "object",
                        "properties": {
                            "smtp_server": {"type": "string"},
                            "smtp_port": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 65535
                            },
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                            "recipients": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "format": "email"
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _init_business_rules(self) -> List[Dict]:
        """Инициализация бизнес-правил валидации"""
        return [
            {
                "name": "component_dependencies",
                "description": "Проверка зависимостей между компонентами",
                "check": self._validate_component_dependencies
            },
            {
                "name": "performance_consistency",
                "description": "Согласованность настроек производительности",
                "check": self._validate_performance_consistency
            },
            {
                "name": "alert_configuration",
                "description": "Корректность настройки алертов",
                "check": self._validate_alert_configuration
            },
            {
                "name": "scale_compatibility",
                "description": "Соответствие компонентов масштабу проекта",
                "check": self._validate_scale_compatibility
            },
            {
                "name": "security_requirements",
                "description": "Проверка требований безопасности",
                "check": self._validate_security_requirements
            }
        ]
    
    def validate_config(self, config_data: Dict[str, Any], 
                       config_type: str = "framework_config") -> List[ValidationResult]:
        """Полная валидация конфигурации"""
        results = []
        
        # 1. Валидация JSON схемы
        schema_results = self._validate_json_schema(config_data, config_type)
        results.extend(schema_results)
        
        # 2. Валидация бизнес-правил (только если схема прошла валидацию)
        if not any(r.severity == ValidationSeverity.ERROR for r in schema_results):
            business_results = self._validate_business_rules(config_data)
            results.extend(business_results)
        
        # 3. Валидация значений по умолчанию
        default_results = self._validate_defaults(config_data, config_type)
        results.extend(default_results)
        
        return results
    
    def _validate_json_schema(self, config_data: Dict[str, Any], 
                            config_type: str) -> List[ValidationResult]:
        """Валидация по JSON схеме"""
        results = []
        
        if config_type not in self.schemas:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="config_type",
                message=f"Неизвестный тип конфигурации: {config_type}",
                suggested_fix=f"Используйте один из: {', '.join(self.schemas.keys())}"
            ))
            return results
        
        schema = self.schemas[config_type]
        
        try:
            jsonschema.validate(instance=config_data, schema=schema)
            results.append(ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                field="schema",
                message="JSON схема прошла валидацию успешно"
            ))
        except jsonschema.ValidationError as e:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field=".".join(str(x) for x in e.absolute_path),
                message=f"Ошибка схемы: {e.message}",
                suggested_fix=self._get_schema_fix_suggestion(e)
            ))
        except jsonschema.SchemaError as e:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="schema",
                message=f"Ошибка в схеме валидации: {e.message}"
            ))
        
        return results
    
    def _validate_business_rules(self, config_data: Dict[str, Any]) -> List[ValidationResult]:
        """Валидация бизнес-правил"""
        results = []
        
        for rule in self.business_rules:
            try:
                rule_results = rule["check"](config_data)
                if rule_results:
                    results.extend(rule_results)
            except Exception as e:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    field=rule["name"],
                    message=f"Ошибка в бизнес-правиле '{rule['name']}': {e}"
                ))
        
        return results
    
    def _validate_component_dependencies(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Валидация зависимостей между компонентами"""
        results = []
        
        components = config.get("framework", {}).get("components", {})
        
        # self_optimizer требует approval_system и config_updater
        if components.get("self_optimizer", False):
            if not components.get("approval_system", False):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    field="framework.components.approval_system",
                    message="self_optimizer требует включения approval_system",
                    suggested_fix="Включите approval_system или отключите self_optimizer"
                ))
            
            if not components.get("config_updater", False):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    field="framework.components.config_updater",
                    message="self_optimizer требует включения config_updater",
                    suggested_fix="Включите config_updater или отключите self_optimizer"
                ))
        
        # optimizer_ai требует performance_tracker
        if components.get("optimizer_ai", False) and not components.get("performance_tracker", False):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                field="framework.components.performance_tracker",
                message="optimizer_ai работает эффективнее с performance_tracker",
                suggested_fix="Рекомендуется включить performance_tracker"
            ))
        
        # auto_reporter требует performance_tracker
        if components.get("auto_reporter", False) and not components.get("performance_tracker", False):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                field="framework.components.performance_tracker",
                message="auto_reporter требует данные от performance_tracker",
                suggested_fix="Включите performance_tracker для полной функциональности отчетов"
            ))
        
        return results
    
    def _validate_performance_consistency(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Валидация согласованности настроек производительности"""
        results = []
        
        monitoring = config.get("monitoring", {})
        alerts = config.get("alerts", {})
        
        # Порог ответа в мониторинге и алертах должен быть согласован
        monitor_threshold = monitoring.get("response_time_threshold")
        alert_threshold = alerts.get("thresholds", {}).get("max_response_time")
        
        if monitor_threshold and alert_threshold:
            if alert_threshold <= monitor_threshold:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    field="alerts.thresholds.max_response_time",
                    message=f"Порог алертов ({alert_threshold}s) меньше или равен порогу мониторинга ({monitor_threshold}s)",
                    suggested_fix="Установите порог алертов больше порога мониторинга"
                ))
        
        # Проверка размера кэша
        cache_size = config.get("optimization", {}).get("max_cache_size_mb", 100)
        if cache_size > 500:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                field="optimization.max_cache_size_mb",
                message=f"Большой размер кэша ({cache_size}MB) может повлиять на производительность",
                suggested_fix="Рекомендуется размер кэша до 500MB"
            ))
        
        return results
    
    def _validate_alert_configuration(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Валидация конфигурации алертов"""
        results = []
        
        alerts = config.get("alerts", {})
        
        # Проверка email конфигурации
        if alerts.get("email_notifications", False):
            email_config = alerts.get("email", {})
            
            if not email_config.get("smtp_server"):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    field="alerts.email.smtp_server",
                    message="Email уведомления включены, но не указан SMTP сервер",
                    suggested_fix="Укажите SMTP сервер или отключите email уведомления"
                ))
            
            if not email_config.get("recipients"):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    field="alerts.email.recipients",
                    message="Email уведомления включены, но не указаны получатели",
                    suggested_fix="Добавьте email адреса получателей"
                ))
        
        # Проверка частоты алертов
        max_alerts = alerts.get("max_alerts_per_hour", 10)
        if max_alerts > 50:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                field="alerts.max_alerts_per_hour",
                message=f"Высокая частота алертов ({max_alerts}/час) может создать спам",
                suggested_fix="Рекомендуется не более 50 алертов в час"
            ))
        
        return results
    
    def _validate_scale_compatibility(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Валидация соответствия компонентов масштабу проекта"""
        results = []
        
        project_scale = config.get("project", {}).get("scale", "standard")
        components = config.get("framework", {}).get("components", {})
        
        # Рекомендации по компонентам для разных масштабов
        scale_requirements = {
            "minimal": {
                "required": ["mcp_monitor"],
                "optional": ["alert_system"],
                "not_recommended": ["optimizer_ai", "self_optimizer"]
            },
            "standard": {
                "required": ["mcp_monitor", "alert_system", "performance_tracker"],
                "optional": ["cache_manager", "auto_reporter"],
                "not_recommended": []
            },
            "advanced": {
                "required": ["mcp_monitor", "alert_system", "performance_tracker", "cache_manager"],
                "optional": ["auto_reporter", "optimizer_ai"],
                "not_recommended": []
            },
            "enterprise": {
                "required": ["mcp_monitor", "alert_system", "performance_tracker", 
                           "cache_manager", "auto_reporter", "optimizer_ai"],
                "optional": ["self_optimizer", "approval_system", "config_updater"],
                "not_recommended": []
            }
        }
        
        if project_scale in scale_requirements:
            reqs = scale_requirements[project_scale]
            
            # Проверка обязательных компонентов
            for required_component in reqs["required"]:
                if not components.get(required_component, False):
                    results.append(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.WARNING,
                        field=f"framework.components.{required_component}",
                        message=f"Для масштаба '{project_scale}' рекомендуется включить {required_component}",
                        suggested_fix=f"Включите {required_component} или измените масштаб проекта"
                    ))
            
            # Проверка нерекомендуемых компонентов
            for not_recommended in reqs["not_recommended"]:
                if components.get(not_recommended, False):
                    results.append(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.INFO,
                        field=f"framework.components.{not_recommended}",
                        message=f"Для масштаба '{project_scale}' компонент {not_recommended} может быть избыточным",
                        suggested_fix=f"Рассмотрите отключение {not_recommended} или увеличение масштаба"
                    ))
        
        return results
    
    def _validate_security_requirements(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Валидация требований безопасности"""
        results = []
        
        # Проверка паролей в конфигурации
        email_config = config.get("alerts", {}).get("email", {})
        if email_config.get("password"):
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="alerts.email.password",
                message="Пароль не должен храниться в конфигурации в открытом виде",
                suggested_fix="Используйте переменные окружения для хранения паролей"
            ))
        
        # Проверка отладочного режима в продакшене
        if config.get("monitoring", {}).get("log_level") == "DEBUG":
            project_type = config.get("project", {}).get("type", "")
            if project_type in ["web_api", "microservice"]:
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    field="monitoring.log_level",
                    message="Отладочный режим не рекомендуется для продакшен сервисов",
                    suggested_fix="Установите log_level в INFO или WARNING для продакшена"
                ))
        
        return results
    
    def _validate_defaults(self, config: Dict[str, Any], config_type: str) -> List[ValidationResult]:
        """Валидация значений по умолчанию"""
        results = []
        
        # Проверка обязательных полей, которые могут отсутствовать
        if config_type == "framework_config":
            if not config.get("project", {}).get("version"):
                results.append(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.INFO,
                    field="project.version",
                    message="Не указана версия проекта",
                    suggested_fix="Добавьте версию проекта (например, '1.0.0')"
                ))
        
        return results
    
    def _get_schema_fix_suggestion(self, error: jsonschema.ValidationError) -> str:
        """Получение предложения по исправлению ошибки схемы"""
        if "is not of type" in error.message:
            expected_type = error.schema.get("type", "unknown")
            return f"Измените тип значения на {expected_type}"
        
        if "is not one of" in error.message:
            enum_values = error.schema.get("enum", [])
            return f"Используйте одно из значений: {', '.join(map(str, enum_values))}"
        
        if "is too short" in error.message:
            min_length = error.schema.get("minLength", 0)
            return f"Минимальная длина: {min_length} символов"
        
        if "is too long" in error.message:
            max_length = error.schema.get("maxLength", 0)
            return f"Максимальная длина: {max_length} символов"
        
        if "is less than the minimum" in error.message:
            minimum = error.schema.get("minimum", 0)
            return f"Минимальное значение: {minimum}"
        
        if "is greater than the maximum" in error.message:
            maximum = error.schema.get("maximum", 0)
            return f"Максимальное значение: {maximum}"
        
        return "Проверьте соответствие схеме"
    
    def validate_config_file(self, config_file: str) -> List[ValidationResult]:
        """Валидация конфигурационного файла"""
        results = []
        
        config_path = Path(config_file)
        
        # Проверка существования файла
        if not config_path.exists():
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="file",
                message=f"Конфигурационный файл не найден: {config_file}",
                suggested_fix="Проверьте путь к файлу"
            ))
            return results
        
        # Определение типа конфигурации по имени файла
        config_type = "framework_config"
        if "monitoring" in config_path.name:
            config_type = "monitoring_config"
        elif "alert" in config_path.name:
            config_type = "alert_config"
        
        # Загрузка и валидация
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Валидация содержимого
            validation_results = self.validate_config(config_data, config_type)
            results.extend(validation_results)
            
        except json.JSONDecodeError as e:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="json",
                message=f"Ошибка парсинга JSON: {e}",
                suggested_fix="Проверьте синтаксис JSON"
            ))
        except Exception as e:
            results.append(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                field="file",
                message=f"Ошибка чтения файла: {e}"
            ))
        
        return results
    
    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """Генерация отчета о валидации"""
        report_lines = ["# Отчет валидации конфигурации\n"]
        
        # Подсчет результатов
        errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
        warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
        info = [r for r in results if r.severity == ValidationSeverity.INFO]
        
        # Сводка
        report_lines.append("## Сводка\n")
        report_lines.append(f"- ❌ Ошибки: {len(errors)}")
        report_lines.append(f"- ⚠️ Предупреждения: {len(warnings)}")
        report_lines.append(f"- ℹ️ Информация: {len(info)}")
        report_lines.append(f"- ✅ Общий статус: {'FAILED' if errors else 'PASSED'}\n")
        
        # Детали по категориям
        for category, items, icon in [
            ("Ошибки", errors, "❌"),
            ("Предупреждения", warnings, "⚠️"),
            ("Информация", info, "ℹ️")
        ]:
            if items:
                report_lines.append(f"## {icon} {category}\n")
                for result in items:
                    report_lines.append(f"### {result.field}")
                    report_lines.append(f"**Сообщение:** {result.message}")
                    if result.suggested_fix:
                        report_lines.append(f"**Исправление:** {result.suggested_fix}")
                    report_lines.append("")
        
        return "\n".join(report_lines)

# Глобальный экземпляр валидатора
config_validator = ConfigValidator()

def validate_project_config(config_file: str) -> bool:
    """Быстрая валидация конфигурации проекта"""
    results = config_validator.validate_config_file(config_file)
    
    # Отображение результатов
    errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
    warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
    
    print(f"\n🔍 [Критик] Валидация конфигурации: {config_file}")
    
    if errors:
        print(f"❌ Найдено {len(errors)} критических ошибок:")
        for error in errors:
            print(f"   • {error.field}: {error.message}")
            if error.suggested_fix:
                print(f"     💡 {error.suggested_fix}")
    
    if warnings:
        print(f"⚠️ Найдено {len(warnings)} предупреждений:")
        for warning in warnings[:3]:  # Показываем только первые 3
            print(f"   • {warning.field}: {warning.message}")
        if len(warnings) > 3:
            print(f"   ... и еще {len(warnings) - 3}")
    
    if not errors and not warnings:
        print("✅ Конфигурация корректна!")
    
    return len(errors) == 0

def validate_all_configs(project_dir: str = ".") -> bool:
    """Валидация всех конфигурационных файлов в проекте"""
    project_path = Path(project_dir)
    config_files = []
    
    # Поиск конфигурационных файлов
    for pattern in ["**/framework_config.json", "**/monitoring_config.json", "**/alert_config.json"]:
        config_files.extend(project_path.glob(pattern))
    
    if not config_files:
        print("⚠️ Конфигурационные файлы не найдены")
        return False
    
    print(f"🔍 [Критик] Валидация {len(config_files)} конфигурационных файлов:")
    
    all_valid = True
    for config_file in config_files:
        is_valid = validate_project_config(str(config_file))
        all_valid = all_valid and is_valid
    
    if all_valid:
        print("\n✅ Все конфигурации корректны!")
    else:
        print("\n❌ Обнаружены проблемы в конфигурациях")
    
    return all_valid

if __name__ == "__main__":
    # Демонстрация валидации
    print("🛡️ Демонстрация системы валидации конфигураций\n")
    
    # Валидация примера правильной конфигурации
    valid_config = {
        "project": {
            "name": "TestProject",
            "type": "web_api",
            "scale": "standard",
            "version": "1.0.0"
        },
        "framework": {
            "components": {
                "mcp_monitor": True,
                "performance_tracker": True,
                "alert_system": True,
                "cache_manager": True,
                "auto_reporter": True,
                "optimizer_ai": False,
                "self_optimizer": False
            }
        },
        "monitoring": {
            "response_time_threshold": 2.0,
            "track_performance": True,
            "log_level": "INFO"
        },
        "alerts": {
            "email_notifications": False,
            "alert_on_errors": True,
            "max_alerts_per_hour": 10
        },
        "optimization": {
            "auto_optimize": False,
            "cache_enabled": True,
            "max_cache_size_mb": 100,
            "cache_ttl_hours": 24
        }
    }
    
    print("✅ Валидация корректной конфигурации:")
    results = config_validator.validate_config(valid_config)
    for result in results:
        severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[result.severity.value]
        print(f"   {severity_icon} {result.field}: {result.message}")
    
    # Валидация примера с ошибками
    print("\n❌ Валидация конфигурации с ошибками:")
    invalid_config = {
        "project": {
            "name": "",  # Пустое имя
            "type": "unknown_type",  # Неверный тип
            "scale": "huge"  # Неверный масштаб
        },
        "framework": {
            "components": {
                "self_optimizer": True,  # Без зависимостей
                "optimizer_ai": True
            }
        },
        "monitoring": {
            "response_time_threshold": -1  # Отрицательное значение
        },
        "alerts": {
            "email_notifications": True,  # Без конфигурации SMTP
            "max_alerts_per_hour": 200  # Слишком много
        }
    }
    
    error_results = config_validator.validate_config(invalid_config)
    for result in error_results[:5]:  # Показываем первые 5 ошибок
        severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[result.severity.value]
        print(f"   {severity_icon} {result.field}: {result.message}")
        if result.suggested_fix:
            print(f"     💡 {result.suggested_fix}")
    
    if len(error_results) > 5:
        print(f"   ... и еще {len(error_results) - 5} проблем")
    
    print(f"\n📊 Итого проблем: {len(error_results)}")