#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации новостного бота
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Проверяет наличие и содержимое .env файла"""
    print("🔍 Проверка .env файла...")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env файл не найден!")
        print("📝 Создайте .env файл на основе env_example.txt:")
        print("   cp env_example.txt .env")
        return False
    
    print("✅ .env файл найден")
    
    # Проверяем обязательные переменные
    required_vars = ['TELEGRAM_TOKEN', 'CHAT_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют обязательные переменные: {', '.join(missing_vars)}")
        return False
    
    print("✅ Все обязательные переменные установлены")
    return True

def check_dependencies():
    """Проверяет установленные зависимости"""
    print("\n🔍 Проверка зависимостей...")
    
    required_packages = [
        'telegram',
        'beautifulsoup4',
        'requests',
        'schedule',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'telegram':
                import telegram
            elif package == 'beautifulsoup4':
                import bs4
            elif package == 'requests':
                import requests
            elif package == 'schedule':
                import schedule
            elif package == 'python-dotenv':
                import dotenv
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Установите недостающие пакеты:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def check_directories():
    """Проверяет структуру директорий"""
    print("\n🔍 Проверка структуры проекта...")
    
    required_dirs = [
        'config',
        'database', 
        'services',
        'utils'
    ]
    
    required_files = [
        'config/settings.py',
        'database/models.py',
        'services/news_parser.py',
        'services/telegram_service.py',
        'utils/helpers.py',
        'main.py'
    ]
    
    # Проверяем директории
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ Директория {dir_name}/")
        else:
            print(f"❌ Директория {dir_name}/ не найдена")
            return False
    
    # Проверяем файлы
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ Файл {file_name}")
        else:
            print(f"❌ Файл {file_name} не найден")
            return False
    
    print("✅ Структура проекта корректна")
    return True

def test_telegram_connection():
    """Тестирует подключение к Telegram API"""
    print("\n🔍 Тест подключения к Telegram...")
    
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        print("❌ TELEGRAM_TOKEN не установлен")
        return False
    
    try:
        from telegram import Bot
        bot = Bot(token=token)
        bot_info = bot.get_me()
        print(f"✅ Подключение успешно: {bot_info.first_name} (@{bot_info.username})")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def main():
    """Главная функция проверки"""
    print("🚀 Проверка конфигурации новостного бота\n")
    
    checks = [
        check_env_file,
        check_dependencies,
        check_directories,
        test_telegram_connection
    ]
    
    all_passed = True
    
    for check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Ошибка при проверке: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 Все проверки пройдены успешно!")
        print("✅ Бот готов к запуску")
        print("\n🚀 Запустите бота командой:")
        print("   python main.py")
    else:
        print("❌ Обнаружены проблемы в конфигурации")
        print("🔧 Исправьте ошибки и запустите проверку снова")
        sys.exit(1)

if __name__ == '__main__':
    main()
