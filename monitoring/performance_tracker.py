#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Tracker - Трекер производительности для анализа паттернов использования MCP
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System  
Дата: 2025-07-11
"""

import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
import asyncio

@dataclass
class PerformanceRecord:
    """Запись производительности для базы данных"""
    timestamp: datetime
    agent: str
    mcp_server: str
    query_hash: str
    query_length: int
    response_time: float
    tokens_used: int
    success: bool
    cached: bool
    session_id: str

@dataclass
class TrendAnalysis:
    """Анализ трендов производительности"""
    server_name: str
    avg_response_time: float
    avg_tokens: float
    success_rate: float
    cache_hit_rate: float
    usage_frequency: int
    trend_direction: str  # 'improving', 'degrading', 'stable'
    efficiency_score: float

class PerformanceTracker:
    """Трекер производительности MCP серверов"""
    
    def __init__(self, db_path: str = "monitoring/performance.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.session_id = f"session_{int(datetime.now().timestamp())}"
        self.lock = threading.Lock()
        
        # Инициализация базы данных
        self.init_database()
        
        # Пороги для анализа
        self.performance_thresholds = {
            'excellent_response_time': 2.0,
            'good_response_time': 5.0,
            'poor_response_time': 10.0,
            'efficient_tokens': 500,
            'verbose_tokens': 1000,
            'minimum_cache_rate': 0.3,
            'excellent_cache_rate': 0.7
        }
    
    def init_database(self):
        """Инициализация SQLite базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    mcp_server TEXT NOT NULL,
                    query_hash TEXT NOT NULL,
                    query_length INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    cached BOOLEAN NOT NULL,
                    session_id TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON performance_records(timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_mcp_server ON performance_records(mcp_server)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_session ON performance_records(session_id)
            ''')
    
    def record_performance(self, agent: str, mcp_server: str, query: str,
                          response_time: float, tokens_used: int, 
                          success: bool, cached: bool = False):
        """Запись данных производительности"""
        record = PerformanceRecord(
            timestamp=datetime.now(),
            agent=agent,
            mcp_server=mcp_server,
            query_hash=str(hash(query)),
            query_length=len(query),
            response_time=response_time,
            tokens_used=tokens_used,
            success=success,
            cached=cached,
            session_id=self.session_id
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO performance_records 
                    (timestamp, agent, mcp_server, query_hash, query_length,
                     response_time, tokens_used, success, cached, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.timestamp.isoformat(),
                    record.agent,
                    record.mcp_server,
                    record.query_hash,
                    record.query_length,
                    record.response_time,
                    record.tokens_used,
                    record.success,
                    record.cached,
                    record.session_id
                ))
    
    def get_server_performance(self, server_name: str, days: int = 7) -> TrendAnalysis:
        """Анализ производительности конкретного сервера"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT response_time, tokens_used, success, cached
                FROM performance_records
                WHERE mcp_server = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (server_name, cutoff_date.isoformat()))
            
            records = cursor.fetchall()
        
        if not records:
            return TrendAnalysis(
                server_name=server_name,
                avg_response_time=0.0,
                avg_tokens=0.0,
                success_rate=0.0,
                cache_hit_rate=0.0,
                usage_frequency=0,
                trend_direction='no_data',
                efficiency_score=0.0
            )
        
        # Вычисление базовых метрик
        response_times = [r[0] for r in records]
        token_counts = [r[1] for r in records]
        successes = [r[2] for r in records]
        cached = [r[3] for r in records]
        
        avg_response_time = statistics.mean(response_times)
        avg_tokens = statistics.mean(token_counts)
        success_rate = sum(successes) / len(successes)
        cache_hit_rate = sum(cached) / len(cached)
        usage_frequency = len(records)
        
        # Анализ тренда (сравнение первой и второй половины периода)
        mid_point = len(records) // 2
        if mid_point > 0:
            early_avg = statistics.mean(response_times[mid_point:])
            recent_avg = statistics.mean(response_times[:mid_point])
            
            if recent_avg < early_avg * 0.9:
                trend_direction = 'improving'
            elif recent_avg > early_avg * 1.1:
                trend_direction = 'degrading'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'insufficient_data'
        
        # Расчет efficiency score (0-100)
        efficiency_score = self.calculate_efficiency_score(
            avg_response_time, avg_tokens, success_rate, cache_hit_rate
        )
        
        return TrendAnalysis(
            server_name=server_name,
            avg_response_time=avg_response_time,
            avg_tokens=avg_tokens,
            success_rate=success_rate,
            cache_hit_rate=cache_hit_rate,
            usage_frequency=usage_frequency,
            trend_direction=trend_direction,
            efficiency_score=efficiency_score
        )
    
    def calculate_efficiency_score(self, response_time: float, tokens: float,
                                 success_rate: float, cache_hit_rate: float) -> float:
        """Расчет комплексного показателя эффективности (0-100)"""
        # Нормализация метрик (0-1)
        time_score = max(0, min(1, (10 - response_time) / 10))
        token_score = max(0, min(1, (1000 - tokens) / 1000))
        
        # Взвешенная сумма
        efficiency = (
            time_score * 0.3 +           # Скорость - 30%
            token_score * 0.25 +         # Экономичность - 25%
            success_rate * 0.25 +        # Надежность - 25%
            cache_hit_rate * 0.2         # Кэширование - 20%
        )
        
        return round(efficiency * 100, 1)
    
    def get_agent_performance_summary(self, days: int = 7) -> Dict[str, Dict]:
        """Сводка производительности по агентам"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT agent, AVG(response_time), AVG(tokens_used), 
                       AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END),
                       AVG(CASE WHEN cached THEN 1.0 ELSE 0.0 END),
                       COUNT(*)
                FROM performance_records
                WHERE timestamp > ?
                GROUP BY agent
                ORDER BY COUNT(*) DESC
            ''', (cutoff_date.isoformat(),))
            
            results = {}
            for row in cursor.fetchall():
                agent, avg_time, avg_tokens, success_rate, cache_rate, count = row
                results[agent] = {
                    'avg_response_time': round(avg_time, 2),
                    'avg_tokens': round(avg_tokens, 1),
                    'success_rate': round(success_rate, 3),
                    'cache_hit_rate': round(cache_rate, 3),
                    'usage_count': count,
                    'efficiency_score': self.calculate_efficiency_score(
                        avg_time, avg_tokens, success_rate, cache_rate
                    )
                }
        
        return results
    
    def identify_performance_anomalies(self, days: int = 7) -> List[Dict]:
        """Выявление аномалий производительности"""
        anomalies = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Поиск медленных запросов
            cursor = conn.execute('''
                SELECT timestamp, agent, mcp_server, response_time, tokens_used
                FROM performance_records
                WHERE timestamp > ? AND response_time > ?
                ORDER BY response_time DESC
                LIMIT 10
            ''', (cutoff_date.isoformat(), self.performance_thresholds['poor_response_time']))
            
            for row in cursor.fetchall():
                anomalies.append({
                    'type': 'slow_response',
                    'timestamp': row[0],
                    'agent': row[1],
                    'server': row[2],
                    'response_time': row[3],
                    'tokens': row[4],
                    'severity': 'high' if row[3] > 15 else 'medium'
                })
            
            # Поиск чрезмерно токен-потребляющих запросов
            cursor = conn.execute('''
                SELECT timestamp, agent, mcp_server, response_time, tokens_used
                FROM performance_records
                WHERE timestamp > ? AND tokens_used > ?
                ORDER BY tokens_used DESC
                LIMIT 10
            ''', (cutoff_date.isoformat(), self.performance_thresholds['verbose_tokens']))
            
            for row in cursor.fetchall():
                anomalies.append({
                    'type': 'high_token_usage',
                    'timestamp': row[0],
                    'agent': row[1],
                    'server': row[2],
                    'response_time': row[3],
                    'tokens': row[4],
                    'severity': 'medium' if row[4] < 1500 else 'high'
                })
            
            # Поиск серверов с низким success rate
            cursor = conn.execute('''
                SELECT mcp_server, AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate,
                       COUNT(*) as total_requests
                FROM performance_records
                WHERE timestamp > ?
                GROUP BY mcp_server
                HAVING success_rate < 0.9 AND total_requests >= 3
                ORDER BY success_rate ASC
            ''', (cutoff_date.isoformat(),))
            
            for row in cursor.fetchall():
                anomalies.append({
                    'type': 'low_success_rate',
                    'server': row[0],
                    'success_rate': round(row[1], 3),
                    'total_requests': row[2],
                    'severity': 'high' if row[1] < 0.7 else 'medium'
                })
        
        return anomalies
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Генерация рекомендаций по оптимизации"""
        recommendations = []
        
        # Анализ всех серверов
        servers = self.get_all_servers()
        for server in servers:
            analysis = self.get_server_performance(server)
            
            if analysis.efficiency_score < 50:
                recommendations.append(
                    f"🔴 {server}: низкая эффективность ({analysis.efficiency_score}%), "
                    f"требует оптимизации"
                )
            
            if analysis.avg_response_time > self.performance_thresholds['poor_response_time']:
                recommendations.append(
                    f"⏰ {server}: медленные ответы ({analysis.avg_response_time:.1f}сек), "
                    f"рассмотреть упрощение запросов"
                )
            
            if analysis.cache_hit_rate < self.performance_thresholds['minimum_cache_rate']:
                recommendations.append(
                    f"💾 {server}: низкое использование кэша ({analysis.cache_hit_rate:.1%}), "
                    f"увеличить TTL или улучшить стратегию кэширования"
                )
            
            if analysis.trend_direction == 'degrading':
                recommendations.append(
                    f"📉 {server}: ухудшение производительности, "
                    f"требует внимания"
                )
        
        # Анализ агентов
        agent_stats = self.get_agent_performance_summary()
        for agent, stats in agent_stats.items():
            if stats['efficiency_score'] < 60:
                recommendations.append(
                    f"👤 Агент {agent}: эффективность {stats['efficiency_score']}%, "
                    f"пересмотреть стратегию использования MCP"
                )
        
        # Общие рекомендации
        anomalies = self.identify_performance_anomalies()
        high_severity_anomalies = [a for a in anomalies if a.get('severity') == 'high']
        
        if len(high_severity_anomalies) > 3:
            recommendations.append(
                f"⚠️ Обнаружено {len(high_severity_anomalies)} критических аномалий, "
                f"требуется срочная оптимизация"
            )
        
        return recommendations
    
    def get_all_servers(self) -> List[str]:
        """Получение списка всех используемых серверов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT DISTINCT mcp_server FROM performance_records
                ORDER BY mcp_server
            ''')
            return [row[0] for row in cursor.fetchall()]
    
    def export_performance_report(self, filepath: str = None) -> str:
        """Экспорт детального отчета производительности"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"reports/performance_report_{timestamp}.json"
        
        Path("reports").mkdir(exist_ok=True)
        
        # Сбор всех данных
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'analysis_period_days': 7,
            'server_analyses': {},
            'agent_performance': self.get_agent_performance_summary(),
            'anomalies': self.identify_performance_anomalies(),
            'recommendations': self.generate_optimization_recommendations()
        }
        
        # Анализ по серверам
        for server in self.get_all_servers():
            analysis = self.get_server_performance(server)
            report_data['server_analyses'][server] = asdict(analysis)
        
        # Сохранение отчета
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        return filepath
    
    def get_session_statistics(self) -> Dict:
        """Статистика текущей сессии"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*), AVG(response_time), SUM(tokens_used),
                       AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END),
                       AVG(CASE WHEN cached THEN 1.0 ELSE 0.0 END)
                FROM performance_records
                WHERE session_id = ?
            ''', (self.session_id,))
            
            row = cursor.fetchone()
            if row[0] == 0:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0.0,
                    'total_tokens': 0,
                    'success_rate': 0.0,
                    'cache_hit_rate': 0.0
                }
            
            return {
                'total_requests': row[0],
                'avg_response_time': round(row[1], 2),
                'total_tokens': row[2],
                'success_rate': round(row[3], 3),
                'cache_hit_rate': round(row[4], 3)
            }
    
    def cleanup_old_records(self, days_to_keep: int = 30):
        """Очистка старых записей"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM performance_records
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            
        return deleted_count

# Глобальный экземпляр трекера
performance_tracker = PerformanceTracker()

def record_mcp_performance(agent: str, mcp_server: str, query: str,
                          response_time: float, tokens_used: int, 
                          success: bool, cached: bool = False):
    """Удобная функция для записи производительности"""
    performance_tracker.record_performance(
        agent, mcp_server, query, response_time, tokens_used, success, cached
    )

def get_performance_recommendations() -> List[str]:
    """Получение рекомендаций по оптимизации"""
    return performance_tracker.generate_optimization_recommendations()

def export_performance_report(filepath: str = None) -> str:
    """Экспорт отчета производительности"""
    return performance_tracker.export_performance_report(filepath)

if __name__ == "__main__":
    # Демонстрация возможностей
    tracker = PerformanceTracker()
    
    print("📊 Performance Tracker инициализирован")
    print("🔍 Анализ производительности MCP серверов...")
    
    # Пример анализа
    servers = tracker.get_all_servers()
    if servers:
        for server in servers:
            analysis = tracker.get_server_performance(server)
            print(f"\n📈 {server}:")
            print(f"  Эффективность: {analysis.efficiency_score}%")
            print(f"  Среднее время: {analysis.avg_response_time:.1f}сек")
            print(f"  Тренд: {analysis.trend_direction}")
    else:
        print("ℹ️ Нет данных для анализа")