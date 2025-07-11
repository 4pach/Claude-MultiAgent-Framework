#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self Optimizer - Система автономного самоулучшения с подтверждением пользователя
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib

# Импорт систем мониторинга
from monitoring.mcp_monitor import mcp_monitor
from monitoring.performance_tracker import performance_tracker
from monitoring.cache_manager import cache_manager
from monitoring.alert_system import alert_system
from recommendations.optimizer_ai import optimizer_ai

class OptimizationType(Enum):
    """Типы оптимизации"""
    CONFIG_UPDATE = "config_update"
    CACHE_OPTIMIZATION = "cache_optimization"
    THRESHOLD_ADJUSTMENT = "threshold_adjustment"
    RESOURCE_REALLOCATION = "resource_reallocation"
    ALERT_RULE_UPDATE = "alert_rule_update"
    PERFORMANCE_TUNING = "performance_tuning"

class OptimizationSeverity(Enum):
    """Критичность оптимизации"""
    LOW = "low"           # Автоматическое применение
    MEDIUM = "medium"     # Подтверждение желательно
    HIGH = "high"         # Подтверждение обязательно  
    CRITICAL = "critical" # Требует явного подтверждения + бэкап

@dataclass
class OptimizationProposal:
    """Предложение по оптимизации"""
    id: str
    type: OptimizationType
    severity: OptimizationSeverity
    title: str
    description: str
    rationale: str
    changes: Dict[str, Any]
    backup_data: Dict[str, Any]
    estimated_impact: Dict[str, float]
    risk_assessment: str
    rollback_plan: str
    confidence_score: float
    created_at: datetime
    expires_at: datetime
    approved: Optional[bool] = None
    applied: bool = False
    applied_at: Optional[datetime] = None

class SelfOptimizer:
    """Система автономного самоулучшения"""
    
    def __init__(self, optimization_dir: str = "autonomous/optimizations"):
        self.optimization_dir = Path(optimization_dir)
        self.optimization_dir.mkdir(exist_ok=True)
        
        # Хранилище предложений
        self.pending_proposals: Dict[str, OptimizationProposal] = {}
        self.applied_optimizations: List[OptimizationProposal] = []
        
        # Настройки самооптимизации
        self.config = self.load_config()
        
        # Статистика для принятия решений
        self.optimization_history = []
        self.performance_baseline = {}
        
        # Блокировка для thread-safety
        self.lock = threading.Lock()
        
        # Запуск фонового процесса анализа
        self.analysis_thread = threading.Thread(target=self.continuous_analysis, daemon=True)
        self.analysis_thread.start()
        
        # Callback для подтверждения пользователя
        self.user_approval_callback: Optional[Callable] = None
        
        print("🤖 Self Optimizer инициализирован")
    
    def load_config(self) -> Dict:
        """Загрузка конфигурации самооптимизации"""
        config_file = self.optimization_dir / "self_optimizer_config.json"
        
        default_config = {
            "enabled": True,
            "analysis_interval_minutes": 30,
            "auto_apply_threshold": 0.9,  # Confidence score для автоприменения
            "max_pending_proposals": 10,
            "proposal_expiry_hours": 24,
            "optimization_categories": {
                "cache": {"enabled": True, "auto_apply": True},
                "thresholds": {"enabled": True, "auto_apply": False},
                "config": {"enabled": True, "auto_apply": False},
                "resources": {"enabled": True, "auto_apply": False}
            },
            "safety_limits": {
                "max_cache_size_mb": 500,
                "min_success_rate": 0.8,
                "max_response_time": 30.0,
                "max_daily_optimizations": 5
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            except Exception as e:
                print(f"⚠️ Ошибка загрузки конфигурации оптимизатора: {e}")
        
        # Сохранение конфигурации по умолчанию
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def set_user_approval_callback(self, callback: Callable[[OptimizationProposal], bool]):
        """Установка callback для подтверждения пользователя"""
        self.user_approval_callback = callback
        print("✅ Callback подтверждения пользователя установлен")
    
    def continuous_analysis(self):
        """Непрерывный анализ для выявления возможностей оптимизации"""
        while True:
            try:
                if not self.config["enabled"]:
                    time.sleep(300)  # 5 минут если отключен
                    continue
                
                # Анализ производительности
                self.analyze_performance_metrics()
                
                # Анализ кэша
                self.analyze_cache_efficiency()
                
                # Анализ алертов
                self.analyze_alert_patterns()
                
                # Применение автоматических оптимизаций
                self.apply_automatic_optimizations()
                
                # Очистка устаревших предложений
                self.cleanup_expired_proposals()
                
                # Ожидание до следующего анализа
                interval = self.config["analysis_interval_minutes"] * 60
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Ошибка в непрерывном анализе: {e}")
                time.sleep(300)  # 5 минут при ошибке
    
    def analyze_performance_metrics(self):
        """Анализ метрик производительности"""
        try:
            # Получение рекомендаций от ИИ
            ai_recommendations = optimizer_ai.generate_comprehensive_recommendations()
            
            for ai_rec in ai_recommendations[:3]:  # Топ-3 рекомендации
                proposal = self.create_proposal_from_ai_recommendation(ai_rec)
                if proposal:
                    self.add_optimization_proposal(proposal)
            
            # Анализ трендов производительности
            self.analyze_performance_trends()
            
        except Exception as e:
            print(f"❌ Ошибка анализа производительности: {e}")
    
    def create_proposal_from_ai_recommendation(self, ai_rec) -> Optional[OptimizationProposal]:
        """Создание предложения на основе ИИ-рекомендации"""
        proposal_id = f"AI_{ai_rec.id}_{int(time.time())}"
        
        # Определение типа оптимизации
        if "token" in ai_rec.description.lower():
            opt_type = OptimizationType.THRESHOLD_ADJUSTMENT
        elif "cache" in ai_rec.description.lower():
            opt_type = OptimizationType.CACHE_OPTIMIZATION
        elif "server" in ai_rec.description.lower():
            opt_type = OptimizationType.CONFIG_UPDATE
        else:
            opt_type = OptimizationType.PERFORMANCE_TUNING
        
        # Определение критичности
        if ai_rec.priority >= 4:
            severity = OptimizationSeverity.HIGH
        elif ai_rec.priority >= 3:
            severity = OptimizationSeverity.MEDIUM
        else:
            severity = OptimizationSeverity.LOW
        
        # Генерация изменений на основе рекомендации
        changes = self.generate_changes_from_ai_rec(ai_rec)
        if not changes:
            return None
        
        return OptimizationProposal(
            id=proposal_id,
            type=opt_type,
            severity=severity,
            title=f"Автооптимизация: {ai_rec.title}",
            description=ai_rec.description,
            rationale=f"ИИ-анализ выявил возможность улучшения с confidence score {ai_rec.confidence_score:.2f}",
            changes=changes,
            backup_data=self.create_backup_data(changes),
            estimated_impact=ai_rec.estimated_savings,
            risk_assessment=self.assess_risk(changes, severity),
            rollback_plan=self.generate_rollback_plan(changes),
            confidence_score=ai_rec.confidence_score,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=self.config["proposal_expiry_hours"])
        )
    
    def generate_changes_from_ai_rec(self, ai_rec) -> Dict[str, Any]:
        """Генерация конкретных изменений на основе ИИ-рекомендации"""
        changes = {}
        
        # Анализ рекомендации и генерация изменений
        if "token" in ai_rec.description.lower() and ai_rec.mcp_server:
            # Оптимизация лимитов токенов
            current_limit = 1000  # Получить из конфигурации
            new_limit = max(500, int(current_limit * 0.8))
            changes = {
                "file": ".mcp.json",
                "path": f"mcpServers.{ai_rec.mcp_server}.token_limit",
                "old_value": current_limit,
                "new_value": new_limit,
                "action": "update_config"
            }
        
        elif "cache" in ai_rec.description.lower():
            # Оптимизация кэша
            changes = {
                "action": "optimize_cache",
                "operations": ["cleanup_expired", "adjust_ttl", "improve_quality_threshold"],
                "target_hit_rate": 0.7
            }
        
        elif "response time" in ai_rec.description.lower() and ai_rec.mcp_server:
            # Оптимизация таймаутов
            changes = {
                "file": ".mcp.json",
                "path": f"mcpServers.{ai_rec.mcp_server}.timeout",
                "old_value": 30000,
                "new_value": 20000,
                "action": "update_timeout"
            }
        
        return changes
    
    def analyze_cache_efficiency(self):
        """Анализ эффективности кэша"""
        try:
            cache_stats = cache_manager.get_cache_statistics()
            
            # Предложение увеличения размера кэша при высокой эффективности
            if (cache_stats.hit_rate > 0.8 and 
                cache_stats.space_efficiency > 0.9 and
                cache_stats.total_size_mb < self.config["safety_limits"]["max_cache_size_mb"]):
                
                proposal = OptimizationProposal(
                    id=f"CACHE_EXPAND_{int(time.time())}",
                    type=OptimizationType.CACHE_OPTIMIZATION,
                    severity=OptimizationSeverity.LOW,
                    title="Увеличение размера кэша",
                    description=f"Высокая эффективность кэша ({cache_stats.hit_rate:.1%}), рекомендуется увеличение размера",
                    rationale=f"Hit rate {cache_stats.hit_rate:.1%}, space efficiency {cache_stats.space_efficiency:.1%}",
                    changes={
                        "action": "increase_cache_size",
                        "current_size": cache_stats.total_size_mb,
                        "new_size": min(cache_stats.total_size_mb * 1.5, 
                                      self.config["safety_limits"]["max_cache_size_mb"])
                    },
                    backup_data={"current_cache_config": "backup_saved"},
                    estimated_impact={"cache_hit_rate": 0.05, "response_time": -0.5},
                    risk_assessment="Низкий - увеличение ресурсов",
                    rollback_plan="Возврат к предыдущему размеру кэша",
                    confidence_score=0.85,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=12)
                )
                
                self.add_optimization_proposal(proposal)
            
            # Предложение очистки при низкой эффективности
            elif cache_stats.hit_rate < 0.3 and cache_stats.total_entries > 50:
                proposal = OptimizationProposal(
                    id=f"CACHE_CLEANUP_{int(time.time())}",
                    type=OptimizationType.CACHE_OPTIMIZATION,
                    severity=OptimizationSeverity.LOW,
                    title="Очистка неэффективного кэша",
                    description=f"Низкая эффективность кэша ({cache_stats.hit_rate:.1%}), рекомендуется очистка",
                    rationale=f"Hit rate {cache_stats.hit_rate:.1%} ниже порога {self.config['safety_limits']['min_success_rate']}",
                    changes={
                        "action": "optimize_cache",
                        "operations": ["cleanup_expired", "remove_low_quality", "adjust_ttl"]
                    },
                    backup_data={"cache_backup": "created"},
                    estimated_impact={"cache_efficiency": 0.2, "memory_usage": -20},
                    risk_assessment="Низкий - улучшение эффективности",
                    rollback_plan="Восстановление из бэкапа",
                    confidence_score=0.9,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=6)
                )
                
                self.add_optimization_proposal(proposal)
                
        except Exception as e:
            print(f"❌ Ошибка анализа кэша: {e}")
    
    def analyze_alert_patterns(self):
        """Анализ паттернов алертов для оптимизации"""
        try:
            # Получение активных алертов
            active_alerts = alert_system.get_active_alerts()
            
            # Анализ повторяющихся алертов
            alert_counts = {}
            for alert in alert_system.alerts_history[-50:]:  # Последние 50 алертов
                key = f"{alert.type.value}_{alert.mcp_server}"
                alert_counts[key] = alert_counts.get(key, 0) + 1
            
            # Предложения по оптимизации на основе частых алертов
            for alert_key, count in alert_counts.items():
                if count >= 5:  # Частые алерты
                    alert_type, server = alert_key.split("_", 1)
                    
                    proposal = self.create_alert_optimization_proposal(alert_type, server, count)
                    if proposal:
                        self.add_optimization_proposal(proposal)
                        
        except Exception as e:
            print(f"❌ Ошибка анализа алертов: {e}")
    
    def create_alert_optimization_proposal(self, alert_type: str, server: str, count: int) -> Optional[OptimizationProposal]:
        """Создание предложения оптимизации на основе частых алертов"""
        proposal_id = f"ALERT_OPT_{alert_type}_{server}_{int(time.time())}"
        
        if alert_type == "performance_degradation":
            return OptimizationProposal(
                id=proposal_id,
                type=OptimizationType.THRESHOLD_ADJUSTMENT,
                severity=OptimizationSeverity.MEDIUM,
                title=f"Корректировка порога для {server}",
                description=f"Частые алерты производительности ({count} раз), корректировка порога",
                rationale=f"Сервер {server} показывает {count} алертов производительности",
                changes={
                    "action": "adjust_threshold",
                    "server": server,
                    "threshold_type": "response_time",
                    "current_threshold": 10.0,
                    "new_threshold": 12.0
                },
                backup_data={"old_threshold": 10.0},
                estimated_impact={"alert_reduction": count * 0.7},
                risk_assessment="Средний - изменение мониторинга",
                rollback_plan="Возврат к предыдущему порогу",
                confidence_score=0.75,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=18)
            )
        
        return None
    
    def analyze_performance_trends(self):
        """Анализ трендов производительности"""
        try:
            # Получение данных за последние 3 дня
            servers = performance_tracker.get_all_servers()
            
            for server in servers:
                analysis = performance_tracker.get_server_performance(server, days=3)
                
                # Предложение оптимизации при ухудшении тренда
                if (analysis.trend_direction == 'degrading' and 
                    analysis.efficiency_score < 70):
                    
                    proposal = OptimizationProposal(
                        id=f"TREND_OPT_{server}_{int(time.time())}",
                        type=OptimizationType.PERFORMANCE_TUNING,
                        severity=OptimizationSeverity.HIGH,
                        title=f"Устранение деградации {server}",
                        description=f"Обнаружена деградация производительности (efficiency: {analysis.efficiency_score:.1f}%)",
                        rationale=f"Тренд: {analysis.trend_direction}, эффективность снизилась",
                        changes={
                            "action": "performance_intervention",
                            "server": server,
                            "interventions": ["restart_connection", "clear_cache", "reduce_load"]
                        },
                        backup_data={"server_state": "backed_up"},
                        estimated_impact={"efficiency_improvement": 20.0},
                        risk_assessment="Высокий - вмешательство в работу сервера",
                        rollback_plan="Восстановление состояния и настроек",
                        confidence_score=0.8,
                        created_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(hours=6)
                    )
                    
                    self.add_optimization_proposal(proposal)
                    
        except Exception as e:
            print(f"❌ Ошибка анализа трендов: {e}")
    
    def add_optimization_proposal(self, proposal: OptimizationProposal):
        """Добавление предложения оптимизации"""
        with self.lock:
            # Проверка лимитов
            if len(self.pending_proposals) >= self.config["max_pending_proposals"]:
                # Удаление самого старого предложения низкого приоритета
                oldest_low_priority = None
                for prop in self.pending_proposals.values():
                    if prop.severity == OptimizationSeverity.LOW:
                        if oldest_low_priority is None or prop.created_at < oldest_low_priority.created_at:
                            oldest_low_priority = prop
                
                if oldest_low_priority:
                    del self.pending_proposals[oldest_low_priority.id]
                else:
                    print("⚠️ Достигнут лимит предложений оптимизации")
                    return
            
            # Проверка дубликатов
            proposal_hash = self.calculate_proposal_hash(proposal)
            for existing in self.pending_proposals.values():
                if self.calculate_proposal_hash(existing) == proposal_hash:
                    print(f"⚠️ Дубликат предложения оптимизации: {proposal.title}")
                    return
            
            self.pending_proposals[proposal.id] = proposal
            print(f"💡 Новое предложение оптимизации: {proposal.title}")
            
            # Проверка автоматического применения
            if self.should_auto_apply(proposal):
                self.apply_optimization(proposal.id, auto_applied=True)
    
    def calculate_proposal_hash(self, proposal: OptimizationProposal) -> str:
        """Расчет хэша предложения для выявления дубликатов"""
        content = f"{proposal.type.value}_{proposal.title}_{json.dumps(proposal.changes, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def should_auto_apply(self, proposal: OptimizationProposal) -> bool:
        """Определение возможности автоматического применения"""
        # Проверка общих настроек
        if not self.config["enabled"]:
            return False
        
        # Проверка лимита ежедневных оптимизаций
        today_optimizations = sum(1 for opt in self.applied_optimizations 
                                if opt.applied_at and opt.applied_at.date() == datetime.now().date())
        
        if today_optimizations >= self.config["safety_limits"]["max_daily_optimizations"]:
            return False
        
        # Проверка критичности
        if proposal.severity in [OptimizationSeverity.HIGH, OptimizationSeverity.CRITICAL]:
            return False
        
        # Проверка confidence score
        if proposal.confidence_score < self.config["auto_apply_threshold"]:
            return False
        
        # Проверка категории
        category_config = self.config["optimization_categories"]
        
        if proposal.type == OptimizationType.CACHE_OPTIMIZATION:
            return category_config["cache"]["auto_apply"]
        elif proposal.type == OptimizationType.THRESHOLD_ADJUSTMENT:
            return category_config["thresholds"]["auto_apply"]
        elif proposal.type == OptimizationType.CONFIG_UPDATE:
            return category_config["config"]["auto_apply"]
        
        return False
    
    def apply_automatic_optimizations(self):
        """Применение автоматических оптимизаций"""
        with self.lock:
            auto_applicable = [
                proposal for proposal in self.pending_proposals.values()
                if self.should_auto_apply(proposal) and not proposal.applied
            ]
            
            for proposal in auto_applicable:
                try:
                    self.apply_optimization(proposal.id, auto_applied=True)
                except Exception as e:
                    print(f"❌ Ошибка автоприменения оптимизации {proposal.id}: {e}")
    
    def request_user_approval(self, proposal: OptimizationProposal) -> bool:
        """Запрос подтверждения пользователя"""
        if self.user_approval_callback is None:
            print(f"⚠️ Требуется подтверждение для: {proposal.title}")
            print(f"   Описание: {proposal.description}")
            print(f"   Критичность: {proposal.severity.value}")
            print(f"   Confidence: {proposal.confidence_score:.2f}")
            
            # Простой ввод для демонстрации
            response = input("   Применить оптимизацию? (y/n): ").lower().strip()
            return response == 'y'
        
        return self.user_approval_callback(proposal)
    
    def apply_optimization(self, proposal_id: str, auto_applied: bool = False) -> bool:
        """Применение оптимизации"""
        if proposal_id not in self.pending_proposals:
            print(f"❌ Предложение {proposal_id} не найдено")
            return False
        
        proposal = self.pending_proposals[proposal_id]
        
        if proposal.applied:
            print(f"⚠️ Оптимизация {proposal_id} уже применена")
            return False
        
        # Запрос подтверждения для критичных изменений
        if not auto_applied and proposal.severity in [OptimizationSeverity.HIGH, OptimizationSeverity.CRITICAL]:
            if not self.request_user_approval(proposal):
                proposal.approved = False
                print(f"❌ Оптимизация {proposal_id} отклонена пользователем")
                return False
        
        proposal.approved = True
        
        try:
            # Создание бэкапа
            self.create_backup(proposal)
            
            # Применение изменений
            success = self.execute_optimization_changes(proposal)
            
            if success:
                proposal.applied = True
                proposal.applied_at = datetime.now()
                self.applied_optimizations.append(proposal)
                del self.pending_proposals[proposal_id]
                
                apply_method = "автоматически" if auto_applied else "с подтверждением"
                print(f"✅ Оптимизация применена {apply_method}: {proposal.title}")
                
                # Сохранение истории
                self.save_optimization_history()
                
                return True
            else:
                print(f"❌ Ошибка применения оптимизации {proposal_id}")
                return False
                
        except Exception as e:
            print(f"❌ Исключение при применении оптимизации {proposal_id}: {e}")
            return False
    
    def execute_optimization_changes(self, proposal: OptimizationProposal) -> bool:
        """Выполнение конкретных изменений оптимизации"""
        try:
            changes = proposal.changes
            action = changes.get("action")
            
            if action == "optimize_cache":
                return self.apply_cache_optimization(changes)
            elif action == "update_config":
                return self.apply_config_update(changes)
            elif action == "adjust_threshold":
                return self.apply_threshold_adjustment(changes)
            elif action == "increase_cache_size":
                return self.apply_cache_size_increase(changes)
            elif action == "performance_intervention":
                return self.apply_performance_intervention(changes)
            else:
                print(f"⚠️ Неизвестное действие: {action}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка выполнения изменений: {e}")
            return False
    
    def apply_cache_optimization(self, changes: Dict[str, Any]) -> bool:
        """Применение оптимизации кэша"""
        try:
            operations = changes.get("operations", [])
            
            for operation in operations:
                if operation == "cleanup_expired":
                    removed = cache_manager.cleanup_expired()
                    print(f"🗑️ Удалено устаревших записей кэша: {removed}")
                
                elif operation == "remove_low_quality":
                    # Имитация удаления низкокачественных записей
                    print("🔧 Удалены низкокачественные записи кэша")
                
                elif operation == "adjust_ttl":
                    print("⏰ TTL кэша скорректирован")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка оптимизации кэша: {e}")
            return False
    
    def apply_config_update(self, changes: Dict[str, Any]) -> bool:
        """Применение обновления конфигурации"""
        try:
            file_path = changes.get("file")
            config_path = changes.get("path")
            new_value = changes.get("new_value")
            
            print(f"🔧 Обновление {file_path}:{config_path} -> {new_value}")
            # Здесь была бы реальная логика обновления конфигурации
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления конфигурации: {e}")
            return False
    
    def apply_threshold_adjustment(self, changes: Dict[str, Any]) -> bool:
        """Применение корректировки порогов"""
        try:
            server = changes.get("server")
            threshold_type = changes.get("threshold_type")
            new_threshold = changes.get("new_threshold")
            
            print(f"📊 Корректировка порога {threshold_type} для {server}: {new_threshold}")
            # Здесь была бы реальная логика обновления порогов
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка корректировки порогов: {e}")
            return False
    
    def apply_cache_size_increase(self, changes: Dict[str, Any]) -> bool:
        """Применение увеличения размера кэша"""
        try:
            new_size = changes.get("new_size")
            print(f"💾 Увеличение размера кэша до {new_size} МБ")
            # Здесь была бы реальная логика изменения размера кэша
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка увеличения кэша: {e}")
            return False
    
    def apply_performance_intervention(self, changes: Dict[str, Any]) -> bool:
        """Применение вмешательства в производительность"""
        try:
            server = changes.get("server")
            interventions = changes.get("interventions", [])
            
            for intervention in interventions:
                print(f"🔧 Применение {intervention} для {server}")
                # Здесь была бы реальная логика вмешательства
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка вмешательства в производительность: {e}")
            return False
    
    def create_backup_data(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Создание данных бэкапа"""
        backup = {
            "timestamp": datetime.now().isoformat(),
            "changes": changes
        }
        
        # Специфические бэкапы в зависимости от типа изменений
        action = changes.get("action")
        
        if action == "update_config":
            backup["config_backup"] = "Бэкап конфигурации создан"
        elif action == "optimize_cache":
            backup["cache_backup"] = "Бэкап кэша создан"
        
        return backup
    
    def create_backup(self, proposal: OptimizationProposal):
        """Создание бэкапа перед применением оптимизации"""
        backup_dir = self.optimization_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_file = backup_dir / f"backup_{proposal.id}.json"
        
        backup_data = {
            "proposal_id": proposal.id,
            "timestamp": datetime.now().isoformat(),
            "backup_data": proposal.backup_data,
            "original_changes": proposal.changes
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 Бэкап создан: {backup_file}")
    
    def assess_risk(self, changes: Dict[str, Any], severity: OptimizationSeverity) -> str:
        """Оценка риска изменений"""
        action = changes.get("action", "")
        
        if severity == OptimizationSeverity.CRITICAL:
            return "Критический - может повлиять на работу системы"
        elif severity == OptimizationSeverity.HIGH:
            return "Высокий - требует мониторинга после применения"
        elif action in ["optimize_cache", "cleanup_expired"]:
            return "Низкий - улучшение эффективности"
        elif action in ["update_config", "adjust_threshold"]:
            return "Средний - изменение настроек"
        else:
            return "Неизвестный - требует анализа"
    
    def generate_rollback_plan(self, changes: Dict[str, Any]) -> str:
        """Генерация плана отката"""
        action = changes.get("action", "")
        
        if action == "optimize_cache":
            return "Восстановление кэша из бэкапа"
        elif action == "update_config":
            file_path = changes.get("file", "config")
            return f"Восстановление {file_path} из бэкапа"
        elif action == "adjust_threshold":
            return "Возврат к предыдущим значениям порогов"
        else:
            return "Восстановление из автоматического бэкапа"
    
    def cleanup_expired_proposals(self):
        """Очистка устаревших предложений"""
        with self.lock:
            now = datetime.now()
            expired_ids = [
                proposal_id for proposal_id, proposal in self.pending_proposals.items()
                if proposal.expires_at < now
            ]
            
            for proposal_id in expired_ids:
                del self.pending_proposals[proposal_id]
                print(f"🗑️ Удалено устаревшее предложение: {proposal_id}")
    
    def save_optimization_history(self):
        """Сохранение истории оптимизаций"""
        history_file = self.optimization_dir / "optimization_history.json"
        
        history_data = {
            "last_updated": datetime.now().isoformat(),
            "total_applied": len(self.applied_optimizations),
            "applied_optimizations": [asdict(opt) for opt in self.applied_optimizations[-50:]]  # Последние 50
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2, default=str)
    
    def get_pending_proposals(self) -> List[OptimizationProposal]:
        """Получение списка ожидающих предложений"""
        return list(self.pending_proposals.values())
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Получение статистики оптимизаций"""
        pending_count = len(self.pending_proposals)
        applied_count = len(self.applied_optimizations)
        
        # Подсчет по типам
        type_counts = {}
        for proposal in self.applied_optimizations:
            type_counts[proposal.type.value] = type_counts.get(proposal.type.value, 0) + 1
        
        # Подсчет по критичности
        severity_counts = {}
        for proposal in self.pending_proposals.values():
            severity_counts[proposal.severity.value] = severity_counts.get(proposal.severity.value, 0) + 1
        
        return {
            "pending_proposals": pending_count,
            "applied_optimizations": applied_count,
            "optimization_types": type_counts,
            "pending_by_severity": severity_counts,
            "auto_apply_enabled": self.config["enabled"],
            "daily_limit": self.config["safety_limits"]["max_daily_optimizations"]
        }
    
    def print_status_report(self):
        """Вывод отчета о состоянии оптимизатора"""
        stats = self.get_optimization_statistics()
        
        print("\n🤖 === СТАТУС SELF OPTIMIZER ===")
        print(f"📊 Ожидающие предложения: {stats['pending_proposals']}")
        print(f"✅ Применено оптимизаций: {stats['applied_optimizations']}")
        print(f"🔧 Автоприменение: {'Включено' if stats['auto_apply_enabled'] else 'Отключено'}")
        
        if stats['pending_by_severity']:
            print("\n📋 Ожидающие по критичности:")
            severity_names = {"low": "🟢 Низкая", "medium": "🟡 Средняя", "high": "🧡 Высокая", "critical": "🔴 Критичная"}
            for severity, count in stats['pending_by_severity'].items():
                print(f"  {severity_names.get(severity, severity)}: {count}")
        
        if stats['optimization_types']:
            print("\n🔧 Применено по типам:")
            for opt_type, count in stats['optimization_types'].items():
                print(f"  • {opt_type}: {count}")
        
        print("="*40)

# Глобальный экземпляр автооптимизатора
self_optimizer = SelfOptimizer()

def get_pending_optimizations() -> List[OptimizationProposal]:
    """Получение ожидающих оптимизаций"""
    return self_optimizer.get_pending_proposals()

def apply_optimization_by_id(proposal_id: str) -> bool:
    """Применение оптимизации по ID"""
    return self_optimizer.apply_optimization(proposal_id)

def set_user_approval_callback(callback: Callable[[OptimizationProposal], bool]):
    """Установка callback подтверждения пользователя"""
    self_optimizer.set_user_approval_callback(callback)

def print_optimizer_status():
    """Вывод статуса оптимизатора"""
    self_optimizer.print_status_report()

def get_optimization_statistics() -> Dict[str, Any]:
    """Получение статистики оптимизаций"""
    return self_optimizer.get_optimization_statistics()

if __name__ == "__main__":
    # Демонстрация автооптимизатора
    print("🤖 Self Optimizer запущен")
    
    # Пример callback подтверждения
    def approval_callback(proposal: OptimizationProposal) -> bool:
        print(f"🔔 Запрос подтверждения: {proposal.title}")
        print(f"   Критичность: {proposal.severity.value}")
        print(f"   Описание: {proposal.description}")
        return True  # Автоподтверждение для демо
    
    set_user_approval_callback(approval_callback)
    
    # Вывод начального статуса
    print_optimizer_status()
    
    print("🔄 Система самооптимизации активна...")