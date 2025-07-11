# Claude MultiAgent Framework - Примеры проектов

## Обзор

Эта директория содержит готовые примеры проектов, демонстрирующие возможности Claude MultiAgent Framework для различных типов приложений.

## Доступные примеры

### 🤖 [Telegram Bot](telegram_bot/)

**Тип проекта**: `telegram_bot`  
**Масштаб**: `standard`  
**Особенности**:
- Полная интеграция с Telegram Bot API
- AI-команды с использованием MCP серверов
- Автоматический мониторинг всех обработчиков
- Middleware для отслеживания производительности
- Система алертов при ошибках

**Основные возможности**:
- `/ask` - AI-поиск информации
- `/stats` - Статистика производительности
- `/optimize` - Ручная оптимизация
- Автоматическое кэширование ответов
- Real-time мониторинг запросов

**Быстрый старт**:
```bash
python claude_framework_cli.py create --name MyBot --type telegram_bot --scale standard
cd MyBot && source venv/bin/activate
python framework_init.py && python bot/main.py
```

---

### 🚀 [Web API](web_api/)

**Тип проекта**: `web_api`  
**Масштаб**: `advanced`  
**Особенности**:
- FastAPI с автоматической документацией
- AI-powered endpoints
- Comprehensive middleware stack
- Pydantic схемы для валидации
- Production-ready конфигурация

**Основные возможности**:
- `/ai/search` - AI поиск информации
- `/ai/code-search` - Поиск примеров кода
- `/metrics/performance` - Метрики производительности  
- `/metrics/cache` - Статистика кэша
- Swagger UI и ReDoc документация

**Быстрый старт**:
```bash
python claude_framework_cli.py create --name MyAPI --type web_api --scale advanced
cd MyAPI && source venv/bin/activate
python framework_init.py && uvicorn api.main:app --reload
```

---

### 🖥️ [CLI Tool](cli_tool/)

**Тип проекта**: `cli_tool`  
**Масштаб**: `minimal`  
**Особенности**:
- Rich CLI интерфейс с красивым выводом
- Click framework для команд
- AI интеграции через MCP
- Автоматическое кэширование результатов
- Простая установка и использование

**Основные возможности**:
- `search web` - Поиск в интернете
- `search research` - Поиск научных статей
- `code search` - Поиск примеров кода
- `code repo` - Анализ репозиториев
- `stats` - Статистика использования

**Быстрый старт**:
```bash
python claude_framework_cli.py create --name MyCLI --type cli_tool --scale minimal
cd MyCLI && source venv/bin/activate && pip install -e .
mycli init && mycli search web "python examples"
```

---

### 🧠 [ML Service](ml_service/)

**Тип проекта**: `ml_service`  
**Масштаб**: `advanced`  
**Особенности**:
- MLflow интеграция для experiment tracking
- Автоматическое логирование экспериментов
- Model registry и версионирование
- AI-ассистированная оптимизация
- Comprehensive ML метрики

**Основные возможности**:
- `/train` - Обучение моделей
- `/predict` - Предсказания
- `/optimize` - Оптимизация гиперпараметров
- `/ai-assistance/suggest-model` - AI советы
- MLflow UI для экспериментов

**Быстрый старт**:
```bash
python claude_framework_cli.py create --name MyML --type ml_service --scale advanced
cd MyML && source venv/bin/activate
python framework_init.py && uvicorn ml_service.main:app --reload
```

## Сравнение примеров

| Характеристика | Telegram Bot | Web API | CLI Tool | ML Service |
|----------------|--------------|---------|----------|------------|
| **Сложность** | Средняя | Высокая | Низкая | Высокая |
| **Масштаб** | Standard | Advanced | Minimal | Advanced |
| **MCP интеграции** | ✅ Exa, GitHub | ✅ Exa, GitHub, Context7 | ✅ Exa, GitHub | ✅ Все MCP серверы |
| **Мониторинг** | ✅ Полный | ✅ Полный | ✅ Базовый | ✅ ML-специфичный |
| **Кэширование** | ✅ | ✅ | ✅ | ✅ ML моделей |
| **Алерты** | ✅ | ✅ | ❌ | ✅ ML метрики |
| **Автооптимизация** | ❌ | ❌ | ❌ | ✅ Гиперпараметры |
| **Развертывание** | Docker | Docker/K8s | Binary | Docker/K8s/MLOps |

## Общие особенности всех примеров

### 🚀 Автоматическая инициализация

Все примеры включают:
- Автоматическую настройку виртуального окружения
- Конфигурацию Claude MultiAgent Framework
- Установку всех необходимых зависимостей
- Базовую настройку мониторинга

### 📊 Мониторинг и отчеты

- **Real-time мониторинг** всех MCP вызовов
- **Автоматические отчеты** в HTML формате
- **Метрики производительности** (время ответа, использование токенов)
- **Кэш статистика** (hit rate, размер кэша)

### 🔧 Конфигурация

- **JSON конфигурация** с валидацией
- **Переменные окружения** для секретных данных
- **Гибкие настройки** компонентов фреймворка
- **Профили масштабирования** (minimal, standard, advanced, enterprise)

### 🛡️ Безопасность

- **Валидация конфигураций** перед запуском
- **Безопасное хранение** API ключей
- **Аудит операций** в логах
- **Контролируемые изменения** с подтверждением

## Создание нового проекта

### 1. Через CLI (рекомендуется)

```bash
# Интерактивное создание
python claude_framework_cli.py create

# Или с параметрами
python claude_framework_cli.py create \
  --name "MyProject" \
  --type telegram_bot \
  --scale standard \
  --dir ./MyProject
```

### 2. Через Python installer

```bash
# Интерактивная установка
python install.py

# Или silent режим
python install.py --name MyProject --type web_api --scale advanced
```

### 3. Через shell скрипты

```bash
# Linux/macOS
./install.sh --name MyProject --type cli_tool --scale minimal

# Windows
install.bat --name MyProject --type ml_service --scale advanced
```

## Настройка окружения

### Общие переменные

Создайте `.env` файл в корне проекта:

```bash
# Claude MultiAgent Framework
ANTHROPIC_API_KEY=your_anthropic_key
GITHUB_TOKEN=your_github_token
PERPLEXITY_API_KEY=your_perplexity_key
EXA_API_KEY=your_exa_key

# Email уведомления (опционально)
EMAIL_PASSWORD=your_email_password

# Проект-специфичные переменные
# (см. README конкретного примера)
```

### API ключи

Получите API ключи от следующих сервисов:

1. **Anthropic** (обязательно) - https://console.anthropic.com/
2. **GitHub** (рекомендуется) - https://github.com/settings/tokens
3. **Perplexity** (для research) - https://www.perplexity.ai/settings/api
4. **Exa** (для web поиска) - https://dashboard.exa.ai/

## Развертывание

### Development

```bash
# Все примеры поддерживают hot reload
uvicorn app.main:app --reload  # Web API, ML Service
python bot/main.py            # Telegram Bot
mycli --help                  # CLI Tool
```

### Production

```bash
# Docker (все примеры включают Dockerfile)
docker build -t my-project .
docker run -p 8000:8000 my-project

# Или через docker-compose
docker-compose up -d
```

### Kubernetes

```yaml
# Примеры включают K8s манифесты
kubectl apply -f k8s/
```

## Мониторинг и отладка

### Просмотр логов

```bash
# Framework логи
tail -f logs/framework.log

# Specific agent логи
tail -f logs/framework.log | grep telegram_bot
```

### Метрики

```bash
# Быстрая статистика
python -c "
from monitoring.performance_tracker import get_statistics
print(get_statistics(hours=24))
"

# Веб интерфейс (для API проектов)
curl http://localhost:8000/metrics/performance | jq
```

### Отчеты

```bash
# Генерация HTML отчета
python -m reports.auto_reporter

# Открытие отчета
open reports/performance_report.html
```

## Кастомизация

### Добавление новых компонентов

```python
# Создайте новый компонент
class CustomComponent:
    def __init__(self):
        pass
    
    @track_mcp_call("custom", "component")
    async def process(self, data):
        # Ваша логика
        pass

# Зарегистрируйте в framework_init.py
from custom_component import CustomComponent
```

### Интеграция новых MCP серверов

```json
// Добавьте в config/framework_config.json
{
  "mcp_servers": {
    "custom_server": {
      "enabled": true,
      "config": {...}
    }
  }
}
```

### Кастомные алерты

```python
# В config/alert_config.json
{
  "custom_alerts": {
    "my_metric": {
      "threshold": 100,
      "handler": "custom_handler"
    }
  }
}
```

## Тестирование

### Unit тесты

```bash
# Все примеры включают pytest тесты
pytest tests/ -v
```

### Integration тесты

```bash
# Тесты с реальными MCP серверами
pytest tests/integration/ -v --api-keys
```

### Load тесты

```bash
# Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Locust (если доступен)
locust -f tests/load_test.py
```

## Troubleshooting

### Частые проблемы

1. **Фреймворк не инициализируется**
   ```bash
   python claude_framework_cli.py validate
   ```

2. **API ключи не работают**
   ```bash
   echo $ANTHROPIC_API_KEY
   # Проверьте .env файл
   ```

3. **Медленные MCP вызовы**
   ```bash
   # Включите кэширование
   # Проверьте интернет соединение
   # Посмотрите отчеты производительности
   ```

4. **Ошибки зависимостей**
   ```bash
   pip install -r requirements.txt
   # Или пересоздайте venv
   ```

### Получение помощи

- 📖 **Документация**: docs/
- ❓ **FAQ**: docs/FAQ.md
- 🏗️ **Архитектура**: docs/architecture.md
- 📊 **Руководство пользователя**: docs/user_guide.md
- 🛠️ **Руководство разработчика**: docs/developer_guide.md

## Roadmap

### Планируемые примеры

- **Desktop App** - Приложение с GUI (Tkinter/PyQt)
- **IoT Device** - Интеграция с IoT устройствами
- **Data Pipeline** - ETL процессы с мониторингом
- **Microservice** - Микросервисная архитектура

### Улучшения

- **Более глубокая интеграция** с популярными фреймворками
- **Advanced MLOps** возможности
- **Distributed monitoring** для кластерных развертываний
- **Custom MCP servers** примеры

---

*Примеры созданы с Claude MultiAgent Framework v1.0.0*  
*Дата: 2025-07-11*  
*Автор: Claude MultiAgent System*