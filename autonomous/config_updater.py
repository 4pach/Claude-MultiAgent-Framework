#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Updater - Безопасная система обновления конфигураций
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import shutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib
import jsonschema
from jsonschema import validate, ValidationError

class ConfigUpdateType(Enum):
    """Типы обновления конфигурации"""
    THRESHOLD_ADJUSTMENT = "threshold_adjustment"
    CACHE_SETTINGS = "cache_settings" 
    ALERT_RULES = "alert_rules"
    PERFORMANCE_TUNING = "performance_tuning"
    MONITORING_CONFIG = "monitoring_config"
    REPORT_SETTINGS = "report_settings"

class UpdateStatus(Enum):
    """Статусы обновления конфигурации"""
    PENDING = "pending"
    VALIDATING = "validating"
    APPLYING = "applying"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class ConfigBackup:
    """Резервная копия конфигурации"""
    backup_id: str
    config_file: str
    original_content: Dict[str, Any]
    backup_timestamp: datetime
    applied_changes: Dict[str, Any]
    checksum: str

@dataclass 
class ConfigUpdate:
    """Обновление конфигурации"""
    update_id: str
    config_file: str
    update_type: ConfigUpdateType
    changes: Dict[str, Any]
    validation_schema: Optional[Dict] = None
    rollback_timeout: timedelta = timedelta(minutes=30)
    status: UpdateStatus = UpdateStatus.PENDING
    created_at: datetime = None
    applied_at: Optional[datetime] = None
    backup_id: Optional[str] = None
    error_message: Optional[str] = None

class ConfigValidator:
    """Валидатор конфигураций"""
    
    def __init__(self):
        self.schemas = self.init_validation_schemas()
    
    def init_validation_schemas(self) -> Dict[str, Dict]:
        """Инициализация схем валидации для различных конфигураций"""
        return {
            "monitoring/mcp_monitor_config.json": {
                "type": "object",
                "properties": {
                    "cache": {
                        "type": "object",
                        "properties": {
                            "max_size_mb": {"type": "number", "minimum": 1, "maximum": 1000},
                            "ttl_hours": {"type": "number", "minimum": 0.1, "maximum": 168}
                        }
                    },
                    "performance": {
                        "type": "object", 
                        "properties": {
                            "max_response_time": {"type": "number", "minimum": 1, "maximum": 300},
                            "max_tokens_per_request": {"type": "integer", "minimum": 50, "maximum": 5000}
                        }
                    }
                }
            },
            "monitoring/alert_config.json": {
                "type": "object",
                "properties": {
                    "thresholds": {
                        "type": "object",
                        "properties": {
                            "max_response_time": {"type": "number", "minimum": 1, "maximum": 60},
                            "max_tokens_per_request": {"type": "integer", "minimum": 100, "maximum": 2000},
                            "min_success_rate": {"type": "number", "minimum": 0.5, "maximum": 1.0}
                        }
                    }
                }
            },
            "reports/report_config.json": {
                "type": "object", 
                "properties": {
                    "schedule": {
                        "type": "object",
                        "properties": {
                            "daily_report": {"type": "string", "pattern": "^[0-2][0-9]:[0-5][0-9]$"},
                            "weekly_report": {"type": "string"},
                            "monthly_report": {"type": "string"}
                        }
                    }
                }
            }
        }
    
    def validate_config(self, config_file: str, config_data: Dict) -> tuple[bool, Optional[str]]:
        """Валидация конфигурации по схеме"""
        schema = self.schemas.get(config_file)
        if not schema:
            # Базовая валидация для неизвестных файлов
            if not isinstance(config_data, dict):
                return False, "Конфигурация должна быть объектом JSON"
            return True, None
        
        try:
            validate(instance=config_data, schema=schema)
            return True, None
        except ValidationError as e:
            return False, f"Ошибка валидации: {e.message}"
    
    def validate_business_logic(self, config_file: str, config_data: Dict) -> tuple[bool, Optional[str]]:
        """Валидация бизнес-логики конфигурации"""
        
        # Специальная валидация для конфигурации алертов
        if "alert_config.json" in config_file:
            thresholds = config_data.get("thresholds", {})
            
            # Проверка логической последовательности порогов
            max_response = thresholds.get("max_response_time", 10)
            max_tokens = thresholds.get("max_tokens_per_request", 1000)
            
            if max_response < 1:
                return False, "Максимальное время ответа не может быть меньше 1 секунды"
            
            if max_tokens < 50:
                return False, "Минимальный лимит токенов не может быть меньше 50"
        
        # Валидация кэш-конфигурации
        elif "mcp_monitor_config.json" in config_file:
            cache_config = config_data.get("cache", {})
            
            max_size = cache_config.get("max_size_mb", 100)
            ttl_hours = cache_config.get("ttl_hours", 24)
            
            if max_size > 500:
                return False, "Размер кэша не должен превышать 500MB для стабильной работы"
            
            if ttl_hours > 168:  # 7 дней
                return False, "TTL кэша не должен превышать 7 дней"
        
        # Валидация расписания отчетов
        elif "report_config.json" in config_file:
            schedule = config_data.get("schedule", {})
            daily_time = schedule.get("daily_report", "09:00")
            
            try:
                hour, minute = map(int, daily_time.split(":"))
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    return False, "Неверный формат времени для ежедневного отчета"
            except ValueError:
                return False, "Время должно быть в формате HH:MM"
        
        return True, None

class ConfigUpdater:
    """Система безопасного обновления конфигураций"""
    
    def __init__(self, config_dir: str = ".", backup_dir: str = "autonomous/config_backups"):
        self.config_dir = Path(config_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Активные обновления и резервные копии
        self.active_updates: Dict[str, ConfigUpdate] = {}
        self.backups: Dict[str, ConfigBackup] = {}
        
        # Валидатор конфигураций
        self.validator = ConfigValidator()
        
        # Настройки системы
        self.config = self.load_updater_config()
        
        # Мониторинг автоматического отката
        self.rollback_monitor = threading.Thread(target=self._rollback_monitor, daemon=True)
        self.rollback_monitor.start()
        
        # Callbacks для уведомлений
        self.update_callbacks: List[Callable] = []
        
        print("🔧 Config Updater инициализирован")
    
    def load_updater_config(self) -> Dict:
        """Загрузка конфигурации системы обновлений"""
        config_file = self.backup_dir / "updater_config.json"
        
        default_config = {
            "safety": {
                "require_validation": True,
                "auto_rollback_on_error": True,
                "max_concurrent_updates": 3,
                "backup_retention_days": 30
            },
            "validation": {
                "strict_mode": True,
                "business_logic_checks": True,
                "dry_run_before_apply": True
            },
            "monitoring": {
                "track_performance_impact": True,
                "alert_on_config_errors": True,
                "log_all_changes": True
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Объединение с настройками по умолчанию
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except Exception as e:
                print(f"⚠️ Ошибка загрузки конфигурации updater: {e}")
        
        # Сохранение конфигурации по умолчанию
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def create_backup(self, config_file: str, applied_changes: Dict[str, Any]) -> str:
        """Создание резервной копии конфигурации"""
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"Конфигурационный файл не найден: {config_file}")
        
        # Чтение текущего содержимого
        with open(config_path, 'r', encoding='utf-8') as f:
            original_content = json.load(f)
        
        # Создание ID и метаданных для бэкапа
        backup_id = f"backup_{config_file.replace('/', '_')}_{int(time.time())}"
        timestamp = datetime.now()
        
        # Вычисление контрольной суммы
        content_str = json.dumps(original_content, sort_keys=True)
        checksum = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Создание объекта резервной копии
        backup = ConfigBackup(
            backup_id=backup_id,
            config_file=config_file,
            original_content=original_content,
            backup_timestamp=timestamp,
            applied_changes=applied_changes,
            checksum=checksum
        )
        
        # Сохранение резервной копии на диск
        backup_file = self.backup_dir / f"{backup_id}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': asdict(backup),
                'original_content': original_content
            }, f, ensure_ascii=False, indent=2, default=str)
        
        self.backups[backup_id] = backup
        
        print(f"💾 Создана резервная копия: {backup_id}")
        return backup_id
    
    def apply_config_update(self, update: ConfigUpdate) -> bool:
        """Применение обновления конфигурации"""
        try:
            update.status = UpdateStatus.VALIDATING
            
            # Создание резервной копии
            backup_id = self.create_backup(update.config_file, update.changes)
            update.backup_id = backup_id
            
            config_path = self.config_dir / update.config_file
            
            # Загрузка текущей конфигурации
            with open(config_path, 'r', encoding='utf-8') as f:
                current_config = json.load(f)
            
            # Применение изменений
            updated_config = self._apply_changes(current_config, update.changes)
            
            # Валидация обновленной конфигурации
            if self.config["validation"]["require_validation"]:
                is_valid, error_msg = self.validator.validate_config(
                    update.config_file, updated_config
                )
                if not is_valid:
                    update.status = UpdateStatus.FAILED
                    update.error_message = f"Валидация схемы: {error_msg}"
                    return False
                
                # Валидация бизнес-логики
                if self.config["validation"]["business_logic_checks"]:
                    is_valid, error_msg = self.validator.validate_business_logic(
                        update.config_file, updated_config
                    )
                    if not is_valid:
                        update.status = UpdateStatus.FAILED
                        update.error_message = f"Валидация логики: {error_msg}"
                        return False
            
            # Dry run режим (если включен)
            if self.config["validation"]["dry_run_before_apply"]:
                print(f"🧪 Dry run для {update.config_file}: валидация прошла успешно")
            
            # Применение изменений
            update.status = UpdateStatus.APPLYING
            
            # Создание временного файла
            temp_file = config_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(updated_config, f, ensure_ascii=False, indent=2)
            
            # Атомарная замена файла
            shutil.move(str(temp_file), str(config_path))
            
            # Обновление статуса
            update.status = UpdateStatus.APPLIED
            update.applied_at = datetime.now()
            
            # Уведомление о применении
            print(f"✅ Конфигурация обновлена: {update.config_file}")
            self._notify_callbacks(update)
            
            # Запуск мониторинга для автоматического отката
            if self.config["safety"]["auto_rollback_on_error"]:
                self.active_updates[update.update_id] = update
            
            return True
            
        except Exception as e:
            update.status = UpdateStatus.FAILED
            update.error_message = str(e)
            print(f"❌ Ошибка применения конфигурации: {e}")
            return False
    
    def _apply_changes(self, config: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Применение изменений к конфигурации"""
        updated_config = config.copy()
        
        for path, value in changes.items():
            # Обработка вложенных путей (например, "cache.max_size_mb")
            keys = path.split('.')
            current = updated_config
            
            # Навигация до родительского объекта
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Установка значения
            final_key = keys[-1]
            
            # Специальная обработка для некоторых операций
            if isinstance(value, dict) and '_operation' in value:
                operation = value['_operation']
                actual_value = value['value']
                
                if operation == 'increment':
                    current[final_key] = current.get(final_key, 0) + actual_value
                elif operation == 'multiply':
                    current[final_key] = current.get(final_key, 1) * actual_value
                elif operation == 'append':
                    if final_key not in current:
                        current[final_key] = []
                    current[final_key].append(actual_value)
                else:
                    current[final_key] = actual_value
            else:
                current[final_key] = value
        
        return updated_config
    
    def rollback_update(self, update_id: str) -> bool:
        """Откат обновления конфигурации"""
        if update_id not in self.active_updates:
            print(f"❌ Обновление {update_id} не найдено или уже завершено")
            return False
        
        update = self.active_updates[update_id]
        
        if not update.backup_id or update.backup_id not in self.backups:
            print(f"❌ Резервная копия для {update_id} не найдена")
            return False
        
        try:
            backup = self.backups[update.backup_id]
            config_path = self.config_dir / update.config_file
            
            # Восстановление из резервной копии
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(backup.original_content, f, ensure_ascii=False, indent=2)
            
            # Обновление статуса
            update.status = UpdateStatus.ROLLED_BACK
            
            # Удаление из активных обновлений
            del self.active_updates[update_id]
            
            print(f"🔄 Выполнен откат конфигурации: {update.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отката: {e}")
            return False
    
    def _rollback_monitor(self):
        """Фоновый мониторинг для автоматического отката"""
        while True:
            try:
                current_time = datetime.now()
                expired_updates = []
                
                for update_id, update in self.active_updates.items():
                    if (update.applied_at and 
                        current_time - update.applied_at > update.rollback_timeout):
                        expired_updates.append(update_id)
                
                # Автоматический откат просроченных обновлений
                for update_id in expired_updates:
                    update = self.active_updates[update_id]
                    print(f"⏰ Автоматический откат по таймауту: {update.config_file}")
                    self.rollback_update(update_id)
                
                time.sleep(60)  # Проверка каждую минуту
                
            except Exception as e:
                print(f"⚠️ Ошибка в мониторе отката: {e}")
                time.sleep(60)
    
    def create_config_update(self, config_file: str, update_type: ConfigUpdateType,
                           changes: Dict[str, Any], rollback_timeout: timedelta = None) -> str:
        """Создание обновления конфигурации"""
        
        # Проверка лимита одновременных обновлений
        if len(self.active_updates) >= self.config["safety"]["max_concurrent_updates"]:
            raise RuntimeError("Превышен лимит одновременных обновлений конфигурации")
        
        update_id = f"update_{config_file.replace('/', '_')}_{int(time.time())}"
        
        update = ConfigUpdate(
            update_id=update_id,
            config_file=config_file,
            update_type=update_type,
            changes=changes,
            rollback_timeout=rollback_timeout or timedelta(minutes=30),
            created_at=datetime.now()
        )
        
        return update_id, update
    
    def execute_config_update(self, config_file: str, update_type: ConfigUpdateType,
                            changes: Dict[str, Any], rollback_timeout: timedelta = None) -> bool:
        """Выполнение полного цикла обновления конфигурации"""
        
        try:
            # Создание обновления
            update_id, update = self.create_config_update(
                config_file, update_type, changes, rollback_timeout
            )
            
            print(f"🔧 Начинаю обновление конфигурации: {config_file}")
            print(f"   Тип: {update_type.value}")
            print(f"   Изменения: {len(changes)} параметров")
            
            # Применение обновления
            success = self.apply_config_update(update)
            
            if success:
                print(f"✅ Обновление {update_id} успешно применено")
                
                # Логирование изменений
                if self.config["monitoring"]["log_all_changes"]:
                    self._log_config_change(update)
                
                return True
            else:
                print(f"❌ Обновление {update_id} не удалось: {update.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Критическая ошибка обновления конфигурации: {e}")
            return False
    
    def _log_config_change(self, update: ConfigUpdate):
        """Логирование изменения конфигурации"""
        log_file = Path("logs") / "config_changes.log"
        log_file.parent.mkdir(exist_ok=True)
        
        log_entry = {
            'timestamp': update.applied_at.isoformat() if update.applied_at else None,
            'update_id': update.update_id,
            'config_file': update.config_file,
            'update_type': update.update_type.value,
            'changes': update.changes,
            'status': update.status.value,
            'backup_id': update.backup_id
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
    
    def _notify_callbacks(self, update: ConfigUpdate):
        """Уведомление callback'ов об изменении конфигурации"""
        for callback in self.update_callbacks:
            try:
                callback(update)
            except Exception as e:
                print(f"⚠️ Ошибка в config update callback: {e}")
    
    def add_update_callback(self, callback: Callable):
        """Добавление callback для уведомлений об обновлениях"""
        self.update_callbacks.append(callback)
    
    def get_active_updates(self) -> List[ConfigUpdate]:
        """Получение списка активных обновлений"""
        return list(self.active_updates.values())
    
    def get_backup_history(self, config_file: Optional[str] = None) -> List[ConfigBackup]:
        """Получение истории резервных копий"""
        backups = list(self.backups.values())
        
        if config_file:
            backups = [b for b in backups if b.config_file == config_file]
        
        return sorted(backups, key=lambda b: b.backup_timestamp, reverse=True)
    
    def cleanup_old_backups(self, days: int = None):
        """Очистка старых резервных копий"""
        days = days or self.config["safety"]["backup_retention_days"]
        cutoff_date = datetime.now() - timedelta(days=days)
        
        old_backups = []
        for backup_id, backup in list(self.backups.items()):
            if backup.backup_timestamp < cutoff_date:
                old_backups.append(backup_id)
                
                # Удаление файла резервной копии
                backup_file = self.backup_dir / f"{backup_id}.json"
                if backup_file.exists():
                    backup_file.unlink()
                
                del self.backups[backup_id]
        
        if old_backups:
            print(f"🧹 Удалено {len(old_backups)} старых резервных копий")
        
        return len(old_backups)
    
    def get_config_update_stats(self) -> Dict[str, Any]:
        """Статистика обновлений конфигурации"""
        total_backups = len(self.backups)
        active_updates = len(self.active_updates)
        
        # Анализ истории обновлений из логов
        log_file = Path("logs") / "config_changes.log"
        recent_updates = 0
        successful_updates = 0
        
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get('timestamp'):
                            timestamp = datetime.fromisoformat(entry['timestamp'])
                            if (datetime.now() - timestamp).days < 7:
                                recent_updates += 1
                                if entry.get('status') == 'applied':
                                    successful_updates += 1
            except Exception as e:
                print(f"⚠️ Ошибка анализа логов: {e}")
        
        return {
            'total_backups': total_backups,
            'active_updates': active_updates,
            'recent_updates_7d': recent_updates,
            'successful_updates_7d': successful_updates,
            'success_rate': successful_updates / max(recent_updates, 1),
            'backup_retention_days': self.config["safety"]["backup_retention_days"]
        }

# Глобальный экземпляр системы обновления конфигураций
config_updater = ConfigUpdater()

# Удобные функции для типичных обновлений конфигурации
def update_cache_settings(max_size_mb: int = None, ttl_hours: float = None) -> bool:
    """Обновление настроек кэша"""
    changes = {}
    if max_size_mb is not None:
        changes["cache.max_size_mb"] = max_size_mb
    if ttl_hours is not None:
        changes["cache.ttl_hours"] = ttl_hours
    
    if not changes:
        print("❌ Не указаны параметры для обновления")
        return False
    
    return config_updater.execute_config_update(
        "monitoring/mcp_monitor_config.json",
        ConfigUpdateType.CACHE_SETTINGS,
        changes
    )

def update_alert_thresholds(max_response_time: float = None, 
                          max_tokens: int = None,
                          min_success_rate: float = None) -> bool:
    """Обновление порогов предупреждений"""
    changes = {}
    if max_response_time is not None:
        changes["thresholds.max_response_time"] = max_response_time
    if max_tokens is not None:
        changes["thresholds.max_tokens_per_request"] = max_tokens
    if min_success_rate is not None:
        changes["thresholds.min_success_rate"] = min_success_rate
    
    if not changes:
        print("❌ Не указаны параметры для обновления")
        return False
    
    return config_updater.execute_config_update(
        "monitoring/alert_config.json",
        ConfigUpdateType.ALERT_RULES,
        changes
    )

def update_report_schedule(daily_time: str = None, 
                         weekly_day: str = None,
                         monthly_day: str = None) -> bool:
    """Обновление расписания отчетов"""
    changes = {}
    if daily_time is not None:
        changes["schedule.daily_report"] = daily_time
    if weekly_day is not None:
        changes["schedule.weekly_report"] = weekly_day
    if monthly_day is not None:
        changes["schedule.monthly_report"] = monthly_day
    
    if not changes:
        print("❌ Не указаны параметры для обновления")
        return False
    
    return config_updater.execute_config_update(
        "reports/report_config.json",
        ConfigUpdateType.REPORT_SETTINGS,
        changes
    )

def rollback_config(update_id: str) -> bool:
    """Откат конфигурации по ID обновления"""
    return config_updater.rollback_update(update_id)

def show_active_updates():
    """Показать активные обновления конфигурации"""
    updates = config_updater.get_active_updates()
    
    if not updates:
        print("📭 Нет активных обновлений конфигурации")
        return
    
    print(f"\n🔧 === АКТИВНЫЕ ОБНОВЛЕНИЯ ({len(updates)}) ===")
    for update in updates:
        status_emoji = {
            UpdateStatus.PENDING: "⏳",
            UpdateStatus.VALIDATING: "🔍", 
            UpdateStatus.APPLYING: "⚙️",
            UpdateStatus.APPLIED: "✅",
            UpdateStatus.FAILED: "❌"
        }
        
        emoji = status_emoji.get(update.status, "❓")
        age = (datetime.now() - update.created_at).total_seconds() / 60
        
        print(f"{emoji} {update.update_id}")
        print(f"   📁 {update.config_file}")
        print(f"   🏷️ {update.update_type.value}")
        print(f"   ⏰ {age:.1f} минут назад")
        if update.applied_at:
            timeout_in = (update.applied_at + update.rollback_timeout - datetime.now()).total_seconds() / 60
            print(f"   🔄 Откат через: {timeout_in:.1f} минут")
        print()

def config_stats():
    """Показать статистику конфигурационных обновлений"""
    stats = config_updater.get_config_update_stats()
    
    print("\n📊 === СТАТИСТИКА КОНФИГУРАЦИЙ ===")
    print(f"💾 Резервных копий: {stats['total_backups']}")
    print(f"🔧 Активных обновлений: {stats['active_updates']}")
    print(f"📈 Обновлений за 7 дней: {stats['recent_updates_7d']}")
    print(f"✅ Успешных обновлений: {stats['successful_updates_7d']}")
    print(f"🎯 Процент успеха: {stats['success_rate']:.1%}")
    print(f"🗂️ Хранение копий: {stats['backup_retention_days']} дней")
    print("="*45)

if __name__ == "__main__":
    # Демонстрация системы обновления конфигураций
    print("🔧 Config Updater инициализирован")
    
    print("\n🎮 Доступные команды:")
    print("  update_cache_settings(max_size_mb, ttl_hours)")
    print("  update_alert_thresholds(max_response_time, max_tokens, min_success_rate)")
    print("  update_report_schedule(daily_time, weekly_day, monthly_day)")
    print("  rollback_config(update_id)")
    print("  show_active_updates()")
    print("  config_stats()")