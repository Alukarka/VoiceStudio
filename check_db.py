# check_db.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VoiceStudio.settings')
django.setup()

from django.db import connection

print("=== ПРОВЕРКА БАЗЫ ДАННЫХ POSTGRESQL ===\n")

# 1. Основная информация
print("1. Параметры подключения:")
print(f"   База данных: {connection.settings_dict['NAME']}")
print(f"   Пользователь: {connection.settings_dict['USER']}")
print(f"   Хост: {connection.settings_dict['HOST']}:{connection.settings_dict['PORT']}")

# 2. Проверка таблиц
print("\n2. Таблицы в базе данных:")
try:
    with connection.cursor() as cursor:
        # Список всех таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        if len(tables) == 0:
            print("   ❌ Нет таблиц. Возможно, миграции не применены.")
        else:
            print(f"   ✅ Найдено таблиц: {len(tables)}")

            # Группируем таблицы по префиксам
            django_tables = []
            app_tables = []
            other_tables = []

            for table in tables:
                table_name = table[0]
                if table_name.startswith('auth_') or table_name.startswith('django_'):
                    django_tables.append(table_name)
                elif table_name.startswith('exercises_') or table_name.startswith('users_') or table_name.startswith(
                        'main_'):
                    app_tables.append(table_name)
                else:
                    other_tables.append(table_name)

            if django_tables:
                print(f"   • Django системные: {len(django_tables)}")
                for tbl in django_tables[:3]:
                    print(f"     - {tbl}")
                if len(django_tables) > 3:
                    print(f"     ... и еще {len(django_tables) - 3}")

            if app_tables:
                print(f"   • Ваши приложения: {len(app_tables)}")
                for tbl in app_tables[:5]:
                    print(f"     - {tbl}")
                if len(app_tables) > 5:
                    print(f"     ... и еще {len(app_tables) - 5}")

            if other_tables:
                print(f"   • Другие таблицы: {len(other_tables)}")
                for tbl in other_tables[:3]:
                    print(f"     - {tbl}")

        # 3. Проверка пользователей
        print("\n3. Проверка данных:")
        try:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
            print(f"   ✅ Пользователей: {user_count}")
        except:
            print("   ⚠️  Таблица auth_user не найдена")

        # 4. Проверка версии PostgreSQL
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\n4. Версия PostgreSQL:")
        print(f"   {version}")

except Exception as e:
    print(f"   ❌ Ошибка при подключении: {e}")
    print("\n   ВОЗМОЖНЫЕ ПРИЧИНЫ:")
    print("   1. Сервер PostgreSQL не запущен")
    print("   2. База 'voicestudio' не существует")
    print("   3. Неправильный пароль пользователя 'postgres'")

print("\n=== РЕКОМЕНДАЦИИ ===")
if len(tables) == 0:
    print("1. Примените миграции: python manage.py migrate")
    print("2. Создайте суперпользователя: python manage.py createsuperuser")
else:
    print("✅ База данных настроена корректно!")