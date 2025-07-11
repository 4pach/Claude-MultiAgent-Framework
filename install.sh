#!/bin/bash
# Claude MultiAgent Framework Installer (Linux/macOS)
# Автоматическая установка фреймворка

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Функции для цветного вывода
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_header() {
    echo -e "${CYAN}${BOLD}$1${NC}"
}

# Функция для проверки команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Баннер
print_banner() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} ${BOLD}Claude MultiAgent Framework Installer${NC}                  ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                          v1.0.0                          ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}🤖 Универсальный фреймворк для автономного мониторинга${NC}"
    echo -e "${BOLD}   и оптимизации проектов с помощью ИИ${NC}"
    echo ""
}

# Проверка системных требований
check_requirements() {
    print_header "🔍 Проверка системных требований..."
    
    local requirements_met=true
    
    # Проверка Python
    if command_exists python3; then
        local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python версия: $python_version"
        else
            print_error "Python 3.8+ требуется (текущая: $python_version)"
            requirements_met=false
        fi
    else
        print_error "Python 3 не найден"
        requirements_met=false
    fi
    
    # Проверка pip
    if command_exists pip3 || python3 -m pip --version >/dev/null 2>&1; then
        print_success "pip доступен"
    else
        print_error "pip не найден"
        requirements_met=false
    fi
    
    # Проверка git (опционально)
    if command_exists git; then
        print_success "git доступен"
    else
        print_warning "git не найден (опционально)"
    fi
    
    # Проверка curl/wget для загрузки
    if command_exists curl; then
        DOWNLOAD_CMD="curl -L"
        print_success "curl доступен"
    elif command_exists wget; then
        DOWNLOAD_CMD="wget -O -"
        print_success "wget доступен"
    else
        print_error "curl или wget требуется для загрузки"
        requirements_met=false
    fi
    
    if [ "$requirements_met" = false ]; then
        print_error "Не все требования выполнены"
        exit 1
    fi
}

# Функция установки
install_framework() {
    local project_name="$1"
    local project_type="$2"
    local project_scale="$3"
    local install_dir="$4"
    
    # Проверка параметров
    if [ -z "$project_name" ] || [ -z "$project_type" ] || [ -z "$project_scale" ]; then
        print_error "Недостаточно параметров для установки"
        show_usage
        exit 1
    fi
    
    # Установка директории по умолчанию
    if [ -z "$install_dir" ]; then
        install_dir="$(pwd)/$project_name"
    fi
    
    print_header "🏗️ Создание проекта: $project_name"
    print_info "Тип: $project_type"
    print_info "Масштаб: $project_scale"
    print_info "Директория: $install_dir"
    
    # Создание директории
    mkdir -p "$install_dir"
    cd "$install_dir"
    
    # Загрузка и запуск Python инсталлятора
    print_info "Загрузка инсталлятора..."
    
    # Если локальный файл существует, используем его
    if [ -f "../install.py" ]; then
        python3 ../install.py --silent --name "$project_name" --type "$project_type" --scale "$project_scale" --dir "$install_dir"
    else
        # Иначе загружаем с GitHub (когда будет опубликован)
        print_warning "Используется локальная версия инсталлятора"
        
        # Создание базовой структуры
        mkdir -p monitoring reports recommendations autonomous config logs tests
        
        # Создание базовых файлов
        cat > framework_init.py << 'EOF'
#!/usr/bin/env python3
"""
Инициализация Claude MultiAgent Framework
"""

def initialize_framework(project_type=None):
    print("🚀 Инициализация Claude MultiAgent Framework...")
    print(f"📋 Тип проекта: {project_type}")
    print("✅ Фреймворк инициализирован!")
    return True

if __name__ == "__main__":
    initialize_framework()
EOF

        # requirements.txt
        cat > requirements.txt << 'EOF'
# Claude MultiAgent Framework dependencies
aiosqlite>=0.19.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
jinja2>=3.1.0
schedule>=1.2.0
jsonschema>=4.17.0
EOF

        # README.md
        cat > README.md << EOF
# $project_name

Проект создан с помощью **Claude MultiAgent Framework**.

## Тип проекта
$project_type ($project_scale)

## Быстрый старт

1. Активируйте виртуальное окружение:
   \`\`\`bash
   source venv/bin/activate
   \`\`\`

2. Установите зависимости:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Инициализируйте фреймворк:
   \`\`\`bash
   python framework_init.py
   \`\`\`

## Документация

См. документацию Claude MultiAgent Framework для подробностей.
EOF

        print_success "Базовая структура создана"
    fi
    
    # Создание виртуального окружения
    if [ "${NO_VENV:-false}" != "true" ]; then
        print_info "Создание виртуального окружения..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        print_success "Виртуальное окружение создано"
    fi
    
    # Установка зависимостей
    if [ "${NO_DEPS:-false}" != "true" ] && [ -f "requirements.txt" ]; then
        print_info "Установка зависимостей..."
        pip install -r requirements.txt
        print_success "Зависимости установлены"
    fi
    
    # Инициализация Git
    if [ "${NO_GIT:-false}" != "true" ] && command_exists git; then
        print_info "Инициализация Git репозитория..."
        git init
        git add .
        git commit -m "Initial commit: $project_name with Claude MultiAgent Framework"
        print_success "Git репозиторий инициализирован"
    fi
    
    # Вывод информации о завершении
    print_success "Установка завершена!"
    echo ""
    print_header "🚀 Для начала работы:"
    echo "cd $install_dir"
    if [ "${NO_VENV:-false}" != "true" ]; then
        echo "source venv/bin/activate"
    fi
    echo "python framework_init.py"
    echo ""
    print_info "Документация: docs/usage_guide.md"
    print_info "Поддержка: https://github.com/claude-multiagent-framework"
}

# Интерактивная установка
interactive_install() {
    print_header "📋 Настройка проекта"
    
    # Ввод имени проекта
    while true; do
        read -p "Введите имя проекта: " project_name
        if [[ $project_name =~ ^[a-zA-Z0-9_-]+$ ]] && [ -n "$project_name" ]; then
            break
        else
            print_error "Имя должно содержать только буквы, цифры, _ и -"
        fi
    done
    
    # Выбор типа проекта
    echo ""
    print_header "Выберите тип проекта:"
    echo "1. Telegram Bot"
    echo "2. Web API"
    echo "3. CLI Tool"
    echo "4. Data Pipeline"
    echo "5. Microservice"
    echo "6. ML Service"
    echo "7. Desktop App"
    echo "8. IoT Device"
    
    while true; do
        read -p "Ваш выбор (1-8): " choice
        case $choice in
            1) project_type="telegram_bot"; break;;
            2) project_type="web_api"; break;;
            3) project_type="cli_tool"; break;;
            4) project_type="data_pipeline"; break;;
            5) project_type="microservice"; break;;
            6) project_type="ml_service"; break;;
            7) project_type="desktop_app"; break;;
            8) project_type="iot_device"; break;;
            *) print_error "Выберите число от 1 до 8";;
        esac
    done
    
    # Выбор масштаба
    echo ""
    print_header "Выберите масштаб проекта:"
    echo "1. Минимальный (базовый мониторинг)"
    echo "2. Стандартный (мониторинг + алерты)"
    echo "3. Продвинутый (+ ИИ оптимизация)"
    echo "4. Корпоративный (полный функционал)"
    
    while true; do
        read -p "Ваш выбор (1-4): " choice
        case $choice in
            1) project_scale="minimal"; break;;
            2) project_scale="standard"; break;;
            3) project_scale="advanced"; break;;
            4) project_scale="enterprise"; break;;
            *) print_error "Выберите число от 1 до 4";;
        esac
    done
    
    # Директория установки
    default_dir="$(pwd)/$project_name"
    read -p "Директория установки [$default_dir]: " install_dir
    install_dir=${install_dir:-$default_dir}
    
    # Дополнительные опции
    echo ""
    print_header "Дополнительные опции:"
    
    read -p "Создать виртуальное окружение? [Y/n]: " create_venv
    if [[ $create_venv =~ ^[Nn] ]]; then
        export NO_VENV=true
    fi
    
    read -p "Установить зависимости автоматически? [Y/n]: " install_deps
    if [[ $install_deps =~ ^[Nn] ]]; then
        export NO_DEPS=true
    fi
    
    read -p "Инициализировать Git репозиторий? [Y/n]: " init_git
    if [[ $init_git =~ ^[Nn] ]]; then
        export NO_GIT=true
    fi
    
    # Запуск установки
    install_framework "$project_name" "$project_type" "$project_scale" "$install_dir"
}

# Показать использование
show_usage() {
    echo "Использование: $0 [ОПЦИИ]"
    echo ""
    echo "Опции:"
    echo "  -n, --name NAME           Имя проекта"
    echo "  -t, --type TYPE           Тип проекта (telegram_bot, web_api, cli_tool, etc.)"
    echo "  -s, --scale SCALE         Масштаб (minimal, standard, advanced, enterprise)"
    echo "  -d, --dir DIRECTORY       Директория установки"
    echo "  --no-venv                 Не создавать виртуальное окружение"
    echo "  --no-deps                 Не устанавливать зависимости"
    echo "  --no-git                  Не инициализировать Git"
    echo "  -h, --help                Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0                                          # Интерактивная установка"
    echo "  $0 -n MyBot -t telegram_bot -s advanced    # Быстрая установка"
    echo "  $0 --name MyAPI --type web_api --scale enterprise --dir /opt/myapi"
}

# Основная функция
main() {
    print_banner
    check_requirements
    
    # Парсинг аргументов
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                PROJECT_NAME="$2"
                shift 2
                ;;
            -t|--type)
                PROJECT_TYPE="$2"
                shift 2
                ;;
            -s|--scale)
                PROJECT_SCALE="$2"
                shift 2
                ;;
            -d|--dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --no-venv)
                export NO_VENV=true
                shift
                ;;
            --no-deps)
                export NO_DEPS=true
                shift
                ;;
            --no-git)
                export NO_GIT=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Неизвестная опция: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Если параметры заданы, выполняем автоматическую установку
    if [ -n "$PROJECT_NAME" ] && [ -n "$PROJECT_TYPE" ] && [ -n "$PROJECT_SCALE" ]; then
        install_framework "$PROJECT_NAME" "$PROJECT_TYPE" "$PROJECT_SCALE" "$INSTALL_DIR"
    else
        # Иначе интерактивная установка
        interactive_install
    fi
}

# Запуск скрипта
main "$@"