#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approval System - Система подтверждения оптимизаций пользователем
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib

# Импорт модулей самооптимизации
from autonomous.self_optimizer import OptimizationProposal, OptimizationType, OptimizationSeverity

class ApprovalDecision(Enum):
    """Решения по предложениям оптимизации"""
    APPROVE = "approve"
    REJECT = "reject" 
    DEFER = "defer"
    REQUEST_INFO = "request_info"

@dataclass
class ApprovalRequest:
    """Запрос на подтверждение оптимизации"""
    proposal_id: str
    proposal: OptimizationProposal
    requested_at: datetime
    expires_at: datetime
    status: str = "pending"  # pending, approved, rejected, deferred, expired
    decision_reason: Optional[str] = None
    decided_at: Optional[datetime] = None

class ApprovalInterface:
    """Интерфейс для управления подтверждениями оптимизации"""
    
    def __init__(self, approval_dir: str = "autonomous/approvals"):
        self.approval_dir = Path(approval_dir)
        self.approval_dir.mkdir(exist_ok=True)
        
        # Хранилище запросов на подтверждение
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[ApprovalRequest] = []
        
        # Настройки интерфейса
        self.config = self.load_approval_config()
        
        # Callbacks для уведомлений
        self.approval_callbacks: List[Callable] = []
        
        # Автоматические правила принятия решений
        self.auto_approval_rules = self.init_auto_approval_rules()
        
        print("✅ Approval System инициализирован")
    
    def load_approval_config(self) -> Dict:
        """Загрузка конфигурации системы подтверждений"""
        config_file = self.approval_dir / "approval_config.json"
        
        default_config = {
            "interface": {
                "auto_show_proposals": True,
                "detailed_impact_analysis": True,
                "confirmation_timeout_hours": 24,
                "max_pending_proposals": 10
            },
            "auto_approval": {
                "enabled": True,
                "low_risk_auto_approve": True,
                "performance_improvement_threshold": 15.0,  # %
                "max_auto_approve_per_hour": 3
            },
            "notification": {
                "show_proposal_details": True,
                "highlight_risks": True,
                "show_rollback_plan": True
            },
            "display": {
                "use_emojis": True,
                "color_coding": True,
                "compact_mode": False
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
                print(f"⚠️ Ошибка загрузки конфигурации подтверждений: {e}")
        
        # Сохранение конфигурации по умолчанию
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def init_auto_approval_rules(self) -> List[Dict]:
        """Инициализация правил автоматического подтверждения"""
        if not self.config["auto_approval"]["enabled"]:
            return []
        
        rules = []
        
        # Правило 1: Автоматическое подтверждение низкорискованных оптимизаций
        if self.config["auto_approval"]["low_risk_auto_approve"]:
            rules.append({
                "name": "low_risk_auto_approve",
                "condition": lambda proposal: (
                    proposal.severity == OptimizationSeverity.LOW and
                    proposal.confidence_score > 0.8 and
                    "cache" in proposal.type.value
                ),
                "max_per_hour": 5
            })
        
        # Правило 2: Автоподтверждение значительных улучшений производительности
        rules.append({
            "name": "high_performance_gain",
            "condition": lambda proposal: (
                proposal.estimated_impact.get("performance_improvement", 0) > 
                self.config["auto_approval"]["performance_improvement_threshold"] and
                proposal.confidence_score > 0.9
            ),
            "max_per_hour": 2
        })
        
        # Правило 3: Автоподтверждение исправлений критических проблем
        rules.append({
            "name": "critical_fixes",
            "condition": lambda proposal: (
                "error" in proposal.description.lower() or
                "fix" in proposal.description.lower() and
                proposal.severity in [OptimizationSeverity.HIGH, OptimizationSeverity.CRITICAL]
            ),
            "max_per_hour": 1
        })
        
        return rules
    
    def request_approval(self, proposal: OptimizationProposal) -> str:
        """Запрос подтверждения предложения оптимизации"""
        request_id = f"approval_{proposal.id}_{int(time.time())}"
        
        # Проверка автоматического подтверждения
        auto_decision = self.check_auto_approval(proposal)
        if auto_decision:
            return self.process_auto_approval(proposal, auto_decision, request_id)
        
        # Создание запроса на подтверждение
        approval_request = ApprovalRequest(
            proposal_id=proposal.id,
            proposal=proposal,
            requested_at=datetime.now(),
            expires_at=proposal.expires_at
        )
        
        self.pending_approvals[request_id] = approval_request
        
        # Отображение предложения пользователю
        if self.config["interface"]["auto_show_proposals"]:
            self.display_proposal(approval_request)
        
        # Уведомление callback'ов
        for callback in self.approval_callbacks:
            try:
                callback(approval_request)
            except Exception as e:
                print(f"⚠️ Ошибка в approval callback: {e}")
        
        return request_id
    
    def check_auto_approval(self, proposal: OptimizationProposal) -> Optional[str]:
        """Проверка возможности автоматического подтверждения"""
        if not self.config["auto_approval"]["enabled"]:
            return None
        
        # Проверка лимитов автоподтверждения
        current_hour = datetime.now().hour
        auto_approvals_this_hour = len([
            req for req in self.approval_history 
            if (req.decided_at and 
                req.decided_at.hour == current_hour and 
                req.status == "approved")
        ])
        
        if auto_approvals_this_hour >= self.config["auto_approval"]["max_auto_approve_per_hour"]:
            return None
        
        # Проверка правил автоподтверждения
        for rule in self.auto_approval_rules:
            try:
                if rule["condition"](proposal):
                    rule_approvals_this_hour = len([
                        req for req in self.approval_history
                        if (req.decided_at and 
                            req.decided_at.hour == current_hour and
                            req.status == "approved" and
                            req.decision_reason == f"auto:{rule['name']}")
                    ])
                    
                    if rule_approvals_this_hour < rule.get("max_per_hour", 1):
                        return f"auto:{rule['name']}"
            except Exception as e:
                print(f"⚠️ Ошибка в правиле автоподтверждения {rule['name']}: {e}")
        
        return None
    
    def process_auto_approval(self, proposal: OptimizationProposal, 
                            auto_reason: str, request_id: str) -> str:
        """Обработка автоматического подтверждения"""
        approval_request = ApprovalRequest(
            proposal_id=proposal.id,
            proposal=proposal,
            requested_at=datetime.now(),
            expires_at=proposal.expires_at,
            status="approved",
            decision_reason=auto_reason,
            decided_at=datetime.now()
        )
        
        self.approval_history.append(approval_request)
        
        # Уведомление об автоматическом подтверждении
        print(f"🤖 Автоподтверждение: {proposal.title}")
        print(f"   Причина: {auto_reason}")
        print(f"   Confidence: {proposal.confidence_score:.1%}")
        
        return request_id
    
    def display_proposal(self, request: ApprovalRequest):
        """Отображение предложения оптимизации для пользователя"""
        proposal = request.proposal
        
        # Заголовок с эмодзи по критичности
        severity_emoji = {
            OptimizationSeverity.LOW: "💚",
            OptimizationSeverity.MEDIUM: "💛", 
            OptimizationSeverity.HIGH: "🧡",
            OptimizationSeverity.CRITICAL: "🔴"
        }
        
        type_emoji = {
            OptimizationType.CONFIG_UPDATE: "⚙️",
            OptimizationType.CACHE_OPTIMIZATION: "💾",
            OptimizationType.THRESHOLD_ADJUSTMENT: "📊",
            OptimizationType.RESOURCE_REALLOCATION: "🔄",
            OptimizationType.ALERT_RULE_UPDATE: "🚨",
            OptimizationType.PERFORMANCE_TUNING: "⚡"
        }
        
        emoji = severity_emoji.get(proposal.severity, "⚠️")
        type_icon = type_emoji.get(proposal.type, "🔧")
        
        print(f"\n{emoji} === ЗАПРОС НА ОПТИМИЗАЦИЮ ===")
        print(f"{type_icon} **{proposal.title}**")
        print(f"📝 {proposal.description}")
        print(f"🎯 Обоснование: {proposal.rationale}")
        
        # Детали воздействия
        if self.config["interface"]["detailed_impact_analysis"]:
            print(f"\n📈 **Ожидаемый эффект:**")
            for metric, value in proposal.estimated_impact.items():
                if value > 0:
                    print(f"  • {metric}: +{value:.1f}")
            
            print(f"🎲 Уверенность: {proposal.confidence_score:.1%}")
        
        # Технические детали
        if proposal.changes and not self.config["display"]["compact_mode"]:
            print(f"\n🔧 **Изменения:**")
            for key, value in proposal.changes.items():
                print(f"  • {key}: {value}")
        
        # План отката
        if self.config["notification"]["show_rollback_plan"]:
            print(f"\n🔙 **План отката:** {proposal.rollback_plan}")
        
        # Оценка рисков
        if self.config["notification"]["highlight_risks"]:
            risk_level = {
                OptimizationSeverity.LOW: "Низкий",
                OptimizationSeverity.MEDIUM: "Средний",
                OptimizationSeverity.HIGH: "Высокий", 
                OptimizationSeverity.CRITICAL: "Критический"
            }
            print(f"⚠️ **Риск:** {risk_level.get(proposal.severity, 'Неизвестен')}")
            print(f"🛡️ **Анализ рисков:** {proposal.risk_assessment}")
        
        # Сроки
        expires_in = (proposal.expires_at - datetime.now()).total_seconds() / 3600
        print(f"⏰ **Срок принятия решения:** {expires_in:.1f} часов")
        
        # Команды для принятия решения
        print(f"\n🎮 **Команды:**")
        print(f"  approve('{request.proposal_id}') - Подтвердить")
        print(f"  reject('{request.proposal_id}') - Отклонить")
        print(f"  defer('{request.proposal_id}') - Отложить")
        print(f"  info('{request.proposal_id}') - Дополнительная информация")
        print("="*60)
    
    def approve_proposal(self, proposal_id: str, reason: str = "") -> bool:
        """Подтверждение предложения оптимизации"""
        request = self.find_pending_request(proposal_id)
        if not request:
            print(f"❌ Предложение {proposal_id} не найдено или уже обработано")
            return False
        
        request.status = "approved"
        request.decision_reason = reason or "Подтверждено пользователем"
        request.decided_at = datetime.now()
        
        # Перемещение в историю
        self.approval_history.append(request)
        del self.pending_approvals[proposal_id]
        
        print(f"✅ Предложение оптимизации подтверждено: {request.proposal.title}")
        
        return True
    
    def reject_proposal(self, proposal_id: str, reason: str = "") -> bool:
        """Отклонение предложения оптимизации"""
        request = self.find_pending_request(proposal_id)
        if not request:
            print(f"❌ Предложение {proposal_id} не найдено или уже обработано")
            return False
        
        request.status = "rejected"
        request.decision_reason = reason or "Отклонено пользователем"
        request.decided_at = datetime.now()
        
        # Перемещение в историю
        self.approval_history.append(request)
        del self.pending_approvals[proposal_id]
        
        print(f"❌ Предложение оптимизации отклонено: {request.proposal.title}")
        
        return True
    
    def defer_proposal(self, proposal_id: str, reason: str = "") -> bool:
        """Отложение решения по предложению"""
        request = self.find_pending_request(proposal_id)
        if not request:
            print(f"❌ Предложение {proposal_id} не найдено или уже обработано")
            return False
        
        # Продление срока на 24 часа
        from datetime import timedelta
        request.expires_at = datetime.now() + timedelta(hours=24)
        request.decision_reason = reason or "Отложено для дальнейшего рассмотрения"
        
        print(f"⏰ Предложение отложено на 24 часа: {request.proposal.title}")
        
        return True
    
    def request_additional_info(self, proposal_id: str) -> bool:
        """Запрос дополнительной информации по предложению"""
        request = self.find_pending_request(proposal_id)
        if not request:
            print(f"❌ Предложение {proposal_id} не найдено")
            return False
        
        proposal = request.proposal
        
        print(f"\n📋 === ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ===")
        print(f"🆔 ID: {proposal.id}")
        print(f"📅 Создано: {proposal.created_at}")
        print(f"⏰ Истекает: {proposal.expires_at}")
        
        # Детальный анализ изменений
        print(f"\n🔍 **Детальные изменения:**")
        for key, value in proposal.changes.items():
            print(f"  • {key}:")
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    print(f"    - {subkey}: {subvalue}")
            else:
                print(f"    {value}")
        
        # Данные для отката
        print(f"\n💾 **Данные для отката:**")
        for key, value in proposal.backup_data.items():
            print(f"  • {key}: {value}")
        
        # Техническая статистика
        print(f"\n📊 **Техническая информация:**")
        print(f"  • Алгоритм: {proposal.type.value}")
        print(f"  • Критичность: {proposal.severity.value}")
        print(f"  • Хеш: {hashlib.md5(proposal.id.encode()).hexdigest()[:8]}")
        
        return True
    
    def find_pending_request(self, proposal_id: str) -> Optional[ApprovalRequest]:
        """Поиск активного запроса на подтверждение"""
        for request_id, request in self.pending_approvals.items():
            if request.proposal_id == proposal_id:
                return request
        return None
    
    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Получение списка ожидающих подтверждения предложений"""
        return list(self.pending_approvals.values())
    
    def cleanup_expired_requests(self):
        """Очистка просроченных запросов"""
        current_time = datetime.now()
        expired_requests = []
        
        for request_id, request in list(self.pending_approvals.items()):
            if current_time > request.expires_at:
                request.status = "expired"
                request.decided_at = current_time
                request.decision_reason = "Срок подтверждения истек"
                
                self.approval_history.append(request)
                expired_requests.append(request)
                del self.pending_approvals[request_id]
        
        if expired_requests:
            print(f"⏰ Истек срок для {len(expired_requests)} предложений")
        
        return len(expired_requests)
    
    def get_approval_statistics(self) -> Dict[str, Any]:
        """Статистика системы подтверждений"""
        total_requests = len(self.approval_history)
        
        if total_requests == 0:
            return {"total": 0, "message": "Нет данных о запросах подтверждения"}
        
        # Подсчет по статусам
        status_counts = {}
        auto_approvals = 0
        
        for request in self.approval_history:
            status_counts[request.status] = status_counts.get(request.status, 0) + 1
            if request.decision_reason and request.decision_reason.startswith("auto:"):
                auto_approvals += 1
        
        # Средние времена принятия решений
        decision_times = []
        for request in self.approval_history:
            if request.decided_at and request.status != "expired":
                delta = request.decided_at - request.requested_at
                decision_times.append(delta.total_seconds() / 3600)  # в часах
        
        avg_decision_time = sum(decision_times) / len(decision_times) if decision_times else 0
        
        return {
            "total_requests": total_requests,
            "pending": len(self.pending_approvals),
            "status_breakdown": status_counts,
            "auto_approvals": auto_approvals,
            "auto_approval_rate": auto_approvals / total_requests if total_requests > 0 else 0,
            "avg_decision_time_hours": avg_decision_time,
            "recent_activity": len([r for r in self.approval_history 
                                  if (datetime.now() - r.requested_at).days < 7])
        }
    
    def add_approval_callback(self, callback: Callable):
        """Добавление callback для уведомлений о новых запросах"""
        self.approval_callbacks.append(callback)
    
    def save_approval_state(self) -> str:
        """Сохранение состояния системы подтверждений"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"approval_state_{timestamp}.json"
        filepath = self.approval_dir / filename
        
        # Сериализация состояния
        state_data = {
            'saved_at': datetime.now().isoformat(),
            'pending_approvals': {
                req_id: {
                    'proposal_id': req.proposal_id,
                    'proposal': asdict(req.proposal),
                    'requested_at': req.requested_at.isoformat(),
                    'expires_at': req.expires_at.isoformat(),
                    'status': req.status
                }
                for req_id, req in self.pending_approvals.items()
            },
            'approval_history_count': len(self.approval_history),
            'statistics': self.get_approval_statistics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2, default=str)
        
        return str(filepath)

# Глобальный экземпляр системы подтверждений
approval_interface = ApprovalInterface()

# Удобные функции для пользователя
def approve(proposal_id: str, reason: str = "") -> bool:
    """Подтвердить предложение оптимизации"""
    return approval_interface.approve_proposal(proposal_id, reason)

def reject(proposal_id: str, reason: str = "") -> bool:
    """Отклонить предложение оптимизации"""
    return approval_interface.reject_proposal(proposal_id, reason)

def defer(proposal_id: str, reason: str = "") -> bool:
    """Отложить решение по предложению"""
    return approval_interface.defer_proposal(proposal_id, reason)

def info(proposal_id: str) -> bool:
    """Получить дополнительную информацию о предложении"""
    return approval_interface.request_additional_info(proposal_id)

def show_pending() -> None:
    """Показать все ожидающие подтверждения предложения"""
    pending = approval_interface.get_pending_approvals()
    
    if not pending:
        print("📭 Нет ожидающих подтверждения предложений")
        return
    
    print(f"\n📋 === ОЖИДАЮЩИЕ ПОДТВЕРЖДЕНИЯ ({len(pending)}) ===")
    for request in pending:
        approval_interface.display_proposal(request)

def approval_stats() -> None:
    """Показать статистику системы подтверждений"""
    stats = approval_interface.get_approval_statistics()
    
    print("\n📊 === СТАТИСТИКА ПОДТВЕРЖДЕНИЙ ===")
    print(f"📥 Всего запросов: {stats['total_requests']}")
    print(f"⏳ Ожидающих: {stats['pending']}")
    
    if stats.get('status_breakdown'):
        print("\nПо статусам:")
        status_emoji = {
            'approved': '✅',
            'rejected': '❌', 
            'deferred': '⏰',
            'expired': '⌛'
        }
        for status, count in stats['status_breakdown'].items():
            emoji = status_emoji.get(status, '📋')
            print(f"  {emoji} {status}: {count}")
    
    if stats['auto_approvals'] > 0:
        print(f"\n🤖 Автоподтверждений: {stats['auto_approvals']} "
              f"({stats['auto_approval_rate']:.1%})")
    
    if stats['avg_decision_time_hours'] > 0:
        print(f"⏱️ Среднее время решения: {stats['avg_decision_time_hours']:.1f} часов")
    
    print("="*50)

if __name__ == "__main__":
    # Демонстрация системы подтверждений
    print("✅ Approval System инициализирован")
    
    # Отображение доступных команд
    print("\n🎮 Доступные команды:")
    print("  show_pending() - Показать ожидающие предложения")
    print("  approve(id, reason) - Подтвердить предложение")
    print("  reject(id, reason) - Отклонить предложение") 
    print("  defer(id, reason) - Отложить решение")
    print("  info(id) - Дополнительная информация")
    print("  approval_stats() - Статистика подтверждений")