@echo off
REM Claude MultiAgent Framework Installer (Windows)
REM Автоматическая установка фреймворка

setlocal enabledelayedexpansion

REM Цвета для вывода (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "BOLD=[1m"
set "RESET=[0m"

REM Функции для цветного вывода
goto :main

:print_error
echo %RED%❌ %~1%RESET%
goto :eof

:print_success
echo %GREEN%✅ %~1%RESET%
goto :eof

:print_info
echo %BLUE%ℹ️ %~1%RESET%
goto :eof

:print_warning
echo %YELLOW%⚠️ %~1%RESET%
goto :eof

:print_header
echo %CYAN%%BOLD%%~1%RESET%
goto :eof

:print_banner
echo %CYAN%╔════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║%RESET% %BOLD%Claude MultiAgent Framework Installer%RESET%                  %CYAN%║%RESET%
echo %CYAN%║%RESET%                          v1.0.0                          %CYAN%║%RESET%
echo %CYAN%╚════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %BOLD%🤖 Универсальный фреймворк для автономного мониторинга%RESET%
echo %BOLD%   и оптимизации проектов с помощью ИИ%RESET%
echo.
goto :eof

:check_command
where %1 >nul 2>&1
goto :eof

:check_requirements
call :print_header "🔍 Проверка системных требований..."

set "requirements_met=true"

REM Проверка Python
call :check_command python
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set python_version=%%i
    python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "Python версия: !python_version!"
    ) else (
        call :print_error "Python 3.8+ требуется (текущая: !python_version!)"
        set "requirements_met=false"
    )
) else (
    call :print_error "Python не найден"
    set "requirements_met=false"
)

REM Проверка pip
python -m pip --version >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "pip доступен"
) else (
    call :print_error "pip не найден"
    set "requirements_met=false"
)

REM Проверка git (опционально)
call :check_command git
if !errorlevel! equ 0 (
    call :print_success "git доступен"
) else (
    call :print_warning "git не найден (опционально)"
)

if "!requirements_met!"=="false" (
    call :print_error "Не все требования выполнены"
    exit /b 1
)
goto :eof

:install_framework
set "project_name=%~1"
set "project_type=%~2"
set "project_scale=%~3"
set "install_dir=%~4"

REM Проверка параметров
if "%project_name%"=="" (
    call :print_error "Недостаточно параметров для установки"
    call :show_usage
    exit /b 1
)
if "%project_type%"=="" (
    call :print_error "Недостаточно параметров для установки"
    call :show_usage
    exit /b 1
)
if "%project_scale%"=="" (
    call :print_error "Недостаточно параметров для установки"
    call :show_usage
    exit /b 1
)

REM Установка директории по умолчанию
if "%install_dir%"=="" set "install_dir=%cd%\%project_name%"

call :print_header "🏗️ Создание проекта: %project_name%"
call :print_info "Тип: %project_type%"
call :print_info "Масштаб: %project_scale%"
call :print_info "Директория: %install_dir%"

REM Создание директории
if not exist "%install_dir%" mkdir "%install_dir%"
cd /d "%install_dir%"

REM Запуск Python инсталлятора
call :print_info "Запуск инсталлятора..."

REM Если локальный файл существует, используем его
if exist "..\install.py" (
    python ..\install.py --silent --name "%project_name%" --type "%project_type%" --scale "%project_scale%" --dir "%install_dir%"
) else (
    call :print_warning "Создание базовой структуры..."
    
    REM Создание директорий
    mkdir monitoring reports recommendations autonomous config logs tests 2>nul
    
    REM Создание framework_init.py
    (
        echo #!/usr/bin/env python3
        echo """
        echo Инициализация Claude MultiAgent Framework
        echo """
        echo.
        echo def initialize_framework(project_type=None^):
        echo     print("🚀 Инициализация Claude MultiAgent Framework..."^)
        echo     print(f"📋 Тип проекта: {project_type}"^)
        echo     print("✅ Фреймворк инициализирован!"^)
        echo     return True
        echo.
        echo if __name__ == "__main__":
        echo     initialize_framework(^)
    ) > framework_init.py
    
    REM Создание requirements.txt
    (
        echo # Claude MultiAgent Framework dependencies
        echo aiosqlite^>=0.19.0
        echo numpy^>=1.24.0
        echo scikit-learn^>=1.3.0
        echo matplotlib^>=3.7.0
        echo jinja2^>=3.1.0
        echo schedule^>=1.2.0
        echo jsonschema^>=4.17.0
    ) > requirements.txt
    
    REM Создание README.md
    (
        echo # %project_name%
        echo.
        echo Проект создан с помощью **Claude MultiAgent Framework**.
        echo.
        echo ## Тип проекта
        echo %project_type% (%project_scale%^)
        echo.
        echo ## Быстрый старт
        echo.
        echo 1. Активируйте виртуальное окружение:
        echo    ```cmd
        echo    venv\Scripts\activate
        echo    ```
        echo.
        echo 2. Установите зависимости:
        echo    ```cmd
        echo    pip install -r requirements.txt
        echo    ```
        echo.
        echo 3. Инициализируйте фреймворк:
        echo    ```cmd
        echo    python framework_init.py
        echo    ```
    ) > README.md
    
    call :print_success "Базовая структура создана"
)

REM Создание виртуального окружения
if not "%NO_VENV%"=="true" (
    call :print_info "Создание виртуального окружения..."
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    call :print_success "Виртуальное окружение создано"
)

REM Установка зависимостей
if not "%NO_DEPS%"=="true" (
    if exist "requirements.txt" (
        call :print_info "Установка зависимостей..."
        pip install -r requirements.txt
        call :print_success "Зависимости установлены"
    )
)

REM Инициализация Git
if not "%NO_GIT%"=="true" (
    call :check_command git
    if !errorlevel! equ 0 (
        call :print_info "Инициализация Git репозитория..."
        git init
        git add .
        git commit -m "Initial commit: %project_name% with Claude MultiAgent Framework"
        call :print_success "Git репозиторий инициализирован"
    )
)

REM Вывод информации о завершении
call :print_success "Установка завершена!"
echo.
call :print_header "🚀 Для начала работы:"
echo cd %install_dir%
if not "%NO_VENV%"=="true" echo venv\Scripts\activate
echo python framework_init.py
echo.
call :print_info "Документация: docs\usage_guide.md"
call :print_info "Поддержка: https://github.com/claude-multiagent-framework"
goto :eof

:interactive_install
call :print_header "📋 Настройка проекта"

REM Ввод имени проекта
:ask_name
set /p "project_name=Введите имя проекта: "
if "%project_name%"=="" goto :ask_name
REM Простая проверка имени (Windows batch ограничен в regex)
echo %project_name% | findstr /r "^[a-zA-Z0-9_-]*$" >nul
if errorlevel 1 (
    call :print_error "Имя должно содержать только буквы, цифры, _ и -"
    goto :ask_name
)

REM Выбор типа проекта
echo.
call :print_header "Выберите тип проекта:"
echo 1. Telegram Bot
echo 2. Web API
echo 3. CLI Tool
echo 4. Data Pipeline
echo 5. Microservice
echo 6. ML Service
echo 7. Desktop App
echo 8. IoT Device

:ask_type
set /p "choice=Ваш выбор (1-8): "
if "%choice%"=="1" set "project_type=telegram_bot" & goto :type_done
if "%choice%"=="2" set "project_type=web_api" & goto :type_done
if "%choice%"=="3" set "project_type=cli_tool" & goto :type_done
if "%choice%"=="4" set "project_type=data_pipeline" & goto :type_done
if "%choice%"=="5" set "project_type=microservice" & goto :type_done
if "%choice%"=="6" set "project_type=ml_service" & goto :type_done
if "%choice%"=="7" set "project_type=desktop_app" & goto :type_done
if "%choice%"=="8" set "project_type=iot_device" & goto :type_done
call :print_error "Выберите число от 1 до 8"
goto :ask_type

:type_done

REM Выбор масштаба
echo.
call :print_header "Выберите масштаб проекта:"
echo 1. Минимальный (базовый мониторинг)
echo 2. Стандартный (мониторинг + алерты)
echo 3. Продвинутый (+ ИИ оптимизация)
echo 4. Корпоративный (полный функционал)

:ask_scale
set /p "choice=Ваш выбор (1-4): "
if "%choice%"=="1" set "project_scale=minimal" & goto :scale_done
if "%choice%"=="2" set "project_scale=standard" & goto :scale_done
if "%choice%"=="3" set "project_scale=advanced" & goto :scale_done
if "%choice%"=="4" set "project_scale=enterprise" & goto :scale_done
call :print_error "Выберите число от 1 до 4"
goto :ask_scale

:scale_done

REM Директория установки
set "default_dir=%cd%\%project_name%"
set /p "install_dir=Директория установки [%default_dir%]: "
if "%install_dir%"=="" set "install_dir=%default_dir%"

REM Дополнительные опции
echo.
call :print_header "Дополнительные опции:"

set /p "create_venv=Создать виртуальное окружение? [Y/n]: "
if /i "%create_venv%"=="n" set "NO_VENV=true"

set /p "install_deps=Установить зависимости автоматически? [Y/n]: "
if /i "%install_deps%"=="n" set "NO_DEPS=true"

set /p "init_git=Инициализировать Git репозиторий? [Y/n]: "
if /i "%init_git%"=="n" set "NO_GIT=true"

REM Запуск установки
call :install_framework "%project_name%" "%project_type%" "%project_scale%" "%install_dir%"
goto :eof

:show_usage
echo Использование: %~nx0 [ОПЦИИ]
echo.
echo Опции:
echo   -n, --name NAME           Имя проекта
echo   -t, --type TYPE           Тип проекта (telegram_bot, web_api, cli_tool, etc.)
echo   -s, --scale SCALE         Масштаб (minimal, standard, advanced, enterprise)
echo   -d, --dir DIRECTORY       Директория установки
echo   --no-venv                 Не создавать виртуальное окружение
echo   --no-deps                 Не устанавливать зависимости
echo   --no-git                  Не инициализировать Git
echo   -h, --help                Показать эту справку
echo.
echo Примеры:
echo   %~nx0                                             # Интерактивная установка
echo   %~nx0 -n MyBot -t telegram_bot -s advanced       # Быстрая установка
goto :eof

:main
call :print_banner
call :check_requirements
if errorlevel 1 exit /b 1

REM Парсинг аргументов
:parse_args
if "%~1"=="" goto :args_done

if "%~1"=="-n" (
    set "PROJECT_NAME=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="--name" (
    set "PROJECT_NAME=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="-t" (
    set "PROJECT_TYPE=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="--type" (
    set "PROJECT_TYPE=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="-s" (
    set "PROJECT_SCALE=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="--scale" (
    set "PROJECT_SCALE=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="-d" (
    set "INSTALL_DIR=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="--dir" (
    set "INSTALL_DIR=%~2"
    shift /1
    shift /1
    goto :parse_args
)
if "%~1"=="--no-venv" (
    set "NO_VENV=true"
    shift /1
    goto :parse_args
)
if "%~1"=="--no-deps" (
    set "NO_DEPS=true"
    shift /1
    goto :parse_args
)
if "%~1"=="--no-git" (
    set "NO_GIT=true"
    shift /1
    goto :parse_args
)
if "%~1"=="-h" (
    call :show_usage
    exit /b 0
)
if "%~1"=="--help" (
    call :show_usage
    exit /b 0
)

call :print_error "Неизвестная опция: %~1"
call :show_usage
exit /b 1

:args_done

REM Если параметры заданы, выполняем автоматическую установку
if not "%PROJECT_NAME%"=="" (
    if not "%PROJECT_TYPE%"=="" (
        if not "%PROJECT_SCALE%"=="" (
            call :install_framework "%PROJECT_NAME%" "%PROJECT_TYPE%" "%PROJECT_SCALE%" "%INSTALL_DIR%"
            goto :end
        )
    )
)

REM Иначе интерактивная установка
call :interactive_install

:end