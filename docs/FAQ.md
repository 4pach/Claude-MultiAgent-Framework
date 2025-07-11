# Claude MultiAgent Framework - FAQ

## Общие вопросы

### Что такое Claude MultiAgent Framework?

Claude MultiAgent Framework - это универсальная система автономного мониторинга и оптимизации проектов с использованием искусственного интеллекта. Фреймворк построен на принципах многоагентной архитектуры, где каждый компонент выполняет специализированную роль.

### Для каких проектов подходит фреймворк?

Фреймворк поддерживает 8 типов проектов:
- **Telegram Bot** - Боты для Telegram
- **Web API** - RESTful API на FastAPI
- **CLI Tool** - Консольные утилиты
- **Data Pipeline** - Обработка данных
- **Microservice** - Микросервисы
- **ML Service** - Машинное обучение
- **Desktop App** - Десктопные приложения
- **IoT Device** - IoT устройства

### Какие масштабы проектов поддерживаются?

- **Minimal** - Базовый мониторинг для простых проектов
- **Standard** - Мониторинг + алерты для средних проектов
- **Advanced** - Добавляется ИИ оптимизация для сложных систем
- **Enterprise** - Полный функционал для корпоративных решений

## Установка и настройка

### Как установить фреймворк?

#### Быстрая установка:
```bash
# Скачайте installer
curl -L https://raw.githubusercontent.com/claude-multiagent-framework/releases/install.sh | bash

# Или используйте Python installer
python install.py --name MyProject --type telegram_bot --scale standard
```

#### Интерактивная установка:
```bash
python install.py
# Следуйте инструкциям мастера установки
```

### Какие системные требования?

- **Python**: 3.8 или выше
- **Память**: Минимум 100MB свободного места
- **ОС**: Linux, macOS, Windows
- **Дополнительно**: git (опционально)

### Как настроить конфигурацию?

Конфигурация находится в файле `config/framework_config.json`:

```json
{
  "project": {
    "name": "MyProject",
    "type": "telegram_bot",
    "scale": "standard",
    "version": "1.0.0"
  },
  "framework": {
    "components": {
      "mcp_monitor": true,
      "performance_tracker": true,
      "alert_system": true,
      "cache_manager": false
    }
  }
}
```

## Использование

### Как запустить мониторинг?

```bash
# Инициализация фреймворка
python framework_init.py

# Запуск мониторинга вручную
python -m monitoring.mcp_monitor

# Автоматический запуск при старте проекта (добавьте в ваш main.py)
from monitoring.mcp_monitor import start_monitoring
start_monitoring()
```

### Как использовать декораторы мониторинга?

```python
from monitoring.mcp_monitor import track_mcp_call

@track_mcp_call("engineer", "github")
def search_repositories(query: str):
    # Ваш код
    return results

# Вызов автоматически будет отслеживаться
repos = search_repositories("python telegram bot")
```

### Как посмотреть отчеты о производительности?

```bash
# Генерация отчета
python -m reports.auto_reporter

# Отчет будет сохранен в reports/performance_report.html
# Откройте его в браузере
```

### Как настроить алерты?

Добавьте в конфигурацию:

```json
{
  "alerts": {
    "email_notifications": true,
    "max_alerts_per_hour": 10,
    "thresholds": {
      "max_response_time": 5.0,
      "min_success_rate": 0.9
    },
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "recipients": ["admin@company.com"]
    }
  }
}
```

**Важно**: Не указывайте пароль в конфигурации! Используйте переменную окружения:
```bash
export EMAIL_PASSWORD="your_password"
```

## Автономная оптимизация

### Что такое автономная оптимизация?

Система автоматически анализирует производительность вашего проекта и предлагает улучшения. Все изменения требуют вашего подтверждения.

### Как включить автономную оптимизацию?

```json
{
  "framework": {
    "components": {
      "self_optimizer": true,
      "approval_system": true,
      "config_updater": true
    }
  }
}
```

### Как работает система подтверждений?

Когда система находит возможность оптимизации, она выводит запрос:

```
🤖 [Self-Optimizer] Предложение оптимизации:
📋 Название: Увеличение размера кэша
📊 Категория: performance
⚡ Приоритет: medium
📝 Описание: Увеличить кэш с 50MB до 100MB для ускорения
🎯 Ожидаемый эффект: Сокращение времени ответа на 20%
⚠️ Уровень риска: low

Ваше решение? [a]pprove / [r]eject / [d]etails / [l]ater: 
```

### Можно ли отключить запросы подтверждения?

Нет, это критично для безопасности. Все изменения должны быть одобрены пользователем.

## Мониторинг и аналитика

### Какие метрики отслеживаются?

- **Время ответа** MCP серверов
- **Использование токенов** по агентам
- **Успешность запросов** (% успешных)
- **Использование кэша** (hit rate)
- **Аномалии производительности**

### Где хранятся данные мониторинга?

- **SQLite база**: `monitoring/performance.db`
- **Кэш**: В памяти + опционально Redis
- **Логи**: `logs/framework.log`
- **Отчеты**: `reports/` директория

### Как настроить кэширование?

```json
{
  "optimization": {
    "cache_enabled": true,
    "max_cache_size_mb": 100,
    "cache_ttl_hours": 24
  }
}
```

## Troubleshooting

### Фреймворк не запускается

1. **Проверьте версию Python**:
   ```bash
   python --version  # Должно быть 3.8+
   ```

2. **Проверьте зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Проверьте конфигурацию**:
   ```bash
   python -c "from config_validator import validate_all_configs; validate_all_configs()"
   ```

### Ошибки валидации конфигурации

```bash
# Запуск валидатора
python config_validator.py

# Исправление типичных ошибок:
# 1. Неверный тип проекта - используйте один из: telegram_bot, web_api, cli_tool, etc.
# 2. Отсутствуют зависимости компонентов - включите необходимые компоненты
# 3. Неверные пороги - проверьте числовые значения
```

### Высокое потребление памяти

1. **Уменьшите размер кэша**:
   ```json
   {"optimization": {"max_cache_size_mb": 50}}
   ```

2. **Отключите тяжелые компоненты**:
   ```json
   {"framework": {"components": {"optimizer_ai": false}}}
   ```

3. **Уменьшите частоту сбора метрик**:
   ```json
   {"monitoring": {"collection_interval_minutes": 5}}
   ```

### MCP серверы не отвечают

1. **Проверьте подключение**:
   ```bash
   # Проверьте доступность серверов
   python -c "from monitoring.mcp_monitor import test_connection; test_connection()"
   ```

2. **Проверьте API ключи** в переменных окружения:
   ```bash
   echo $ANTHROPIC_API_KEY
   echo $GITHUB_TOKEN
   echo $PERPLEXITY_API_KEY
   ```

3. **Проверьте лимиты** API (rate limiting)

### Алерты не приходят

1. **Проверьте email конфигурацию**:
   ```bash
   # Тест отправки email
   python -c "from monitoring.alert_system import test_email; test_email()"
   ```

2. **Проверьте пароль email** в переменных окружения:
   ```bash
   echo $EMAIL_PASSWORD
   ```

3. **Проверьте настройки firewall** для SMTP

## CLI команды

### Основные команды

```bash
# Создание нового проекта
python claude_framework_cli.py create --name MyBot --type telegram_bot

# Проверка статуса проекта
python claude_framework_cli.py status

# Валидация конфигурации
python claude_framework_cli.py validate

# Список доступных шаблонов
python claude_framework_cli.py list-templates

# Запуск инициализации
python claude_framework_cli.py init

# Показать версию
python claude_framework_cli.py version
```

### Полезные опции

```bash
# Создание с кастомными настройками
python claude_framework_cli.py create \
  --name "MyProject" \
  --type web_api \
  --scale enterprise \
  --dir /opt/myproject \
  --no-venv  # Без виртуального окружения

# Валидация конкретного файла
python claude_framework_cli.py validate config/framework_config.json

# Генерация конфигурации
python claude_framework_cli.py generate-config \
  --name TestProject \
  --type cli_tool \
  --scale minimal
```

## Интеграции

### MCP серверы

Фреймворк поддерживает интеграцию с:
- **Context7** - Поиск документации
- **GitHub** - Поиск кода и примеров
- **Exa** - Веб-поиск и исследования
- **Playwright** - Автоматизация браузера
- **TaskMaster-AI** - Управление задачами

### Внешние сервисы

- **Email SMTP** - Уведомления по email
- **Slack API** - Командные уведомления
- **Webhook endpoints** - Кастомные интеграции
- **Redis** - Расширенное кэширование

### Добавление кастомных интеграций

```python
# Создание кастомного плагина
from framework_plugin import FrameworkPlugin

class CustomPlugin(FrameworkPlugin):
    def on_mcp_request(self, request_data):
        # Обработка запросов
        pass
    
    def on_optimization_proposal(self, proposal):
        # Обработка предложений оптимизации
        pass

# Регистрация
framework.register_plugin('custom', CustomPlugin())
```

## Безопасность

### Рекомендации по безопасности

1. **Никогда не сохраняйте пароли** в конфигурационных файлах
2. **Используйте переменные окружения** для секретных данных
3. **Регулярно обновляйте зависимости**
4. **Проверяйте предложения оптимизации** перед подтверждением
5. **Делайте бэкапы конфигураций** перед изменениями

### Переменные окружения

```bash
# Создайте .env файл в корне проекта
echo "EMAIL_PASSWORD=your_password" >> .env
echo "GITHUB_TOKEN=your_token" >> .env
echo "ANTHROPIC_API_KEY=your_key" >> .env

# Загружайте в вашем коде
from dotenv import load_dotenv
load_dotenv()
```

### Аудит безопасности

```bash
# Проверка конфигурации на безопасность
python -c "from config_validator import validate_security; validate_security('.')"

# Проверка зависимостей
pip audit

# Сканирование кода
bandit -r .
```

## Производительность

### Оптимизация производительности

1. **Используйте кэширование**:
   ```json
   {"optimization": {"cache_enabled": true}}
   ```

2. **Настройте размер кэша** под ваши потребности:
   - Малые проекты: 50MB
   - Средние проекты: 100MB
   - Большие проекты: 200MB+

3. **Отключите ненужные компоненты**:
   ```json
   {"framework": {"components": {"optimizer_ai": false}}}
   ```

4. **Настройте интервалы сбора данных**:
   ```json
   {"monitoring": {"collection_interval_minutes": 5}}
   ```

### Мониторинг ресурсов

```bash
# Проверка использования памяти
python -c "from monitoring.performance_tracker import show_memory_usage; show_memory_usage()"

# Статистика кэша
python -c "from monitoring.cache_manager import show_cache_stats; show_cache_stats()"

# Общая статистика
python -c "from reports.auto_reporter import quick_stats; quick_stats()"
```

## Поддержка и сообщество

### Где получить помощь?

- **GitHub Issues**: https://github.com/claude-multiagent-framework/issues
- **Документация**: https://claude-multiagent-framework.readthedocs.io
- **Telegram канал**: @claude_framework
- **Email поддержка**: support@claude-framework.dev

### Как сообщить об ошибке?

1. **Проверьте существующие issues** на GitHub
2. **Соберите информацию**:
   ```bash
   python -c "import sys; print(f'Python: {sys.version}')"
   python claude_framework_cli.py version
   cat config/framework_config.json
   ```
3. **Создайте issue** с подробным описанием

### Как предложить улучшение?

1. **Форкните репозиторий**
2. **Создайте feature branch**
3. **Напишите тесты** для нового функционала
4. **Отправьте Pull Request**

### Roadmap развития

- **v1.1**: Поддержка Docker контейнеров
- **v1.2**: GUI интерфейс для управления
- **v1.3**: Интеграция с Kubernetes
- **v2.0**: Distributed mode для больших проектов

## Примеры использования

### Telegram Bot проект

```bash
# Создание проекта
python claude_framework_cli.py create --name TelegramBot --type telegram_bot --scale standard

# Структура проекта
TelegramBot/
├── bot/
│   ├── handlers/
│   └── main.py
├── monitoring/
├── config/
└── framework_init.py

# Запуск с мониторингом
python framework_init.py
python bot/main.py
```

### Web API проект

```bash
# Создание проекта
python claude_framework_cli.py create --name WebAPI --type web_api --scale advanced

# Запуск API с мониторингом
cd WebAPI
source venv/bin/activate
python framework_init.py
uvicorn api.main:app --reload
```

### CLI Tool проект

```bash
# Создание проекта
python claude_framework_cli.py create --name CliTool --type cli_tool --scale minimal

# Простой CLI с базовым мониторингом
cd CliTool
python cli/main.py --help
```

---

*Обновлено: 2025-07-11*  
*Claude MultiAgent Framework v1.0.0*