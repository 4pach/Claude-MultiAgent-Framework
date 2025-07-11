#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Performance Monitor - Основной модуль мониторинга производительности MCP серверов
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class MCPRequest:
    """Структура данных для запроса к MCP серверу"""
    agent: str
    mcp_server: str
    query: str
    timestamp: datetime
    request_id: str
    estimated_tokens: int = 0

@dataclass
class MCPResponse:
    """Структура данных для ответа от MCP сервера"""
    request_id: str
    success: bool
    response_time: float
    tokens_used: int
    response_size: int
    cached: bool = False
    error_message: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Метрики производительности для анализа"""
    total_requests: int = 0
    total_tokens: int = 0
    total_time: float = 0.0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    agent_usage: Dict[str, int] = None
    server_usage: Dict[str, int] = None

class MCPMonitor:
    """Основной класс мониторинга MCP производительности"""
    
    def __init__(self, config_path: str = ".mcp.json"):
        self.config_path = Path(config_path)
        self.monitoring_data = []
        self.session_start = datetime.now()
        self.cache = {}
        self.performance_thresholds = {
            'max_response_time': 10.0,  # секунды
            'max_tokens_per_request': 1000,
            'max_session_tokens': 5000,
            'warning_response_time': 5.0
        }
        
        # Настройка логирования
        self.setup_logging()
        
        # Загрузка конфигурации MCP
        self.mcp_config = self.load_mcp_config()
        
    def setup_logging(self):
        """Настройка системы логирования"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "mcp_monitor.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("MCPMonitor")
        
    def load_mcp_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации MCP серверов"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Конфигурационный файл {self.config_path} не найден")
                return {"mcpServers": {}}
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {"mcpServers": {}}
    
    def log_request(self, agent: str, mcp_server: str, query: str, 
                   estimated_tokens: int = 0) -> str:
        """Логирование запроса к MCP серверу"""
        request_id = f"{int(time.time() * 1000)}_{len(self.monitoring_data)}"
        
        request = MCPRequest(
            agent=agent,
            mcp_server=mcp_server,
            query=query,
            timestamp=datetime.now(),
            request_id=request_id,
            estimated_tokens=estimated_tokens
        )
        
        # Проверка кэша
        cache_key = f"{mcp_server}:{hash(query)}"
        if cache_key in self.cache:
            self.logger.info(f"🔄 [💰 Оптимизатор] ДУБЛИКАТ ОБНАРУЖЕН: {cache_key}")
            return self.use_cached_response(cache_key, request_id)
        
        self.monitoring_data.append({"type": "request", "data": asdict(request)})
        
        # Логирование в формате мультиагентной архитектуры
        agent_emoji = self.get_agent_emoji(agent)
        self.logger.info(f"[{agent_emoji} {agent} → {mcp_server}] {query[:50]}...")
        
        return request_id
    
    def log_response(self, request_id: str, success: bool, response_time: float,
                    tokens_used: int, response_size: int, 
                    error_message: Optional[str] = None) -> str:
        """Логирование ответа от MCP сервера"""
        response = MCPResponse(
            request_id=request_id,
            success=success,
            response_time=response_time,
            tokens_used=tokens_used,
            response_size=response_size,
            error_message=error_message
        )
        
        self.monitoring_data.append({"type": "response", "data": asdict(response)})
        
        # Анализ производительности
        optimization_message = self.analyze_response_performance(response)
        
        # Логирование ответа
        self.logger.info(f"[MCP Response] {tokens_used} токенов, {response_time:.1f}сек")
        self.logger.info(f"[💰 Оптимизатор] {optimization_message}")
        
        # Кэширование успешного ответа
        if success and self.should_cache_response(response):
            self.cache_response(request_id, response)
        
        return optimization_message
    
    def analyze_response_performance(self, response: MCPResponse) -> str:
        """Анализ производительности ответа и генерация рекомендаций"""
        if not response.success:
            return f"❌ Ошибка: {response.error_message}"
        
        if response.response_time > self.performance_thresholds['max_response_time']:
            return f"⚠️ Длительное выполнение: {response.response_time:.1f}сек (лимит: {self.performance_thresholds['max_response_time']}сек)"
        
        if response.tokens_used > self.performance_thresholds['max_tokens_per_request']:
            return f"💡 Большой ответ: {response.tokens_used} токенов, рекомендую сузить запрос"
        
        if response.response_time > self.performance_thresholds['warning_response_time']:
            return f"⚠️ Предупреждение: можно оптимизировать время выполнения ({response.response_time:.1f}сек)"
        
        if response.tokens_used < 100:
            return f"✅ Эффективно: минимальное использование ресурсов"
        
        return f"✅ Хорошо: оптимальное использование ресурсов"
    
    def should_cache_response(self, response: MCPResponse) -> bool:
        """Определение необходимости кэширования ответа"""
        # Кэшируем успешные ответы среднего размера
        return (response.success and 
                100 <= response.tokens_used <= 800 and
                response.response_time < 10.0)
    
    def cache_response(self, request_id: str, response: MCPResponse):
        """Кэширование ответа для повторного использования"""
        # Находим соответствующий запрос
        request_data = None
        for item in self.monitoring_data:
            if (item["type"] == "request" and 
                item["data"]["request_id"] == request_id):
                request_data = item["data"]
                break
        
        if request_data:
            cache_key = f"{request_data['mcp_server']}:{hash(request_data['query'])}"
            cache_ttl = self.get_cache_ttl(request_data['mcp_server'])
            
            self.cache[cache_key] = {
                'response': asdict(response),
                'expires': datetime.now() + timedelta(seconds=cache_ttl),
                'usage_count': 0
            }
            
            self.logger.info(f"💾 Ответ кэширован: {cache_key} (TTL: {cache_ttl}сек)")
    
    def get_cache_ttl(self, mcp_server: str) -> int:
        """Получение времени жизни кэша для конкретного MCP сервера"""
        ttl_mapping = {
            'context7': 14400,      # 4 часа
            'github': 86400,        # 24 часа  
            'exa': 43200,          # 12 часов
            'taskmaster-ai': 7200,  # 2 часа
            'wcgw': 3600,          # 1 час
            'youtube-transcript': 172800  # 48 часов
        }
        return ttl_mapping.get(mcp_server, 3600)  # по умолчанию 1 час
    
    def use_cached_response(self, cache_key: str, request_id: str) -> str:
        """Использование кэшированного ответа"""
        cached_data = self.cache[cache_key]
        cached_response = cached_data['response']
        
        # Увеличиваем счетчик использования
        cached_data['usage_count'] += 1
        
        # Создаем новый ответ на основе кэшированного
        response = MCPResponse(
            request_id=request_id,
            success=cached_response['success'],
            response_time=0.1,  # мгновенный ответ из кэша
            tokens_used=cached_response['tokens_used'],
            response_size=cached_response['response_size'],
            cached=True
        )
        
        self.monitoring_data.append({"type": "response", "data": asdict(response)})
        
        savings_time = cached_response['response_time']
        savings_tokens = cached_response['tokens_used']
        
        self.logger.info(f"[MCP Response] Кэшированный ответ (0.1сек)")
        return f"🔄 Использован кэш. Экономия: {savings_tokens} токенов, {savings_time:.1f}сек"
    
    def get_agent_emoji(self, agent: str) -> str:
        """Получение эмодзи для подагента"""
        emoji_mapping = {
            'architect': '🧠',
            'engineer': '🧪', 
            'integrator': '📦',
            'critic': '🛡️',
            'manager': '🧭',
            'optimizer': '💰'
        }
        return emoji_mapping.get(agent.lower(), '👤')
    
    def generate_session_report(self) -> PerformanceMetrics:
        """Генерация отчета по текущей сессии"""
        requests = [item["data"] for item in self.monitoring_data if item["type"] == "request"]
        responses = [item["data"] for item in self.monitoring_data if item["type"] == "response"]
        
        if not responses:
            return PerformanceMetrics()
        
        # Расчет основных метрик
        total_requests = len(responses)
        successful_responses = [r for r in responses if r["success"]]
        total_tokens = sum(r["tokens_used"] for r in responses)
        total_time = sum(r["response_time"] for r in responses)
        cached_responses = [r for r in responses if r.get("cached", False)]
        
        success_rate = len(successful_responses) / total_requests if total_requests > 0 else 0
        avg_response_time = total_time / total_requests if total_requests > 0 else 0
        cache_hit_rate = len(cached_responses) / total_requests if total_requests > 0 else 0
        
        # Анализ использования по агентам и серверам
        agent_usage = {}
        server_usage = {}
        
        for request in requests:
            agent = request["agent"]
            server = request["mcp_server"]
            
            agent_usage[agent] = agent_usage.get(agent, 0) + 1
            server_usage[server] = server_usage.get(server, 0) + 1
        
        return PerformanceMetrics(
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_time=total_time,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            cache_hit_rate=cache_hit_rate,
            agent_usage=agent_usage,
            server_usage=server_usage
        )
    
    def print_session_summary(self):
        """Вывод сводки по сессии"""
        metrics = self.generate_session_report()
        session_duration = datetime.now() - self.session_start
        
        print("\n" + "="*60)
        print("[💰 Оптимизатор] === СВОДКА СЕССИИ ===")
        print("="*60)
        print(f"📅 Продолжительность сессии: {session_duration}")
        print(f"📊 Всего запросов: {metrics.total_requests}")
        print(f"🎯 Успешность: {metrics.success_rate:.1%}")
        print(f"⏱️  Среднее время ответа: {metrics.avg_response_time:.1f}сек")
        print(f"💾 Кэш hit rate: {metrics.cache_hit_rate:.1%}")
        print(f"🔢 Всего токенов: {metrics.total_tokens:,}")
        print(f"⏰ Общее время: {metrics.total_time:.1f}сек")
        
        if metrics.agent_usage:
            print("\n📈 Использование по агентам:")
            for agent, count in sorted(metrics.agent_usage.items(), key=lambda x: x[1], reverse=True):
                emoji = self.get_agent_emoji(agent)
                print(f"  {emoji} {agent}: {count} запросов")
        
        if metrics.server_usage:
            print("\n🌐 Использование по серверам:")
            for server, count in sorted(metrics.server_usage.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {server}: {count} запросов")
        
        # Рекомендации оптимизатора
        self.print_optimization_recommendations(metrics)
        
        print("="*60)
    
    def print_optimization_recommendations(self, metrics: PerformanceMetrics):
        """Генерация и вывод рекомендаций по оптимизации"""
        print("\n💡 Рекомендации оптимизатора:")
        
        if metrics.cache_hit_rate < 0.3:
            print("  • Увеличить использование кэшированных запросов")
        
        if metrics.avg_response_time > 5.0:
            print("  • Оптимизировать запросы для уменьшения времени ответа")
        
        if metrics.total_tokens > self.performance_thresholds['max_session_tokens']:
            print(f"  • Превышен лимит токенов сессии ({metrics.total_tokens}/{self.performance_thresholds['max_session_tokens']})")
        
        if metrics.success_rate < 0.95:
            print("  • Проверить причины неуспешных запросов")
        
        # Анализ наиболее используемых серверов
        if metrics.server_usage:
            most_used = max(metrics.server_usage.items(), key=lambda x: x[1])
            if most_used[1] > metrics.total_requests * 0.5:
                print(f"  • Рассмотреть дополнительную оптимизацию сервера {most_used[0]}")
    
    def cleanup_expired_cache(self):
        """Очистка устаревшего кэша"""
        now = datetime.now()
        expired_keys = []
        
        for key, data in self.cache.items():
            if now > data['expires']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            self.logger.info(f"🗑️ Удален устаревший кэш: {key}")
    
    def save_monitoring_data(self, filepath: str = None):
        """Сохранение данных мониторинга в файл"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"logs/monitoring_session_{timestamp}.json"
        
        Path("logs").mkdir(exist_ok=True)
        
        session_data = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'monitoring_data': self.monitoring_data,
            'performance_metrics': asdict(self.generate_session_report()),
            'cache_stats': {
                'total_entries': len(self.cache),
                'cache_usage': {k: v['usage_count'] for k, v in self.cache.items()}
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"📄 Данные мониторинга сохранены: {filepath}")

# Глобальный экземпляр монитора
mcp_monitor = MCPMonitor()

def log_mcp_request(agent: str, mcp_server: str, query: str, estimated_tokens: int = 0) -> str:
    """Удобная функция для логирования MCP запроса"""
    return mcp_monitor.log_request(agent, mcp_server, query, estimated_tokens)

def log_mcp_response(request_id: str, success: bool, response_time: float,
                    tokens_used: int, response_size: int, 
                    error_message: str = None) -> str:
    """Удобная функция для логирования MCP ответа"""
    return mcp_monitor.log_response(request_id, success, response_time, 
                                  tokens_used, response_size, error_message)

def print_session_summary():
    """Удобная функция для вывода сводки сессии"""
    mcp_monitor.print_session_summary()

def save_session_data(filepath: str = None):
    """Удобная функция для сохранения данных сессии"""
    mcp_monitor.save_monitoring_data(filepath)

if __name__ == "__main__":
    # Пример использования
    print("🔧 MCP Monitor инициализирован")
    print("📊 Используйте функции log_mcp_request() и log_mcp_response() для мониторинга")
    print("📈 Вызовите print_session_summary() для просмотра статистики")