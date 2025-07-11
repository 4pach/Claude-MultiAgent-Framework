#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizer AI - ИИ-система рекомендаций для оптимизации MCP производительности
Часть Claude MultiAgent Framework

Автор: Claude MultiAgent System
Дата: 2025-07-11
"""

import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
import pickle

@dataclass
class OptimizationRecommendation:
    """Рекомендация по оптимизации"""
    id: str
    category: str
    priority: int  # 1-5, где 5 = критично
    title: str
    description: str
    impact_estimate: str
    implementation_complexity: str
    estimated_savings: Dict[str, float]  # tokens, time, etc.
    agent: Optional[str]
    mcp_server: Optional[str]
    confidence_score: float
    generated_at: datetime

@dataclass
class PerformancePattern:
    """Паттерн производительности"""
    pattern_type: str
    frequency: float
    impact_score: float
    description: str
    affected_components: List[str]
    recommendations: List[str]

class OptimizerAI:
    """ИИ-система для анализа и оптимизации производительности"""
    
    def __init__(self, models_dir: str = "recommendations/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Пути к базам данных
        self.performance_db = Path("monitoring/performance.db")
        self.cache_db = Path("monitoring/cache/cache_metadata.db")
        
        # Модели машинного обучения
        self.anomaly_detector = None
        self.pattern_clusterer = None
        
        # Пороги для анализа
        self.thresholds = {
            'slow_response': 5.0,
            'high_tokens': 800,
            'low_success_rate': 0.9,
            'poor_cache_rate': 0.3,
            'anomaly_threshold': -0.5
        }
        
        # Инициализация моделей
        self.load_or_train_models()
    
    def load_or_train_models(self):
        """Загрузка или обучение моделей ML"""
        anomaly_model_path = self.models_dir / "anomaly_detector.pkl"
        cluster_model_path = self.models_dir / "pattern_clusterer.pkl"
        
        try:
            # Попытка загрузки существующих моделей
            if anomaly_model_path.exists():
                with open(anomaly_model_path, 'rb') as f:
                    self.anomaly_detector = pickle.load(f)
            
            if cluster_model_path.exists():
                with open(cluster_model_path, 'rb') as f:
                    self.pattern_clusterer = pickle.load(f)
            
            # Если модели не загружены, обучаем новые
            if self.anomaly_detector is None or self.pattern_clusterer is None:
                self.train_models()
                
        except Exception as e:
            print(f"⚠️ Ошибка загрузки моделей: {e}")
            self.train_models()
    
    def train_models(self):
        """Обучение моделей машинного обучения"""
        print("🧠 Обучение ИИ-моделей оптимизации...")
        
        # Получение данных для обучения
        training_data = self.get_training_data()
        
        if len(training_data) < 10:
            print("⚠️ Недостаточно данных для обучения моделей")
            # Создание базовых моделей
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.pattern_clusterer = KMeans(n_clusters=5, random_state=42)
            return
        
        # Подготовка данных
        features = np.array(training_data)
        
        # Обучение детектора аномалий
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.anomaly_detector.fit(features)
        
        # Обучение кластеризатора паттернов
        n_clusters = min(5, max(2, len(training_data) // 5))
        self.pattern_clusterer = KMeans(n_clusters=n_clusters, random_state=42)
        self.pattern_clusterer.fit(features)
        
        # Сохранение моделей
        self.save_models()
        print("✅ Модели обучены и сохранены")
    
    def save_models(self):
        """Сохранение обученных моделей"""
        try:
            with open(self.models_dir / "anomaly_detector.pkl", 'wb') as f:
                pickle.dump(self.anomaly_detector, f)
            
            with open(self.models_dir / "pattern_clusterer.pkl", 'wb') as f:
                pickle.dump(self.pattern_clusterer, f)
                
        except Exception as e:
            print(f"❌ Ошибка сохранения моделей: {e}")
    
    def get_training_data(self) -> List[List[float]]:
        """Получение данных для обучения моделей"""
        if not self.performance_db.exists():
            return []
        
        try:
            with sqlite3.connect(self.performance_db) as conn:
                cursor = conn.execute('''
                    SELECT response_time, tokens_used, success, 
                           strftime('%H', timestamp) as hour,
                           length(query_hash) as query_complexity
                    FROM performance_records
                    WHERE timestamp > datetime('now', '-30 days')
                    ORDER BY timestamp DESC
                    LIMIT 1000
                ''')
                
                data = []
                for row in cursor.fetchall():
                    response_time, tokens, success, hour, complexity = row
                    
                    # Нормализация признаков
                    features = [
                        min(response_time / 20.0, 1.0),  # Нормализация времени ответа
                        min(tokens / 1500.0, 1.0),       # Нормализация токенов
                        float(success),                   # Успешность (0 или 1)
                        int(hour) / 24.0,                # Час дня (0-1)
                        min(complexity / 50.0, 1.0)      # Сложность запроса
                    ]
                    data.append(features)
                
                return data
                
        except Exception as e:
            print(f"❌ Ошибка получения данных для обучения: {e}")
            return []
    
    def detect_anomalies(self, recent_hours: int = 24) -> List[Dict]:
        """Обнаружение аномалий в производительности"""
        if self.anomaly_detector is None:
            return []
        
        # Получение недавних данных
        cutoff_time = datetime.now() - timedelta(hours=recent_hours)
        recent_data = self.get_recent_performance_data(cutoff_time)
        
        if len(recent_data) < 5:
            return []
        
        anomalies = []
        
        for record in recent_data:
            features = np.array([record['features']]).reshape(1, -1)
            anomaly_score = self.anomaly_detector.decision_function(features)[0]
            
            if anomaly_score < self.thresholds['anomaly_threshold']:
                anomalies.append({
                    'timestamp': record['timestamp'],
                    'agent': record['agent'],
                    'mcp_server': record['mcp_server'],
                    'anomaly_score': anomaly_score,
                    'features': record['original_features'],
                    'description': self.describe_anomaly(record['original_features'])
                })
        
        return sorted(anomalies, key=lambda x: x['anomaly_score'])
    
    def get_recent_performance_data(self, cutoff_time: datetime) -> List[Dict]:
        """Получение недавних данных производительности"""
        if not self.performance_db.exists():
            return []
        
        try:
            with sqlite3.connect(self.performance_db) as conn:
                cursor = conn.execute('''
                    SELECT timestamp, agent, mcp_server, response_time, 
                           tokens_used, success, query_hash
                    FROM performance_records
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                ''', (cutoff_time.isoformat(),))
                
                data = []
                for row in cursor.fetchall():
                    timestamp, agent, server, response_time, tokens, success, query_hash = row
                    
                    original_features = {
                        'response_time': response_time,
                        'tokens_used': tokens,
                        'success': success,
                        'query_complexity': len(query_hash)
                    }
                    
                    # Нормализованные признаки для модели
                    hour = datetime.fromisoformat(timestamp).hour
                    features = [
                        min(response_time / 20.0, 1.0),
                        min(tokens / 1500.0, 1.0),
                        float(success),
                        hour / 24.0,
                        min(len(query_hash) / 50.0, 1.0)
                    ]
                    
                    data.append({
                        'timestamp': timestamp,
                        'agent': agent,
                        'mcp_server': server,
                        'original_features': original_features,
                        'features': features
                    })
                
                return data
                
        except Exception as e:
            print(f"❌ Ошибка получения недавних данных: {e}")
            return []
    
    def describe_anomaly(self, features: Dict) -> str:
        """Описание обнаруженной аномалии"""
        descriptions = []
        
        if features['response_time'] > 15.0:
            descriptions.append(f"Критически медленный ответ ({features['response_time']:.1f}сек)")
        elif features['response_time'] > 10.0:
            descriptions.append(f"Медленный ответ ({features['response_time']:.1f}сек)")
        
        if features['tokens_used'] > 1200:
            descriptions.append(f"Чрезмерное потребление токенов ({features['tokens_used']})")
        
        if not features['success']:
            descriptions.append("Неуспешный запрос")
        
        if not descriptions:
            descriptions.append("Необычная комбинация параметров")
        
        return "; ".join(descriptions)
    
    def identify_patterns(self) -> List[PerformancePattern]:
        """Идентификация паттернов производительности"""
        if self.pattern_clusterer is None:
            return []
        
        # Получение данных за последние 7 дней
        cutoff_time = datetime.now() - timedelta(days=7)
        recent_data = self.get_recent_performance_data(cutoff_time)
        
        if len(recent_data) < 10:
            return []
        
        # Кластеризация данных
        features_matrix = np.array([record['features'] for record in recent_data])
        cluster_labels = self.pattern_clusterer.predict(features_matrix)
        
        # Анализ кластеров
        patterns = []
        for cluster_id in np.unique(cluster_labels):
            cluster_data = [record for i, record in enumerate(recent_data) 
                          if cluster_labels[i] == cluster_id]
            
            if len(cluster_data) < 3:  # Слишком мало данных для паттерна
                continue
            
            pattern = self.analyze_cluster(cluster_id, cluster_data)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def analyze_cluster(self, cluster_id: int, cluster_data: List[Dict]) -> Optional[PerformancePattern]:
        """Анализ кластера для выявления паттерна"""
        if len(cluster_data) < 3:
            return None
        
        # Анализ характеристик кластера
        response_times = [d['original_features']['response_time'] for d in cluster_data]
        tokens = [d['original_features']['tokens_used'] for d in cluster_data]
        success_rates = [d['original_features']['success'] for d in cluster_data]
        
        avg_response_time = statistics.mean(response_times)
        avg_tokens = statistics.mean(tokens)
        success_rate = statistics.mean(success_rates)
        
        # Определение типа паттерна
        pattern_type = self.classify_pattern(avg_response_time, avg_tokens, success_rate)
        
        # Анализ затронутых компонентов
        agents = set(d['agent'] for d in cluster_data)
        servers = set(d['mcp_server'] for d in cluster_data)
        
        # Частота встречаемости
        frequency = len(cluster_data) / len(cluster_data)  # Упрощенный расчет
        
        # Оценка влияния
        impact_score = self.calculate_impact_score(avg_response_time, avg_tokens, success_rate)
        
        # Генерация рекомендаций для паттерна
        recommendations = self.generate_pattern_recommendations(
            pattern_type, agents, servers, avg_response_time, avg_tokens, success_rate
        )
        
        return PerformancePattern(
            pattern_type=pattern_type,
            frequency=frequency,
            impact_score=impact_score,
            description=self.describe_pattern(pattern_type, avg_response_time, avg_tokens, success_rate),
            affected_components=list(agents | servers),
            recommendations=recommendations
        )
    
    def classify_pattern(self, response_time: float, tokens: float, success_rate: float) -> str:
        """Классификация типа паттерна"""
        if success_rate < 0.8:
            return "high_failure_rate"
        elif response_time > 10.0:
            return "slow_responses"
        elif tokens > 1000:
            return "high_token_consumption"
        elif response_time < 2.0 and tokens < 200:
            return "efficient_operations"
        elif response_time > 5.0 and tokens > 600:
            return "resource_intensive"
        else:
            return "normal_operations"
    
    def calculate_impact_score(self, response_time: float, tokens: float, success_rate: float) -> float:
        """Расчет оценки влияния паттерна"""
        # Нормализация метрик (0-1, где 1 = плохо)
        time_impact = min(response_time / 20.0, 1.0)
        token_impact = min(tokens / 1500.0, 1.0)
        success_impact = 1.0 - success_rate
        
        # Взвешенная сумма
        return (time_impact * 0.4 + token_impact * 0.3 + success_impact * 0.3) * 100
    
    def describe_pattern(self, pattern_type: str, response_time: float, 
                        tokens: float, success_rate: float) -> str:
        """Описание паттерна"""
        descriptions = {
            "high_failure_rate": f"Высокий процент неудач (успешность: {success_rate:.1%})",
            "slow_responses": f"Медленные ответы (среднее время: {response_time:.1f}сек)",
            "high_token_consumption": f"Высокое потребление токенов (среднее: {tokens:.0f})",
            "efficient_operations": f"Эффективные операции (время: {response_time:.1f}сек, токены: {tokens:.0f})",
            "resource_intensive": f"Ресурсоемкие операции (время: {response_time:.1f}сек, токены: {tokens:.0f})",
            "normal_operations": f"Обычные операции (время: {response_time:.1f}сек, токены: {tokens:.0f})"
        }
        
        return descriptions.get(pattern_type, f"Неизвестный паттерн: {pattern_type}")
    
    def generate_pattern_recommendations(self, pattern_type: str, agents: set, servers: set,
                                       response_time: float, tokens: float, 
                                       success_rate: float) -> List[str]:
        """Генерация рекомендаций для паттерна"""
        recommendations = []
        
        if pattern_type == "high_failure_rate":
            recommendations.extend([
                f"Проверить стабильность серверов: {', '.join(servers)}",
                "Добавить retry механизм для неудачных запросов",
                "Проанализировать логи ошибок для выявления причин"
            ])
        
        elif pattern_type == "slow_responses":
            recommendations.extend([
                f"Оптимизировать запросы для серверов: {', '.join(servers)}",
                "Рассмотреть параллельное выполнение запросов",
                "Увеличить таймауты или разбить большие запросы"
            ])
        
        elif pattern_type == "high_token_consumption":
            recommendations.extend([
                f"Сузить запросы для агентов: {', '.join(agents)}",
                "Улучшить фильтрацию результатов",
                "Увеличить использование кэша для похожих запросов"
            ])
        
        elif pattern_type == "resource_intensive":
            recommendations.extend([
                "Оптимизировать стратегию кэширования",
                "Рассмотреть батчевую обработку запросов",
                f"Настроить лимиты для агентов: {', '.join(agents)}"
            ])
        
        elif pattern_type == "efficient_operations":
            recommendations.extend([
                "Изучить и распространить успешные практики",
                "Использовать данную конфигурацию как эталон",
                "Применить похожие настройки к другим компонентам"
            ])
        
        return recommendations
    
    def generate_comprehensive_recommendations(self) -> List[OptimizationRecommendation]:
        """Генерация комплексных рекомендаций"""
        recommendations = []
        
        # Обнаружение аномалий
        anomalies = self.detect_anomalies(24)
        
        # Анализ паттернов
        patterns = self.identify_patterns()
        
        # Статистический анализ
        stats_recommendations = self.generate_statistical_recommendations()
        
        # Объединение всех рекомендаций
        rec_id = 1
        
        # Рекомендации на основе аномалий
        for anomaly in anomalies[:5]:  # Топ-5 аномалий
            recommendations.append(OptimizationRecommendation(
                id=f"ANOM_{rec_id:03d}",
                category="anomaly",
                priority=4,
                title=f"Устранение аномалии в {anomaly['mcp_server']}",
                description=f"Обнаружена аномалия: {anomaly['description']}",
                impact_estimate="Высокий",
                implementation_complexity="Средняя",
                estimated_savings={"response_time": 2.0, "tokens": 100},
                agent=anomaly['agent'],
                mcp_server=anomaly['mcp_server'],
                confidence_score=abs(anomaly['anomaly_score']),
                generated_at=datetime.now()
            ))
            rec_id += 1
        
        # Рекомендации на основе паттернов
        for pattern in patterns:
            if pattern.impact_score > 50:  # Только значимые паттерны
                priority = 5 if pattern.impact_score > 80 else 3
                
                recommendations.append(OptimizationRecommendation(
                    id=f"PATT_{rec_id:03d}",
                    category="pattern",
                    priority=priority,
                    title=f"Оптимизация паттерна: {pattern.pattern_type}",
                    description=pattern.description,
                    impact_estimate="Высокий" if pattern.impact_score > 70 else "Средний",
                    implementation_complexity="Средняя",
                    estimated_savings=self.estimate_pattern_savings(pattern),
                    agent=None,
                    mcp_server=None,
                    confidence_score=pattern.frequency,
                    generated_at=datetime.now()
                ))
                rec_id += 1
        
        # Статистические рекомендации
        for stat_rec in stats_recommendations:
            recommendations.append(OptimizationRecommendation(
                id=f"STAT_{rec_id:03d}",
                category="statistics",
                priority=stat_rec['priority'],
                title=stat_rec['title'],
                description=stat_rec['description'],
                impact_estimate=stat_rec['impact'],
                implementation_complexity=stat_rec['complexity'],
                estimated_savings=stat_rec['savings'],
                agent=stat_rec.get('agent'),
                mcp_server=stat_rec.get('mcp_server'),
                confidence_score=stat_rec['confidence'],
                generated_at=datetime.now()
            ))
            rec_id += 1
        
        # Сортировка по приоритету и confidence score
        recommendations.sort(key=lambda x: (x.priority, x.confidence_score), reverse=True)
        
        return recommendations[:15]  # Топ-15 рекомендаций
    
    def estimate_pattern_savings(self, pattern: PerformancePattern) -> Dict[str, float]:
        """Оценка экономии от устранения паттерна"""
        savings = {"response_time": 0.0, "tokens": 0, "error_reduction": 0.0}
        
        if pattern.pattern_type == "slow_responses":
            savings["response_time"] = pattern.impact_score * 0.1
        elif pattern.pattern_type == "high_token_consumption":
            savings["tokens"] = pattern.impact_score * 5
        elif pattern.pattern_type == "high_failure_rate":
            savings["error_reduction"] = pattern.impact_score * 0.01
        
        return savings
    
    def generate_statistical_recommendations(self) -> List[Dict]:
        """Генерация рекомендаций на основе статистического анализа"""
        recommendations = []
        
        # Анализ данных за последние 7 дней
        cutoff_time = datetime.now() - timedelta(days=7)
        
        try:
            with sqlite3.connect(self.performance_db) as conn:
                # Анализ по серверам
                cursor = conn.execute('''
                    SELECT mcp_server, AVG(response_time), AVG(tokens_used), 
                           AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END), COUNT(*)
                    FROM performance_records
                    WHERE timestamp > ?
                    GROUP BY mcp_server
                    HAVING COUNT(*) >= 5
                    ORDER BY AVG(response_time) DESC
                ''', (cutoff_time.isoformat(),))
                
                for row in cursor.fetchall():
                    server, avg_time, avg_tokens, success_rate, count = row
                    
                    if avg_time > self.thresholds['slow_response']:
                        recommendations.append({
                            'priority': 4,
                            'title': f"Оптимизация сервера {server}",
                            'description': f"Сервер показывает медленные ответы: {avg_time:.1f}сек в среднем",
                            'impact': "Высокий",
                            'complexity': "Средняя",
                            'savings': {"response_time": avg_time - 3.0, "tokens": 0},
                            'mcp_server': server,
                            'confidence': min(count / 50.0, 1.0)
                        })
                    
                    if success_rate < self.thresholds['low_success_rate']:
                        recommendations.append({
                            'priority': 5,
                            'title': f"Повышение надежности {server}",
                            'description': f"Низкая успешность: {success_rate:.1%}",
                            'impact': "Критический",
                            'complexity': "Высокая",
                            'savings': {"error_reduction": 0.9 - success_rate, "tokens": 0},
                            'mcp_server': server,
                            'confidence': min(count / 30.0, 1.0)
                        })
                
                # Анализ по агентам
                cursor = conn.execute('''
                    SELECT agent, AVG(response_time), AVG(tokens_used), COUNT(*)
                    FROM performance_records
                    WHERE timestamp > ?
                    GROUP BY agent
                    HAVING COUNT(*) >= 5
                    ORDER BY AVG(tokens_used) DESC
                ''', (cutoff_time.isoformat(),))
                
                for row in cursor.fetchall():
                    agent, avg_time, avg_tokens, count = row
                    
                    if avg_tokens > self.thresholds['high_tokens']:
                        recommendations.append({
                            'priority': 3,
                            'title': f"Оптимизация токенов для агента {agent}",
                            'description': f"Высокое потребление токенов: {avg_tokens:.0f} в среднем",
                            'impact': "Средний",
                            'complexity': "Низкая",
                            'savings': {"tokens": avg_tokens - 500, "response_time": 0},
                            'agent': agent,
                            'confidence': min(count / 40.0, 1.0)
                        })
        
        except Exception as e:
            print(f"❌ Ошибка статистического анализа: {e}")
        
        return recommendations
    
    def save_recommendations(self, recommendations: List[OptimizationRecommendation]) -> str:
        """Сохранение рекомендаций в файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_recommendations_{timestamp}.json"
        filepath = Path("recommendations") / filename
        
        # Создание директории
        filepath.parent.mkdir(exist_ok=True)
        
        # Сериализация рекомендаций
        recommendations_data = {
            'generated_at': datetime.now().isoformat(),
            'total_recommendations': len(recommendations),
            'recommendations': [asdict(rec) for rec in recommendations]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recommendations_data, f, ensure_ascii=False, indent=2, default=str)
        
        return str(filepath)
    
    def print_recommendations_summary(self, recommendations: List[OptimizationRecommendation]):
        """Вывод сводки рекомендаций"""
        if not recommendations:
            print("💡 Рекомендации оптимизатора: Все работает эффективно!")
            return
        
        print("\n💡 === ИИ РЕКОМЕНДАЦИИ ОПТИМИЗАЦИИ ===")
        
        # Группировка по приоритету
        priority_groups = {}
        for rec in recommendations:
            priority_groups.setdefault(rec.priority, []).append(rec)
        
        priority_names = {5: "🔴 Критично", 4: "🧡 Высокий", 3: "🟡 Средний", 2: "🟢 Низкий", 1: "🔵 Информационный"}
        
        for priority in sorted(priority_groups.keys(), reverse=True):
            group_recs = priority_groups[priority]
            print(f"\n{priority_names.get(priority, f'Приоритет {priority}')} ({len(group_recs)} рекомендаций):")
            
            for rec in group_recs[:3]:  # Топ-3 в каждой группе
                print(f"  • {rec.title}")
                print(f"    {rec.description}")
                print(f"    Влияние: {rec.impact_estimate}, Сложность: {rec.implementation_complexity}")
                
                if rec.estimated_savings:
                    savings_str = ", ".join([
                        f"{k}: {v:.1f}" for k, v in rec.estimated_savings.items() if v > 0
                    ])
                    if savings_str:
                        print(f"    Экономия: {savings_str}")
                print()
        
        # Общая статистика
        total_time_savings = sum(rec.estimated_savings.get('response_time', 0) for rec in recommendations)
        total_token_savings = sum(rec.estimated_savings.get('tokens', 0) for rec in recommendations)
        
        print(f"📊 Потенциальная экономия:")
        print(f"  ⏱️ Время ответа: {total_time_savings:.1f}сек")
        print(f"  🔢 Токены: {total_token_savings:.0f}")
        print("="*50)

# Глобальный экземпляр ИИ-оптимизатора
optimizer_ai = OptimizerAI()

def generate_ai_recommendations() -> List[OptimizationRecommendation]:
    """Генерация ИИ-рекомендаций"""
    return optimizer_ai.generate_comprehensive_recommendations()

def detect_performance_anomalies(hours: int = 24) -> List[Dict]:
    """Обнаружение аномалий производительности"""
    return optimizer_ai.detect_anomalies(hours)

def identify_performance_patterns() -> List[PerformancePattern]:
    """Идентификация паттернов производительности"""
    return optimizer_ai.identify_patterns()

def save_ai_recommendations(recommendations: List[OptimizationRecommendation]) -> str:
    """Сохранение ИИ-рекомендаций"""
    return optimizer_ai.save_recommendations(recommendations)

def print_ai_recommendations_summary(recommendations: List[OptimizationRecommendation]):
    """Вывод сводки ИИ-рекомендаций"""
    optimizer_ai.print_recommendations_summary(recommendations)

if __name__ == "__main__":
    # Демонстрация ИИ-оптимизатора
    print("🧠 AI Optimizer инициализирован")
    
    # Генерация рекомендаций
    recommendations = generate_ai_recommendations()
    
    if recommendations:
        print_ai_recommendations_summary(recommendations)
        
        # Сохранение рекомендаций
        saved_file = save_ai_recommendations(recommendations)
        print(f"💾 Рекомендации сохранены: {saved_file}")
    else:
        print("💡 Недостаточно данных для генерации рекомендаций")