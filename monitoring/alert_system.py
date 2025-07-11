#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alert System - Система предупреждений для мониторинга MCP производительности
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System  
Дата: 2025-07-11
"""

import json
import smtplib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
import queue
import time

class AlertSeverity(Enum):
    """Уровни критичности предупреждений"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Типы предупреждений"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    HIGH_TOKEN_USAGE = "high_token_usage"
    REPEATED_FAILURES = "repeated_failures"
    CACHE_INEFFICIENCY = "cache_inefficiency"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_CONCERN = "security_concern"
    QUOTA_EXCEEDED = "quota_exceeded"
    SYSTEM_ERROR = "system_error"

@dataclass
class Alert:
    """Структура предупреждения"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    details: Dict[str, Any]
    agent: Optional[str]
    mcp_server: Optional[str]
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class AlertRule:
    """Правило для генерации предупреждений"""
    name: str
    type: AlertType
    severity: AlertSeverity
    condition: Callable[[Dict], bool]
    threshold_value: float
    time_window: timedelta
    max_frequency: timedelta  # Минимальный интервал между одинаковыми алертами
    enabled: bool = True

class AlertSystem:
    """Система предупреждений для мониторинга MCP"""
    
    def __init__(self, config_path: str = "monitoring/alert_config.json"):
        self.config_path = Path(config_path)
        self.alerts_history: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # Загрузка конфигурации
        self.config = self.load_config()
        
        # Инициализация правил предупреждений
        self.alert_rules = self.init_alert_rules()
        
        # Статистика MCP для анализа
        self.mcp_stats = {
            'requests_count': {},
            'failure_count': {},
            'response_times': {},
            'token_usage': {},
            'last_alert_time': {}
        }
        
        # Запуск фонового процессора алертов
        self.processor_thread = threading.Thread(target=self._alert_processor, daemon=True)
        self.processor_thread.start()
        
        # Создание директории для логов
        Path("logs").mkdir(exist_ok=True)
    
    def load_config(self) -> Dict:
        """Загрузка конфигурации системы предупреждений"""
        default_config = {
            "thresholds": {
                "max_response_time": 10.0,
                "max_tokens_per_request": 1000,
                "max_session_tokens": 5000,
                "min_success_rate": 0.9,
                "max_failure_streak": 3,
                "min_cache_hit_rate": 0.3
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
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Объединение с настройками по умолчанию
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except Exception as e:
                print(f"⚠️ Ошибка загрузки конфигурации алертов: {e}")
        
        # Сохранение конфигурации по умолчанию
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def init_alert_rules(self) -> List[AlertRule]:
        """Инициализация правил предупреждений"""
        thresholds = self.config["thresholds"]
        
        rules = [
            # Правило: медленный ответ
            AlertRule(
                name="slow_response",
                type=AlertType.PERFORMANCE_DEGRADATION,
                severity=AlertSeverity.MEDIUM,
                condition=lambda stats: stats.get('response_time', 0) > thresholds["max_response_time"],
                threshold_value=thresholds["max_response_time"],
                time_window=timedelta(minutes=5),
                max_frequency=timedelta(minutes=10)
            ),
            
            # Правило: высокое потребление токенов
            AlertRule(
                name="high_token_usage",
                type=AlertType.HIGH_TOKEN_USAGE,
                severity=AlertSeverity.MEDIUM,
                condition=lambda stats: stats.get('tokens_used', 0) > thresholds["max_tokens_per_request"],
                threshold_value=thresholds["max_tokens_per_request"],
                time_window=timedelta(minutes=1),
                max_frequency=timedelta(minutes=15)
            ),
            
            # Правило: серия неудач
            AlertRule(
                name="repeated_failures",
                type=AlertType.REPEATED_FAILURES,
                severity=AlertSeverity.HIGH,
                condition=lambda stats: stats.get('consecutive_failures', 0) >= thresholds["max_failure_streak"],
                threshold_value=thresholds["max_failure_streak"],
                time_window=timedelta(minutes=5),
                max_frequency=timedelta(minutes=20)
            ),
            
            # Правило: низкая эффективность кэша
            AlertRule(
                name="cache_inefficiency",
                type=AlertType.CACHE_INEFFICIENCY,
                severity=AlertSeverity.LOW,
                condition=lambda stats: stats.get('cache_hit_rate', 1.0) < thresholds["min_cache_hit_rate"],
                threshold_value=thresholds["min_cache_hit_rate"],
                time_window=timedelta(hours=1),
                max_frequency=timedelta(hours=2)
            ),
            
            # Правило: превышение квоты токенов сессии
            AlertRule(
                name="session_quota_exceeded",
                type=AlertType.QUOTA_EXCEEDED,
                severity=AlertSeverity.HIGH,
                condition=lambda stats: stats.get('session_tokens', 0) > thresholds["max_session_tokens"],
                threshold_value=thresholds["max_session_tokens"],
                time_window=timedelta(hours=1),
                max_frequency=timedelta(hours=1)
            ),
            
            # Правило: критически низкая успешность
            AlertRule(
                name="low_success_rate",
                type=AlertType.SYSTEM_ERROR,
                severity=AlertSeverity.CRITICAL,
                condition=lambda stats: stats.get('success_rate', 1.0) < thresholds["min_success_rate"],
                threshold_value=thresholds["min_success_rate"],
                time_window=timedelta(minutes=10),
                max_frequency=timedelta(minutes=30)
            )
        ]
        
        return rules
    
    def check_metrics(self, agent: str, mcp_server: str, metrics: Dict[str, Any]):
        """Проверка метрик на соответствие правилам предупреждений"""
        current_time = datetime.now()
        
        # Обновление статистики
        self.update_mcp_stats(agent, mcp_server, metrics)
        
        # Проверка каждого правила
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Проверка частоты алертов (защита от спама)
            rule_key = f"{agent}:{mcp_server}:{rule.name}"
            last_alert_time = self.mcp_stats['last_alert_time'].get(rule_key)
            
            if (last_alert_time and 
                current_time - last_alert_time < rule.max_frequency):
                continue
            
            # Проверка условия правила
            enhanced_metrics = self.get_enhanced_metrics(agent, mcp_server, metrics)
            
            if rule.condition(enhanced_metrics):
                self.generate_alert(rule, agent, mcp_server, enhanced_metrics)
                self.mcp_stats['last_alert_time'][rule_key] = current_time
    
    def update_mcp_stats(self, agent: str, mcp_server: str, metrics: Dict[str, Any]):
        """Обновление статистики MCP для анализа трендов"""
        server_key = f"{agent}:{mcp_server}"
        
        # Счетчики запросов
        if server_key not in self.mcp_stats['requests_count']:
            self.mcp_stats['requests_count'][server_key] = 0
        self.mcp_stats['requests_count'][server_key] += 1
        
        # Обновление времени ответа (скользящее среднее)
        response_time = metrics.get('response_time', 0)
        if server_key not in self.mcp_stats['response_times']:
            self.mcp_stats['response_times'][server_key] = []
        
        self.mcp_stats['response_times'][server_key].append(response_time)
        # Ограничиваем историю последними 20 запросами
        if len(self.mcp_stats['response_times'][server_key]) > 20:
            self.mcp_stats['response_times'][server_key].pop(0)
        
        # Подсчет неудач
        if not metrics.get('success', True):
            if server_key not in self.mcp_stats['failure_count']:
                self.mcp_stats['failure_count'][server_key] = 0
            self.mcp_stats['failure_count'][server_key] += 1
        else:
            # Сброс счетчика при успешном запросе
            self.mcp_stats['failure_count'][server_key] = 0
        
        # Учет потребления токенов
        tokens = metrics.get('tokens_used', 0)
        if server_key not in self.mcp_stats['token_usage']:
            self.mcp_stats['token_usage'][server_key] = []
        
        self.mcp_stats['token_usage'][server_key].append(tokens)
        if len(self.mcp_stats['token_usage'][server_key]) > 50:
            self.mcp_stats['token_usage'][server_key].pop(0)
    
    def get_enhanced_metrics(self, agent: str, mcp_server: str, 
                           base_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Получение расширенных метрик для анализа"""
        server_key = f"{agent}:{mcp_server}"
        enhanced = base_metrics.copy()
        
        # Добавление исторических данных
        response_times = self.mcp_stats['response_times'].get(server_key, [])
        if response_times:
            enhanced['avg_response_time'] = sum(response_times) / len(response_times)
            enhanced['max_response_time'] = max(response_times)
        
        # Подсчет последовательных неудач
        enhanced['consecutive_failures'] = self.mcp_stats['failure_count'].get(server_key, 0)
        
        # Расчет успешности
        total_requests = self.mcp_stats['requests_count'].get(server_key, 1)
        total_failures = self.mcp_stats['failure_count'].get(server_key, 0)
        enhanced['success_rate'] = (total_requests - total_failures) / total_requests
        
        # Анализ потребления токенов
        token_history = self.mcp_stats['token_usage'].get(server_key, [])
        if token_history:
            enhanced['avg_tokens'] = sum(token_history) / len(token_history)
            enhanced['session_tokens'] = sum(token_history)
        
        # Примерная оценка cache hit rate (требует интеграции с cache_manager)
        cached_requests = sum(1 for m in [base_metrics] if m.get('cached', False))
        enhanced['cache_hit_rate'] = cached_requests / max(1, len([base_metrics]))
        
        return enhanced
    
    def generate_alert(self, rule: AlertRule, agent: str, mcp_server: str, 
                      metrics: Dict[str, Any]):
        """Генерация предупреждения"""
        alert_id = f"{rule.name}_{agent}_{mcp_server}_{int(time.time())}"
        
        # Формирование сообщения
        title, message = self.format_alert_message(rule, agent, mcp_server, metrics)
        
        alert = Alert(
            id=alert_id,
            type=rule.type,
            severity=rule.severity,
            title=title,
            message=message,
            details={
                'rule_name': rule.name,
                'threshold': rule.threshold_value,
                'actual_value': self.get_actual_value(rule, metrics),
                'metrics': metrics,
                'agent': agent,
                'mcp_server': mcp_server
            },
            agent=agent,
            mcp_server=mcp_server,
            timestamp=datetime.now()
        )
        
        # Добавление в очередь для обработки
        self.alert_queue.put(alert)
    
    def format_alert_message(self, rule: AlertRule, agent: str, mcp_server: str,
                           metrics: Dict[str, Any]) -> tuple[str, str]:
        """Форматирование сообщения предупреждения"""
        severity_emoji = {
            AlertSeverity.LOW: "💙",
            AlertSeverity.MEDIUM: "💛", 
            AlertSeverity.HIGH: "🧡",
            AlertSeverity.CRITICAL: "🔴"
        }
        
        agent_emoji = {
            'architect': '🧠',
            'engineer': '🧪',
            'integrator': '📦', 
            'critic': '🛡️',
            'manager': '🧭',
            'optimizer': '💰'
        }
        
        emoji = severity_emoji.get(rule.severity, "⚠️")
        agent_icon = agent_emoji.get(agent, "👤")
        
        if rule.type == AlertType.PERFORMANCE_DEGRADATION:
            actual_time = metrics.get('response_time', 0)
            title = f"Медленный ответ от {mcp_server}"
            message = (f"{emoji} [{agent_icon} {agent} → {mcp_server}] "
                      f"Время ответа {actual_time:.1f}сек превышает лимит {rule.threshold_value}сек")
        
        elif rule.type == AlertType.HIGH_TOKEN_USAGE:
            actual_tokens = metrics.get('tokens_used', 0)
            title = f"Высокое потребление токенов"
            message = (f"{emoji} [{agent_icon} {agent} → {mcp_server}] "
                      f"Использовано {actual_tokens} токенов (лимит: {rule.threshold_value})")
        
        elif rule.type == AlertType.REPEATED_FAILURES:
            failures = metrics.get('consecutive_failures', 0)
            title = f"Серия неудачных запросов"
            message = (f"{emoji} [{agent_icon} {agent} → {mcp_server}] "
                      f"{failures} неудачных запросов подряд")
        
        elif rule.type == AlertType.CACHE_INEFFICIENCY:
            cache_rate = metrics.get('cache_hit_rate', 0) * 100
            title = f"Низкая эффективность кэша"
            message = (f"{emoji} [{agent_icon} {agent} → {mcp_server}] "
                      f"Cache hit rate: {cache_rate:.1f}% (мин: {rule.threshold_value*100:.1f}%)")
        
        elif rule.type == AlertType.QUOTA_EXCEEDED:
            session_tokens = metrics.get('session_tokens', 0)
            title = f"Превышена квота токенов сессии"
            message = (f"{emoji} Использовано {session_tokens} токенов "
                      f"(лимит: {rule.threshold_value})")
        
        elif rule.type == AlertType.SYSTEM_ERROR:
            success_rate = metrics.get('success_rate', 0) * 100
            title = f"Критически низкая успешность"
            message = (f"{emoji} [{agent_icon} {agent} → {mcp_server}] "
                      f"Успешность: {success_rate:.1f}% (мин: {rule.threshold_value*100:.1f}%)")
        
        else:
            title = f"Предупреждение системы мониторинга"
            message = f"{emoji} [{agent_icon} {agent} → {mcp_server}] {rule.name}"
        
        return title, message
    
    def get_actual_value(self, rule: AlertRule, metrics: Dict[str, Any]) -> Any:
        """Получение фактического значения для сравнения с порогом"""
        if rule.type == AlertType.PERFORMANCE_DEGRADATION:
            return metrics.get('response_time', 0)
        elif rule.type == AlertType.HIGH_TOKEN_USAGE:
            return metrics.get('tokens_used', 0)
        elif rule.type == AlertType.REPEATED_FAILURES:
            return metrics.get('consecutive_failures', 0)
        elif rule.type == AlertType.CACHE_INEFFICIENCY:
            return metrics.get('cache_hit_rate', 0)
        elif rule.type == AlertType.QUOTA_EXCEEDED:
            return metrics.get('session_tokens', 0)
        elif rule.type == AlertType.SYSTEM_ERROR:
            return metrics.get('success_rate', 0)
        return None
    
    def _alert_processor(self):
        """Фоновый процессор предупреждений"""
        while True:
            try:
                alert = self.alert_queue.get(timeout=1.0)
                self.process_alert(alert)
                self.alert_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Ошибка обработки алерта: {e}")
    
    def process_alert(self, alert: Alert):
        """Обработка предупреждения"""
        with self.lock:
            # Сохранение в историю
            self.alerts_history.append(alert)
            self.active_alerts[alert.id] = alert
            
            # Логирование в консоль
            if self.config["notification"]["console_output"]:
                self.print_alert(alert)
            
            # Логирование в файл
            if self.config["notification"]["file_logging"]:
                self.log_alert_to_file(alert)
            
            # Отправка email (если настроено)
            if (self.config["notification"]["email_alerts"] and 
                alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]):
                self.send_email_alert(alert)
    
    def print_alert(self, alert: Alert):
        """Вывод предупреждения в консоль"""
        timestamp = alert.timestamp.strftime("%H:%M:%S")
        print(f"\n🚨 [{timestamp}] {alert.title}")
        print(f"   {alert.message}")
        
        if alert.severity == AlertSeverity.CRITICAL:
            print("   ⚡ ТРЕБУЕТ НЕМЕДЛЕННОГО ВНИМАНИЯ!")
    
    def log_alert_to_file(self, alert: Alert):
        """Логирование предупреждения в файл"""
        log_file = Path("logs") / "alerts.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.value,
                'type': alert.type.value,
                'title': alert.title,
                'message': alert.message,
                'details': alert.details
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def send_email_alert(self, alert: Alert):
        """Отправка предупреждения по email"""
        email_config = self.config["email"]
        
        if not email_config["recipients"]:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config["username"]
            msg['To'] = ", ".join(email_config["recipients"])
            msg['Subject'] = f"[MCP Alert] {alert.title}"
            
            body = f"""
            Тип: {alert.type.value}
            Критичность: {alert.severity.value}
            Время: {alert.timestamp}
            Агент: {alert.agent}
            MCP Сервер: {alert.mcp_server}
            
            Сообщение:
            {alert.message}
            
            Детали:
            {json.dumps(alert.details, ensure_ascii=False, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Подтверждение получения предупреждения"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Отметка о решении проблемы"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            del self.active_alerts[alert_id]
            return True
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Получение активных предупреждений"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Сводка по предупреждениям"""
        active_count = len(self.active_alerts)
        total_count = len(self.alerts_history)
        
        # Подсчет по критичности
        severity_counts = {}
        for alert in self.active_alerts.values():
            severity_counts[alert.severity.value] = severity_counts.get(alert.severity.value, 0) + 1
        
        # Топ проблемных серверов
        server_issues = {}
        for alert in self.alerts_history[-50:]:  # Последние 50 алертов
            if alert.mcp_server:
                server_issues[alert.mcp_server] = server_issues.get(alert.mcp_server, 0) + 1
        
        return {
            'active_alerts': active_count,
            'total_alerts': total_count,
            'severity_breakdown': severity_counts,
            'top_problematic_servers': sorted(server_issues.items(), 
                                            key=lambda x: x[1], reverse=True)[:5]
        }
    
    def cleanup_old_alerts(self, days: int = 7):
        """Очистка старых предупреждений"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Очистка истории
        self.alerts_history = [a for a in self.alerts_history if a.timestamp > cutoff_date]
        
        # Очистка активных алертов (если они очень старые)
        old_active_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.timestamp < cutoff_date
        ]
        
        for alert_id in old_active_alerts:
            del self.active_alerts[alert_id]
        
        return len(old_active_alerts)

# Глобальный экземпляр системы предупреждений
alert_system = AlertSystem()

def check_mcp_metrics(agent: str, mcp_server: str, metrics: Dict[str, Any]):
    """Проверка метрик MCP на предупреждения"""
    alert_system.check_metrics(agent, mcp_server, metrics)

def get_active_alerts(severity: Optional[AlertSeverity] = None) -> List[Alert]:
    """Получение активных предупреждений"""
    return alert_system.get_active_alerts(severity)

def acknowledge_alert(alert_id: str) -> bool:
    """Подтверждение предупреждения"""
    return alert_system.acknowledge_alert(alert_id)

def resolve_alert(alert_id: str) -> bool:
    """Решение проблемы"""
    return alert_system.resolve_alert(alert_id)

def print_alert_summary():
    """Вывод сводки по предупреждениям"""
    summary = alert_system.get_alert_summary()
    
    print("\n🚨 === СВОДКА ПРЕДУПРЕЖДЕНИЙ ===")
    print(f"🔴 Активные алерты: {summary['active_alerts']}")
    print(f"📊 Всего за историю: {summary['total_alerts']}")
    
    if summary['severity_breakdown']:
        print("\nПо критичности:")
        for severity, count in summary['severity_breakdown'].items():
            emoji = {"low": "💙", "medium": "💛", "high": "🧡", "critical": "🔴"}
            print(f"  {emoji.get(severity, '⚠️')} {severity}: {count}")
    
    if summary['top_problematic_servers']:
        print("\nПроблемные серверы:")
        for server, count in summary['top_problematic_servers']:
            print(f"  • {server}: {count} алертов")

if __name__ == "__main__":
    # Демонстрация системы предупреждений
    print("🚨 Alert System инициализирован")
    
    # Тест предупреждения
    test_metrics = {
        'response_time': 12.0,  # Превышает лимит
        'tokens_used': 500,
        'success': True
    }
    
    alert_system.check_metrics("architect", "context7", test_metrics)
    
    time.sleep(1)  # Даем время обработчику
    print_alert_summary()