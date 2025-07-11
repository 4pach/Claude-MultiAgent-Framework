# Claude Code Development Kit - Workflow для Telegram Sticker Bot

## 🚀 Быстрый старт

### Запуск Claude Code в проекте:
```bash
cd /home/dmin/projects/telegram_sticker_bot/telegram_sticker_bot
claude
```

### Основные команды для разработки:
```bash
# Проверка статуса проекта
./dev-scripts.sh status

# Запуск бота
./dev-scripts.sh start

# Просмотр логов
./dev-scripts.sh logs

# Тестирование
./dev-scripts.sh test
```

## 📋 Интеграция с Claude Code Development Kit

### 1. Настройка проекта
Все настройки находятся в файле `.clauderc`:
- Пути к исходникам
- Команды для запуска
- Конфигурация AI сервисов
- Структура проекта

### 2. Автоматизация разработки
Скрипт `dev-scripts.sh` предоставляет:
- ✅ Проверку зависимостей
- ✅ Инициализацию базы данных
- ✅ Запуск и тестирование бота
- ✅ Просмотр логов
- ✅ Установку зависимостей

### 3. Структура для Claude Code
```
telegram_sticker_bot/
├── .clauderc              # Конфигурация Claude Code
├── CLAUDE.md              # Документация проекта
├── claude-dev-workflow.md # Этот файл
├── dev-scripts.sh         # Скрипты автоматизации
├── bot/                   # Основной код бота
│   ├── handlers/          # Обработчики событий
│   ├── menu/              # Модульная система меню
│   └── states/            # FSM состояния
├── services/              # AI сервисы и постобработка
│   ├── image_generation_service.py
│   ├── image_processing_service.py
│   └── sticker_service.py
├── db/                    # База данных
├── config/                # Конфигурация
└── storage/               # Хранилище изображений
```

## 🔧 Команды Claude Code для проекта

### Работа с ботом:
```bash
# В Claude Code CLI:
/run ./dev-scripts.sh start        # Запуск бота
/run ./dev-scripts.sh test         # Тестирование
/run ./dev-scripts.sh status       # Проверка статуса
```

### Разработка:
```bash
# Анализ кода
Проанализируй структуру бота в директории bot/

# Добавление новых функций
Добавь новый хендлер для обработки видео в bot/handlers/

# Работа с базой данных
Создай новую модель для хранения пользовательских настроек

# Тестирование AI сервисов
Протестируй интеграцию с Replicate API
```

## 🎯 Workflow для разработки

### Типичный цикл разработки:
1. **Запуск Claude Code**: `claude` в директории проекта
2. **Анализ задачи**: Опишите, что нужно сделать
3. **Разработка**: Claude Code поможет с кодом
4. **Тестирование**: `./dev-scripts.sh test`
5. **Запуск**: `./dev-scripts.sh start`
6. **Отладка**: `./dev-scripts.sh logs`

### Пример сессии:
```bash
# Терминал 1: Claude Code
cd /home/dmin/projects/telegram_sticker_bot/telegram_sticker_bot
claude

# В Claude Code:
Хочу добавить новую эмоцию "удивление" для генерации стикеров

# Терминал 2: Тестирование
./dev-scripts.sh test
./dev-scripts.sh start
```

## 🔍 Отладка и мониторинг

### Логирование:
- Основные логи: `logs/bot.log`
- Просмотр в реальном времени: `./dev-scripts.sh logs`
- Уровни логирования настроены в `logs/logging_config.py`

### Диагностика:
```bash
# Проверка всех компонентов
./dev-scripts.sh status

# Проверка базы данных
./dev-scripts.sh init-db

# Тестирование зависимостей
./dev-scripts.sh deps
```

## 🤖 AI Сервисы

### Replicate Integration:
- Модель: `fofr/face-to-many`
- Конфигурация: `services/replicate_client.py`
- API токен: `REPLICATE_API_TOKEN` в .env

### Leonardo AI:
- Конфигурация: `services/leonardo_client.py`
- API ключ: `LEONARDO_API_KEY` в .env

### Local Diffusers:
- Модель: `SG161222/Realistic_Vision_V6.0_B1_noVAE`
- Конфигурация: `services/image_generation_service.py`
- Требует: PyTorch, Diffusers

## 🎨 Постобработка изображений

### ImageProcessingService:
- Удаление фона: rembg (локально), Remove.bg API, ClipDrop API
- Ресайз до 512x512 пикселей для стикеров
- Конвертация в PNG с прозрачностью
- Оптимизация размера файла (<500KB)
- Валидация и предобработка изображений

### StickerService:
- Интеграция с ImageProcessingService
- Создание стикерпаков Telegram
- Управление вариантами стикеров
- Очистка временных файлов

## 📚 Полезные команды для Claude Code

### Анализ кода:
```
Проанализируй архитектуру бота
Найди потенциальные проблемы в коде
Предложи оптимизации для производительности
```

### Добавление функций:
```
Добавь поддержку групповых чатов
Реализуй систему подписок
Создай админ-панель для управления ботом
```

### Рефакторинг:
```
Оптимизируй код в services/image_generation_service.py
Улучши обработку ошибок в handlers/
Добавь типизацию для всех функций
```

## 🎨 Кастомизация

### Добавление новых AI сервисов:
1. Создать клиент в `services/`
2. Добавить в `ImageGenerationService`
3. Обновить конфигурацию в `config/config.py`
4. Добавить в `.clauderc`

### Добавление новых API удаления фона:
1. Добавить конфигурацию API в `ImageProcessingService.__init__()`
2. Реализовать обработку в `_remove_background_api()`
3. Добавить переменные окружения в `.env`
4. Обновить документацию в `CLAUDE.md`

### Новые типы контента:
1. Расширить модели в `db/models.py`
2. Добавить хендлеры в `bot/handlers/`
3. Обновить клавиатуры в `bot/keyboards.py`

## 🔐 Безопасность

### Переменные окружения:
- Никогда не коммитить реальные API ключи
- Использовать `.env` файл
- Проверять наличие ключей в `config/config.py`
- Новые API ключи для постобработки:
  - `REMOVEBG_API_KEY` (опционально)
  - `CLIPDROP_API_KEY` (опционально)

### Обработка ошибок:
- Логировать все ошибки
- Не показывать внутренние ошибки пользователям
- Graceful degradation для AI сервисов

---

**Создано для оптимальной работы с Claude Code Development Kit**
*Обновлено: 2025-07-11 - Добавлена система постобработки изображений*