#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Profiles - Система профилей конфигурации для разных типов проектов
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import yaml

class ProjectType(Enum):
    """Типы проектов"""
    TELEGRAM_BOT = "telegram_bot"
    WEB_API = "web_api"
    CLI_TOOL = "cli_tool"
    DATA_PIPELINE = "data_pipeline"
    MICROSERVICE = "microservice"
    DESKTOP_APP = "desktop_app"
    ML_SERVICE = "ml_service"
    IOT_DEVICE = "iot_device"

class ScaleProfile(Enum):
    """Профили масштабирования"""
    MINIMAL = "minimal"        # Минимальный мониторинг
    STANDARD = "standard"      # Стандартный набор
    ADVANCED = "advanced"      # Расширенный мониторинг
    ENTERPRISE = "enterprise"  # Корпоративный уровень

@dataclass
class ConfigProfile:
    """Профиль конфигурации"""
    name: str
    project_type: ProjectType
    scale_profile: ScaleProfile
    components: Dict[str, bool]
    monitoring_settings: Dict[str, Any]
    alert_settings: Dict[str, Any]
    optimization_settings: Dict[str, Any]
    custom_settings: Dict[str, Any]

class ConfigProfileManager:
    """Менеджер профилей конфигурации"""
    
    def __init__(self, profiles_dir: str = "config_profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Загрузка базовых профилей
        self.base_profiles = self._init_base_profiles()
        
        # Кэш загруженных профилей
        self.loaded_profiles: Dict[str, ConfigProfile] = {}
    
    def _init_base_profiles(self) -> Dict[str, ConfigProfile]:
        """Инициализация базовых профилей конфигурации"""
        profiles = {}
        
        # ===== TELEGRAM BOT PROFILES =====
        profiles["telegram_bot_minimal"] = ConfigProfile(
            name="Telegram Bot - Минимальный",
            project_type=ProjectType.TELEGRAM_BOT,
            scale_profile=ScaleProfile.MINIMAL,
            components={
                "mcp_monitor": True,
                "alert_system": True,
                "performance_tracker": False,
                "cache_manager": False,
                "auto_reporter": False,
                "optimizer_ai": False,
                "self_optimizer": False
            },
            monitoring_settings={
                "track_message_handlers": True,
                "track_callback_queries": True,
                "track_inline_queries": False,
                "response_time_threshold": 5.0,
                "log_user_actions": True
            },
            alert_settings={
                "telegram_notifications": True,
                "email_notifications": False,
                "alert_on_errors": True,
                "alert_on_slow_response": False,
                "daily_summary": False
            },
            optimization_settings={
                "auto_optimize": False,
                "cache_user_data": False,
                "batch_processing": False
            },
            custom_settings={
                "bot_specific": {
                    "track_user_sessions": True,
                    "monitor_api_limits": True,
                    "webhook_monitoring": False
                }
            }
        )
        
        profiles["telegram_bot_advanced"] = ConfigProfile(
            name="Telegram Bot - Продвинутый",
            project_type=ProjectType.TELEGRAM_BOT,
            scale_profile=ScaleProfile.ADVANCED,
            components={
                "mcp_monitor": True,
                "alert_system": True,
                "performance_tracker": True,
                "cache_manager": True,
                "auto_reporter": True,
                "optimizer_ai": True,
                "self_optimizer": True
            },
            monitoring_settings={
                "track_message_handlers": True,
                "track_callback_queries": True,
                "track_inline_queries": True,
                "response_time_threshold": 2.0,
                "log_user_actions": True,
                "track_memory_usage": True,
                "track_api_calls": True
            },
            alert_settings={
                "telegram_notifications": True,
                "email_notifications": True,
                "alert_on_errors": True,
                "alert_on_slow_response": True,
                "alert_on_high_memory": True,
                "daily_summary": True,
                "weekly_report": True
            },
            optimization_settings={
                "auto_optimize": True,
                "cache_user_data": True,
                "batch_processing": True,
                "adaptive_polling": True,
                "auto_scale_workers": True
            },
            custom_settings={
                "bot_specific": {
                    "track_user_sessions": True,
                    "monitor_api_limits": True,
                    "webhook_monitoring": True,
                    "conversation_analytics": True,
                    "user_behavior_tracking": True
                }
            }
        )
        
        # ===== WEB API PROFILES =====
        profiles["web_api_standard"] = ConfigProfile(
            name="Web API - Стандартный",
            project_type=ProjectType.WEB_API,
            scale_profile=ScaleProfile.STANDARD,
            components={
                "mcp_monitor": True,
                "alert_system": True,
                "performance_tracker": True,
                "cache_manager": True,
                "auto_reporter": True,
                "optimizer_ai": False,
                "self_optimizer": False
            },
            monitoring_settings={
                "track_endpoints": True,
                "track_response_times": True,
                "track_status_codes": True,
                "track_request_body_size": True,
                "track_auth_failures": True,
                "response_time_threshold": 1.0,
                "track_database_queries": True
            },
            alert_settings={
                "slack_notifications": True,
                "email_notifications": True,
                "alert_on_5xx_errors": True,
                "alert_on_4xx_surge": True,
                "alert_on_slow_endpoints": True,
                "rate_limit_alerts": True
            },
            optimization_settings={
                "auto_caching": True,
                "query_optimization": True,
                "connection_pooling": True,
                "response_compression": True
            },
            custom_settings={
                "api_specific": {
                    "track_api_versions": True,
                    "monitor_rate_limits": True,
                    "track_client_usage": True,
                    "api_key_analytics": True
                }
            }
        )
        
        profiles["web_api_enterprise"] = ConfigProfile(
            name="Web API - Корпоративный",
            project_type=ProjectType.WEB_API,
            scale_profile=ScaleProfile.ENTERPRISE,
            components={
                "mcp_monitor": True,
                "alert_system": True,
                "performance_tracker": True,
                "cache_manager": True,
                "auto_reporter": True,
                "optimizer_ai": True,
                "self_optimizer": True
            },
            monitoring_settings={
                "track_endpoints": True,
                "track_response_times": True,
                "track_status_codes": True,
                "track_request_body_size": True,
                "track_auth_failures": True,
                "response_time_threshold": 0.5,
                "track_database_queries": True,
                "distributed_tracing": True,
                "apm_integration": True,
                "track_sla_compliance": True
            },
            alert_settings={
                "pagerduty_integration": True,
                "slack_notifications": True,
                "email_notifications": True,
                "alert_on_5xx_errors": True,
                "alert_on_4xx_surge": True,
                "alert_on_slow_endpoints": True,
                "rate_limit_alerts": True,
                "sla_breach_alerts": True,
                "predictive_alerts": True
            },
            optimization_settings={
                "auto_caching": True,
                "query_optimization": True,
                "connection_pooling": True,
                "response_compression": True,
                "auto_scaling": True,
                "load_balancing": True,
                "circuit_breaker": True,
                "adaptive_throttling": True
            },
            custom_settings={
                "api_specific": {
                    "track_api_versions": True,
                    "monitor_rate_limits": True,
                    "track_client_usage": True,
                    "api_key_analytics": True,
                    "geo_analytics": True,
                    "business_metrics": True,
                    "cost_tracking": True
                }
            }
        )
        
        # ===== CLI TOOL PROFILES =====
        profiles["cli_tool_minimal"] = ConfigProfile(
            name="CLI Tool - Минимальный",
            project_type=ProjectType.CLI_TOOL,
            scale_profile=ScaleProfile.MINIMAL,
            components={
                "mcp_monitor": True,
                "alert_system": False,
                "performance_tracker": False,
                "cache_manager": False,
                "auto_reporter": False,
                "optimizer_ai": False,
                "self_optimizer": False
            },
            monitoring_settings={
                "track_commands": True,
                "track_execution_time": True,
                "track_errors": True,
                "log_to_file": True,
                "response_time_threshold": 10.0
            },
            alert_settings={
                "console_alerts": True,
                "log_file_alerts": True
            },
            optimization_settings={
                "command_caching": False,
                "parallel_execution": False
            },
            custom_settings={
                "cli_specific": {
                    "track_user_commands": True,
                    "usage_statistics": True,
                    "error_reporting": True
                }
            }
        )
        
        # ===== DATA PIPELINE PROFILES =====
        profiles["data_pipeline_standard"] = ConfigProfile(
            name="Data Pipeline - Стандартный",
            project_type=ProjectType.DATA_PIPELINE,
            scale_profile=ScaleProfile.STANDARD,
            components={
                "mcp_monitor": True,
                "alert_system": True,
                "performance_tracker": True,
                "cache_manager": False,
                "auto_reporter": True,
                "optimizer_ai": True,
                "self_optimizer": False
            },
            monitoring_settings={
                "track_pipeline_stages": True,
                "track_data_volume": True,
                "track_processing_time": True,
                "track_error_rate": True,
                "track_data_quality": True,
                "checkpoint_monitoring": True,
                "response_time_threshold": 60.0
            },
            alert_settings={
                "email_notifications": True,
                "slack_notifications": True,
                "alert_on_pipeline_failure": True,
                "alert_on_data_quality": True,
                "alert_on_sla_breach": True,
                "anomaly_detection": True
            },
            optimization_settings={
                "auto_retry": True,
                "batch_size_optimization": True,
                "parallel_processing": True,
                "resource_optimization": True
            },
            custom_settings={
                "pipeline_specific": {
                    "track_data_lineage": True,
                    "monitor_data_freshness": True,
                    "track_schema_changes": True,
                    "cost_per_run": True
                }
            }
        )
        
        # ===== MICROSERVICE PROFILES =====
        profiles["microservice_standard"] = ConfigProfile(
            name="Microservice - Стандартный",
            project_type=ProjectType.MICROSERVICE,
            scale_profile=ScaleProfile.STANDARD,
            components={
                "mcp_monitor": True,
                "alert_system": True,
                "performance_tracker": True,
                "cache_manager": True,
                "auto_reporter": True,
                "optimizer_ai": False,
                "self_optimizer": False
            },
            monitoring_settings={
                "track_grpc_calls": True,
                "track_http_calls": True,
                "track_message_queue": True,
                "distributed_tracing": True,
                "service_mesh_integration": True,
                "response_time_threshold": 0.1,
                "circuit_breaker_monitoring": True
            },
            alert_settings={
                "prometheus_integration": True,
                "alert_manager": True,
                "service_degradation": True,
                "dependency_failure": True,
                "resource_alerts": True
            },
            optimization_settings={
                "connection_pooling": True,
                "request_batching": True,
                "cache_coordination": True,
                "auto_scaling": True
            },
            custom_settings={
                "microservice_specific": {
                    "service_discovery": True,
                    "health_checks": True,
                    "graceful_shutdown": True,
                    "version_tracking": True
                }
            }
        )
        
        # ===== ML SERVICE PROFILES =====
        profiles["ml_service_advanced"] = ConfigProfile(
            name="ML Service - Продвинутый",
            project_type=ProjectType.ML_SERVICE,
            scale_profile=ScaleProfile.ADVANCED,
            components={
                "mcp_monitor": True,
                "alert_system": True,
                "performance_tracker": True,
                "cache_manager": True,
                "auto_reporter": True,
                "optimizer_ai": True,
                "self_optimizer": True
            },
            monitoring_settings={
                "track_inference_time": True,
                "track_model_accuracy": True,
                "track_data_drift": True,
                "track_resource_usage": True,
                "track_batch_processing": True,
                "gpu_monitoring": True,
                "response_time_threshold": 0.5
            },
            alert_settings={
                "accuracy_degradation": True,
                "data_drift_alerts": True,
                "resource_exhaustion": True,
                "model_version_alerts": True,
                "gpu_utilization": True
            },
            optimization_settings={
                "model_caching": True,
                "batch_optimization": True,
                "gpu_scheduling": True,
                "model_quantization": True,
                "auto_model_selection": True
            },
            custom_settings={
                "ml_specific": {
                    "experiment_tracking": True,
                    "model_versioning": True,
                    "a_b_testing": True,
                    "feature_importance": True,
                    "explainability": True
                }
            }
        )
        
        return profiles
    
    def get_profile(self, profile_name: str) -> Optional[ConfigProfile]:
        """Получение профиля по имени"""
        # Проверка в кэше
        if profile_name in self.loaded_profiles:
            return self.loaded_profiles[profile_name]
        
        # Проверка в базовых профилях
        if profile_name in self.base_profiles:
            profile = self.base_profiles[profile_name]
            self.loaded_profiles[profile_name] = profile
            return profile
        
        # Попытка загрузки из файла
        profile_file = self.profiles_dir / f"{profile_name}.json"
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                profile = ConfigProfile(**profile_data)
                self.loaded_profiles[profile_name] = profile
                return profile
            except Exception as e:
                print(f"⚠️ Ошибка загрузки профиля {profile_name}: {e}")
        
        return None
    
    def create_custom_profile(self, base_profile_name: str, 
                            custom_settings: Dict[str, Any]) -> ConfigProfile:
        """Создание кастомного профиля на основе базового"""
        base_profile = self.get_profile(base_profile_name)
        if not base_profile:
            raise ValueError(f"Базовый профиль {base_profile_name} не найден")
        
        # Создание копии базового профиля
        custom_profile = ConfigProfile(
            name=f"{base_profile.name} (Custom)",
            project_type=base_profile.project_type,
            scale_profile=base_profile.scale_profile,
            components=base_profile.components.copy(),
            monitoring_settings=base_profile.monitoring_settings.copy(),
            alert_settings=base_profile.alert_settings.copy(),
            optimization_settings=base_profile.optimization_settings.copy(),
            custom_settings=base_profile.custom_settings.copy()
        )
        
        # Применение кастомных настроек
        for key, value in custom_settings.items():
            if key == "components":
                custom_profile.components.update(value)
            elif key == "monitoring_settings":
                custom_profile.monitoring_settings.update(value)
            elif key == "alert_settings":
                custom_profile.alert_settings.update(value)
            elif key == "optimization_settings":
                custom_profile.optimization_settings.update(value)
            elif key == "custom_settings":
                custom_profile.custom_settings.update(value)
        
        return custom_profile
    
    def save_profile(self, profile: ConfigProfile, profile_name: str):
        """Сохранение профиля в файл"""
        profile_file = self.profiles_dir / f"{profile_name}.json"
        
        profile_data = asdict(profile)
        # Конвертация Enum в строки
        profile_data["project_type"] = profile.project_type.value
        profile_data["scale_profile"] = profile.scale_profile.value
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Профиль сохранен: {profile_file}")
    
    def generate_config_from_profile(self, profile: ConfigProfile) -> Dict[str, Any]:
        """Генерация конфигурации из профиля"""
        config = {
            "framework": {
                "project_type": profile.project_type.value,
                "scale_profile": profile.scale_profile.value,
                "components": profile.components
            },
            "monitoring": profile.monitoring_settings,
            "alerts": profile.alert_settings,
            "optimization": profile.optimization_settings,
            "custom": profile.custom_settings
        }
        
        return config
    
    def recommend_profile(self, project_type: ProjectType, 
                         requirements: Dict[str, Any]) -> str:
        """Рекомендация профиля на основе требований"""
        suitable_profiles = []
        
        # Фильтрация по типу проекта
        for profile_name, profile in self.base_profiles.items():
            if profile.project_type == project_type:
                score = self._calculate_profile_score(profile, requirements)
                suitable_profiles.append((profile_name, score))
        
        # Сортировка по score
        suitable_profiles.sort(key=lambda x: x[1], reverse=True)
        
        if suitable_profiles:
            return suitable_profiles[0][0]
        
        return "web_api_standard"  # Профиль по умолчанию
    
    def _calculate_profile_score(self, profile: ConfigProfile, 
                               requirements: Dict[str, Any]) -> float:
        """Расчет соответствия профиля требованиям"""
        score = 0.0
        
        # Проверка масштаба
        if "scale" in requirements:
            if requirements["scale"] == profile.scale_profile.value:
                score += 10.0
        
        # Проверка необходимых компонентов
        if "required_components" in requirements:
            for component in requirements["required_components"]:
                if profile.components.get(component, False):
                    score += 5.0
                else:
                    score -= 5.0
        
        # Проверка производительности
        if "response_time" in requirements:
            profile_threshold = profile.monitoring_settings.get("response_time_threshold", 10.0)
            if profile_threshold <= requirements["response_time"]:
                score += 3.0
        
        # Проверка возможностей оптимизации
        if "auto_optimization" in requirements and requirements["auto_optimization"]:
            if profile.components.get("optimizer_ai", False):
                score += 7.0
        
        return score
    
    def list_profiles(self, project_type: Optional[ProjectType] = None) -> List[str]:
        """Список доступных профилей"""
        profiles = []
        
        # Базовые профили
        for profile_name, profile in self.base_profiles.items():
            if project_type is None or profile.project_type == project_type:
                profiles.append(profile_name)
        
        # Сохраненные профили
        for profile_file in self.profiles_dir.glob("*.json"):
            profile_name = profile_file.stem
            if profile_name not in profiles:
                profiles.append(profile_name)
        
        return sorted(profiles)
    
    def export_profile_documentation(self, output_file: str = "profiles_documentation.md"):
        """Экспорт документации по всем профилям"""
        doc_lines = ["# Профили конфигурации Claude MultiAgent Framework\n"]
        
        # Группировка по типам проектов
        by_project_type = {}
        for profile_name, profile in self.base_profiles.items():
            project_type = profile.project_type.value
            if project_type not in by_project_type:
                by_project_type[project_type] = []
            by_project_type[project_type].append(profile)
        
        # Генерация документации
        for project_type, profiles in by_project_type.items():
            doc_lines.append(f"\n## {project_type.replace('_', ' ').title()}\n")
            
            for profile in profiles:
                doc_lines.append(f"### {profile.name}\n")
                doc_lines.append(f"**Масштаб:** {profile.scale_profile.value}\n")
                
                # Компоненты
                enabled_components = [k for k, v in profile.components.items() if v]
                doc_lines.append(f"**Включенные компоненты:** {', '.join(enabled_components)}\n")
                
                # Основные настройки
                doc_lines.append("\n**Основные настройки мониторинга:**")
                for key, value in list(profile.monitoring_settings.items())[:5]:
                    doc_lines.append(f"- {key}: {value}")
                
                doc_lines.append("\n**Настройки оповещений:**")
                for key, value in list(profile.alert_settings.items())[:5]:
                    doc_lines.append(f"- {key}: {value}")
                
                doc_lines.append("\n---\n")
        
        # Сохранение документации
        output_path = Path(output_file)
        output_path.write_text("\n".join(doc_lines))
        
        print(f"📚 Документация сохранена: {output_file}")
        return output_file

# Глобальный менеджер профилей
profile_manager = ConfigProfileManager()

def get_config_for_project(project_type: str, scale: str = "standard",
                          custom_settings: Dict[str, Any] = None) -> Dict[str, Any]:
    """Получение конфигурации для типа проекта"""
    profile_name = f"{project_type}_{scale}"
    
    profile = profile_manager.get_profile(profile_name)
    if not profile:
        # Поиск подходящего профиля
        requirements = {"scale": scale}
        if custom_settings:
            requirements.update(custom_settings)
        
        profile_name = profile_manager.recommend_profile(
            ProjectType(project_type), requirements
        )
        profile = profile_manager.get_profile(profile_name)
    
    if profile:
        config = profile_manager.generate_config_from_profile(profile)
        
        # Применение кастомных настроек
        if custom_settings:
            for key, value in custom_settings.items():
                if key in config:
                    config[key].update(value)
        
        return config
    
    return {}

def create_project_config(project_name: str, project_type: str,
                         scale: str = "standard",
                         custom_requirements: Dict[str, Any] = None) -> str:
    """Создание конфигурации проекта с профилем"""
    print(f"🔧 [Архитектор] Создание конфигурации для {project_name}")
    print(f"   Тип: {project_type}")
    print(f"   Масштаб: {scale}")
    
    # Получение конфигурации
    config = get_config_for_project(project_type, scale, custom_requirements)
    
    # Добавление метаданных проекта
    config["project"] = {
        "name": project_name,
        "type": project_type,
        "scale": scale,
        "created": "2025-07-11",
        "framework_version": "1.0.0"
    }
    
    # Сохранение конфигурации
    config_file = f"generated_configs/{project_name}_config.json"
    config_path = Path(config_file)
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Конфигурация создана: {config_file}")
    return config_file

if __name__ == "__main__":
    # Демонстрация системы профилей
    print("🎯 Демонстрация системы профилей конфигурации\n")
    
    # Список доступных профилей
    print("📋 Доступные профили:")
    for profile_name in profile_manager.list_profiles():
        profile = profile_manager.get_profile(profile_name)
        if profile:
            print(f"  • {profile_name} - {profile.scale_profile.value}")
    
    # Создание примеров конфигураций
    print("\n🏗️ Создание примеров конфигураций:")
    
    # Telegram бот
    create_project_config(
        "MyTelegramBot",
        "telegram_bot",
        "advanced",
        {"bot_token_monitoring": True}
    )
    
    # Web API
    create_project_config(
        "MyWebAPI", 
        "web_api",
        "enterprise",
        {"kubernetes_integration": True}
    )
    
    # ML сервис
    create_project_config(
        "MyMLService",
        "ml_service", 
        "advanced",
        {"model_explainability": True}
    )
    
    # Экспорт документации
    profile_manager.export_profile_documentation()