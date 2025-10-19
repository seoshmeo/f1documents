#!/usr/bin/env python3
"""
Simple script to test database connection
"""

import psycopg2
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection and display info"""

    print("="*60)
    print("Проверка подключения к базе данных PostgreSQL")
    print("="*60)

    # Display connection parameters (hide password)
    print(f"\nПараметры подключения:")
    print(f"  Хост: {os.getenv('DB_HOST', 'не указан')}")
    print(f"  Порт: {os.getenv('DB_PORT', 'не указан')}")
    print(f"  База данных: {os.getenv('DB_NAME', 'не указан')}")
    print(f"  Пользователь: {os.getenv('DB_USER', 'не указан')}")
    print(f"  Пароль: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'не указан'}")

    print("\n" + "="*60)
    print("Попытка подключения...")
    print("="*60 + "\n")

    try:
        # Try to connect
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

        cursor = connection.cursor()

        # Get PostgreSQL version
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]

        print("✅ ПОДКЛЮЧЕНИЕ УСПЕШНО!")
        print(f"\nPostgreSQL версия:")
        print(f"  {version}")

        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'fia_documents'
            );
        """)
        table_exists = cursor.fetchone()[0]

        print(f"\nТаблица 'fia_documents': {'✅ Существует' if table_exists else '❌ Не найдена'}")

        if table_exists:
            # Get document count
            cursor.execute("SELECT COUNT(*) FROM fia_documents;")
            count = cursor.fetchone()[0]
            print(f"Количество документов в базе: {count}")

            # Get latest document
            cursor.execute("""
                SELECT document_name, created_at
                FROM fia_documents
                ORDER BY created_at DESC
                LIMIT 1;
            """)
            latest = cursor.fetchone()

            if latest:
                print(f"\nПоследний документ:")
                print(f"  Название: {latest[0]}")
                print(f"  Добавлен: {latest[1]}")
            else:
                print("\nБаза данных пуста (нет документов)")
        else:
            print("\n⚠️  Таблица 'fia_documents' не найдена!")
            print("Запустите 'python main.py once' для автоматического создания таблицы")

        # Close connection
        cursor.close()
        connection.close()

        print("\n" + "="*60)
        print("Подключение закрыто")
        print("="*60)

        return True

    except psycopg2.OperationalError as e:
        print("❌ ОШИБКА ПОДКЛЮЧЕНИЯ!")
        print(f"\nДетали ошибки:")
        print(f"  {e}")

        print(f"\n💡 Возможные причины:")
        print(f"  1. Неверный хост или порт")
        print(f"  2. База данных не существует")
        print(f"  3. Неверное имя пользователя или пароль")
        print(f"  4. PostgreSQL не запущен")
        print(f"  5. Фаервол блокирует подключение")

        print(f"\n📝 Проверьте настройки в файле .env")

        return False

    except psycopg2.Error as e:
        print("❌ ОШИБКА POSTGRESQL!")
        print(f"\nДетали ошибки:")
        print(f"  {e}")
        return False

    except Exception as e:
        print("❌ НЕИЗВЕСТНАЯ ОШИБКА!")
        print(f"\nДетали ошибки:")
        print(f"  {e}")
        return False


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
