#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Manager - Интеллектуальное управление кэшем MCP запросов
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import hashlib
import pickle
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import gzip
import sqlite3

@dataclass
class CacheEntry:
    """Запись в кэше"""
    key: str
    agent: str
    mcp_server: str
    query_hash: str
    response_data: Any
    tokens_used: int
    response_time: float
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: datetime
    quality_score: float

@dataclass
class CacheStats:
    """Статистика кэша"""
    total_entries: int
    total_size_mb: float
    hit_rate: float
    miss_rate: float
    space_efficiency: float
    avg_access_count: float
    expiration_rate: float

class IntelligentCacheManager:
    """Интеллектуальный менеджер кэша MCP запросов"""
    
    def __init__(self, cache_dir: str = "monitoring/cache", max_size_mb: float = 100.0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_mb = max_size_mb
        self.lock = threading.RLock()
        
        # База данных для метаданных кэша
        self.db_path = self.cache_dir / "cache_metadata.db"
        
        # Статистика
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Конфигурация TTL по серверам
        self.server_ttl_config = {
            'context7': timedelta(hours=4),
            'github': timedelta(hours=24),
            'exa': timedelta(hours=12),
            'taskmaster-ai': timedelta(hours=2),
            'wcgw': timedelta(hours=1),
            'youtube-transcript': timedelta(hours=48),
            'playwright': timedelta(minutes=30),  # Интерактивные тесты кэшируются ненадолго
            'sequentialthinking': timedelta(minutes=0)  # Не кэшируется
        }
        
        # Качественные показатели для кэширования
        self.quality_thresholds = {
            'min_tokens': 50,      # Минимальное количество токенов для кэширования
            'max_tokens': 1500,    # Максимальное (слишком большие ответы не кэшируем)
            'max_response_time': 20.0,  # Максимальное время ответа
            'min_quality_score': 0.6    # Минимальный показатель качества
        }
        
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных метаданных кэша"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    key TEXT PRIMARY KEY,
                    agent TEXT NOT NULL,
                    mcp_server TEXT NOT NULL,
                    query_hash TEXT NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    file_size INTEGER NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_metadata(expires_at)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_mcp_server ON cache_metadata(mcp_server)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_metadata(last_accessed)
            ''')
    
    def generate_cache_key(self, agent: str, mcp_server: str, query: str) -> str:
        """Генерация ключа кэша"""
        # Нормализация запроса для лучшего попадания в кэш
        normalized_query = self.normalize_query(query)
        
        # Хэш от агента, сервера и нормализованного запроса
        content = f"{agent}:{mcp_server}:{normalized_query}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def normalize_query(self, query: str) -> str:
        """Нормализация запроса для улучшения попаданий в кэш"""
        # Удаление лишних пробелов и приведение к нижнему регистру
        normalized = " ".join(query.lower().strip().split())
        
        # Удаление временных меток и специфичных идентификаторов
        import re
        normalized = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', 'DATE', normalized)
        normalized = re.sub(r'\b\d+\.\d+\.\d+\b', 'VERSION', normalized)
        normalized = re.sub(r'\bid\s*[:=]\s*\w+', 'id:ID', normalized)
        
        return normalized
    
    def calculate_quality_score(self, agent: str, mcp_server: str, query: str,
                               response_data: Any, tokens_used: int, 
                               response_time: float) -> float:
        """Расчет показателя качества для определения ценности кэширования"""
        score = 1.0
        
        # Фактор размера ответа (оптимальный размер = высокий score)
        if tokens_used < self.quality_thresholds['min_tokens']:
            score *= 0.3  # Слишком маленький ответ
        elif tokens_used > self.quality_thresholds['max_tokens']:
            score *= 0.2  # Слишком большой ответ
        else:
            # Оптимальный размер (200-800 токенов)
            optimal_range = (200, 800)
            if optimal_range[0] <= tokens_used <= optimal_range[1]:
                score *= 1.0
            else:
                distance = min(abs(tokens_used - optimal_range[0]), 
                              abs(tokens_used - optimal_range[1]))
                score *= max(0.5, 1.0 - distance / 1000)
        
        # Фактор времени ответа (быстрые ответы менее ценны для кэширования)
        if response_time > 5.0:
            score *= 1.2  # Медленные запросы более ценны для кэширования
        elif response_time < 1.0:
            score *= 0.7  # Быстрые запросы менее ценны
        
        # Фактор типа сервера
        server_priority = {
            'context7': 1.3,      # Документация часто переиспользуется
            'github': 1.2,        # Поиск кода стабилен
            'exa': 1.1,          # Исследования полезно кэшировать
            'taskmaster-ai': 0.8, # Планы часто уникальны
            'wcgw': 0.6,         # Системные команды менее предсказуемы
            'youtube-transcript': 1.5, # Транскрипции не меняются
            'playwright': 0.3,    # Интерактивные тесты уникальны
            'sequentialthinking': 0.0  # Аналитические процессы не кэшируются
        }
        score *= server_priority.get(mcp_server, 1.0)
        
        # Фактор агента (некоторые агенты более предсказуемы)
        agent_priority = {
            'architect': 1.2,     # Поиск документации часто повторяется
            'engineer': 1.1,      # Поиск примеров кода
            'integrator': 1.0,    # Интеграции умеренно повторяются
            'critic': 0.9,        # Анализ безопасности более уникален
            'manager': 0.8,       # Планирование часто уникально
            'optimizer': 1.3      # Анализ метрик стабилен
        }
        score *= agent_priority.get(agent, 1.0)
        
        return min(1.0, max(0.0, score))
    
    def should_cache(self, agent: str, mcp_server: str, query: str,
                    response_data: Any, tokens_used: int, 
                    response_time: float) -> bool:
        """Определение необходимости кэширования"""
        # Проверка базовых ограничений
        if tokens_used < self.quality_thresholds['min_tokens']:
            return False
        
        if tokens_used > self.quality_thresholds['max_tokens']:
            return False
        
        if response_time > self.quality_thresholds['max_response_time']:
            return False
        
        # Серверы, которые не кэшируются
        if mcp_server in ['sequentialthinking', 'playwright']:
            return False
        
        # Расчет показателя качества
        quality_score = self.calculate_quality_score(
            agent, mcp_server, query, response_data, tokens_used, response_time
        )
        
        return quality_score >= self.quality_thresholds['min_quality_score']
    
    def get_ttl(self, mcp_server: str) -> timedelta:
        """Получение времени жизни для сервера"""
        return self.server_ttl_config.get(mcp_server, timedelta(hours=1))
    
    def store(self, agent: str, mcp_server: str, query: str, response_data: Any,
             tokens_used: int, response_time: float) -> Optional[str]:
        """Сохранение ответа в кэш"""
        # Проверка необходимости кэширования
        if not self.should_cache(agent, mcp_server, query, response_data, 
                                tokens_used, response_time):
            return None
        
        with self.lock:
            cache_key = self.generate_cache_key(agent, mcp_server, query)
            
            # Проверка, есть ли уже такая запись
            if self.exists(cache_key):
                self.update_access(cache_key)
                return cache_key
            
            # Создание записи кэша
            now = datetime.now()
            ttl = self.get_ttl(mcp_server)
            expires_at = now + ttl
            
            quality_score = self.calculate_quality_score(
                agent, mcp_server, query, response_data, tokens_used, response_time
            )
            
            # Сохранение данных в файл
            file_path = self.cache_dir / f"{cache_key}.gz"
            with gzip.open(file_path, 'wb') as f:
                pickle.dump(response_data, f)
            
            file_size = file_path.stat().st_size
            
            # Сохранение метаданных в БД
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache_metadata
                    (key, agent, mcp_server, query_hash, tokens_used, response_time,
                     created_at, expires_at, access_count, last_accessed, 
                     quality_score, file_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cache_key, agent, mcp_server, str(hash(query)), tokens_used,
                    response_time, now.isoformat(), expires_at.isoformat(),
                    1, now.isoformat(), quality_score, file_size
                ))
            
            # Проверка лимитов размера
            self.enforce_size_limits()
            
            return cache_key
    
    def retrieve(self, agent: str, mcp_server: str, query: str) -> Optional[Tuple[Any, Dict]]:
        """Получение ответа из кэша"""
        with self.lock:
            cache_key = self.generate_cache_key(agent, mcp_server, query)
            
            # Проверка существования и актуальности
            if not self.exists(cache_key) or self.is_expired(cache_key):
                self.misses += 1
                return None
            
            # Загрузка данных
            file_path = self.cache_dir / f"{cache_key}.gz"
            try:
                with gzip.open(file_path, 'rb') as f:
                    response_data = pickle.load(f)
                
                # Получение метаданных
                metadata = self.get_metadata(cache_key)
                if not metadata:
                    self.misses += 1
                    return None
                
                # Обновление статистики доступа
                self.update_access(cache_key)
                self.hits += 1
                
                return response_data, metadata
                
            except Exception as e:
                # Удаление поврежденной записи
                self.remove(cache_key)
                self.misses += 1
                return None
    
    def exists(self, cache_key: str) -> bool:
        """Проверка существования записи в кэше"""
        file_path = self.cache_dir / f"{cache_key}.gz"
        return file_path.exists()
    
    def is_expired(self, cache_key: str) -> bool:
        """Проверка истечения срока действия"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT expires_at FROM cache_metadata WHERE key = ?
            ''', (cache_key,))
            
            row = cursor.fetchone()
            if not row:
                return True
            
            expires_at = datetime.fromisoformat(row[0])
            return datetime.now() > expires_at
    
    def get_metadata(self, cache_key: str) -> Optional[Dict]:
        """Получение метаданных записи"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM cache_metadata WHERE key = ?
            ''', (cache_key,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    
    def update_access(self, cache_key: str):
        """Обновление статистики доступа"""
        now = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE cache_metadata 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE key = ?
            ''', (now.isoformat(), cache_key))
    
    def remove(self, cache_key: str) -> bool:
        """Удаление записи из кэша"""
        with self.lock:
            file_path = self.cache_dir / f"{cache_key}.gz"
            
            # Удаление файла
            if file_path.exists():
                file_path.unlink()
            
            # Удаление метаданных
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM cache_metadata WHERE key = ?
                ''', (cache_key,))
                
                return cursor.rowcount > 0
    
    def cleanup_expired(self) -> int:
        """Очистка устаревших записей"""
        with self.lock:
            now = datetime.now()
            
            # Получение списка устаревших записей
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT key FROM cache_metadata WHERE expires_at < ?
                ''', (now.isoformat(),))
                
                expired_keys = [row[0] for row in cursor.fetchall()]
            
            # Удаление устаревших записей
            removed_count = 0
            for key in expired_keys:
                if self.remove(key):
                    removed_count += 1
            
            return removed_count
    
    def enforce_size_limits(self):
        """Принудительное соблюдение лимитов размера"""
        current_size = self.get_cache_size_mb()
        
        if current_size <= self.max_size_mb:
            return
        
        # Удаление наименее ценных записей
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT key, quality_score, access_count, last_accessed
                FROM cache_metadata
                ORDER BY quality_score ASC, access_count ASC, last_accessed ASC
            ''')
            
            entries_to_remove = []
            for row in cursor.fetchall():
                entries_to_remove.append(row[0])
                if len(entries_to_remove) >= 10:  # Удаляем батчами
                    break
        
        # Удаление записей
        removed_count = 0
        for key in entries_to_remove:
            if self.remove(key):
                removed_count += 1
                self.evictions += 1
            
            # Проверка размера после каждого удаления
            if self.get_cache_size_mb() <= self.max_size_mb * 0.9:
                break
    
    def get_cache_size_mb(self) -> float:
        """Получение текущего размера кэша в МБ"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT SUM(file_size) FROM cache_metadata
            ''')
            
            total_bytes = cursor.fetchone()[0] or 0
            return total_bytes / (1024 * 1024)
    
    def get_cache_statistics(self) -> CacheStats:
        """Получение статистики кэша"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*), AVG(access_count), SUM(file_size)
                FROM cache_metadata
            ''')
            
            total_entries, avg_access_count, total_size_bytes = cursor.fetchone()
            total_entries = total_entries or 0
            avg_access_count = avg_access_count or 0
            total_size_bytes = total_size_bytes or 0
            
            # Расчет показателей
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            miss_rate = self.misses / total_requests if total_requests > 0 else 0
            
            # Эффективность использования пространства
            max_size_bytes = self.max_size_mb * 1024 * 1024
            space_efficiency = total_size_bytes / max_size_bytes if max_size_bytes > 0 else 0
            
            # Скорость истечения
            cursor = conn.execute('''
                SELECT COUNT(*) FROM cache_metadata WHERE expires_at < ?
            ''', (datetime.now().isoformat(),))
            expired_count = cursor.fetchone()[0] or 0
            expiration_rate = expired_count / total_entries if total_entries > 0 else 0
        
        return CacheStats(
            total_entries=total_entries,
            total_size_mb=total_size_bytes / (1024 * 1024),
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            space_efficiency=space_efficiency,
            avg_access_count=avg_access_count,
            expiration_rate=expiration_rate
        )
    
    def print_cache_report(self):
        """Вывод отчета по состоянию кэша"""
        stats = self.get_cache_statistics()
        
        print("\n" + "="*50)
        print("[💾 Cache Manager] === ОТЧЕТ ПО КЭШУ ===")
        print("="*50)
        print(f"📊 Всего записей: {stats.total_entries}")
        print(f"💾 Размер кэша: {stats.total_size_mb:.1f} МБ / {self.max_size_mb} МБ")
        print(f"🎯 Hit rate: {stats.hit_rate:.1%}")
        print(f"❌ Miss rate: {stats.miss_rate:.1%}")
        print(f"📈 Среднее использование: {stats.avg_access_count:.1f} раз")
        print(f"⏰ Истекших записей: {stats.expiration_rate:.1%}")
        print(f"🗑️ Вытеснений: {self.evictions}")
        
        # Топ серверов по количеству записей
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT mcp_server, COUNT(*), AVG(access_count)
                FROM cache_metadata
                GROUP BY mcp_server
                ORDER BY COUNT(*) DESC
                LIMIT 5
            ''')
            
            print("\n🏆 Топ серверов в кэше:")
            for row in cursor.fetchall():
                server, count, avg_access = row
                print(f"  • {server}: {count} записей (среднее использование: {avg_access:.1f})")
        
        print("="*50)
    
    def optimize_cache(self) -> Dict[str, int]:
        """Оптимизация кэша (очистка и реорганизация)"""
        with self.lock:
            operations = {
                'expired_removed': self.cleanup_expired(),
                'low_quality_removed': 0,
                'defragmented': 0
            }
            
            # Удаление записей с низким качеством и редким использованием
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT key FROM cache_metadata 
                    WHERE quality_score < 0.4 AND access_count <= 1
                    AND created_at < ?
                ''', ((datetime.now() - timedelta(hours=24)).isoformat(),))
                
                low_quality_keys = [row[0] for row in cursor.fetchall()]
            
            for key in low_quality_keys:
                if self.remove(key):
                    operations['low_quality_removed'] += 1
            
            # Принудительное соблюдение лимитов
            self.enforce_size_limits()
            
            return operations

# Глобальный экземпляр менеджера кэша
cache_manager = IntelligentCacheManager()

def cache_mcp_response(agent: str, mcp_server: str, query: str, response_data: Any,
                      tokens_used: int, response_time: float) -> Optional[str]:
    """Кэширование ответа MCP"""
    return cache_manager.store(agent, mcp_server, query, response_data, 
                              tokens_used, response_time)

def get_cached_mcp_response(agent: str, mcp_server: str, query: str) -> Optional[Tuple[Any, Dict]]:
    """Получение кэшированного ответа MCP"""
    return cache_manager.retrieve(agent, mcp_server, query)

def cleanup_cache() -> int:
    """Очистка устаревшего кэша"""
    return cache_manager.cleanup_expired()

def optimize_cache() -> Dict[str, int]:
    """Оптимизация кэша"""
    return cache_manager.optimize_cache()

def print_cache_report():
    """Вывод отчета по кэшу"""
    cache_manager.print_cache_report()

if __name__ == "__main__":
    # Демонстрация работы кэша
    print("💾 Intelligent Cache Manager инициализирован")
    
    # Примеры тестирования
    cache = IntelligentCacheManager()
    
    # Тест кэширования
    test_response = {"result": "test data", "tokens": 300}
    cache_key = cache.store("architect", "context7", "test query", 
                           test_response, 300, 2.5)
    
    if cache_key:
        print(f"✅ Ответ кэширован: {cache_key}")
        
        # Тест получения из кэша
        cached_data = cache.retrieve("architect", "context7", "test query")
        if cached_data:
            print("✅ Ответ успешно получен из кэша")
        else:
            print("❌ Ошибка получения из кэша")
    
    cache.print_cache_report()