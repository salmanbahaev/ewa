"""Скрипт для проверки содержимого базы данных"""
import asyncio
import sys
from data.database import Database
import config


async def check_database():
    """Проверка содержимого БД"""
    db = Database(config.DATABASE_PATH)
    
    print("=" * 60)
    print("📊 ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    print(f"\n📁 Путь к БД: {config.DATABASE_PATH}")
    
    if not config.DATABASE_PATH.exists():
        print("\n❌ База данных не найдена!")
        return
    
    print("\n✅ База данных найдена!\n")
    
    # Получаем всех пользователей
    import aiosqlite
    async with aiosqlite.connect(db.db_path) as conn:
            # Пользователи
            print("-" * 60)
            print("👥 ПОЛЬЗОВАТЕЛИ:")
            print("-" * 60)
            async with conn.execute("""
                SELECT user_id, username, first_name, assistant_gender, created_at 
                FROM users
            """) as cursor:
                users = await cursor.fetchall()
                if users:
                    for user in users:
                        gender = user[3]
                        if gender == "male":
                            gender_display = "👨 Сергей"
                        elif gender == "female":
                            gender_display = "👩 Екатерина"
                        else:
                            gender_display = "❓ Не выбран"
                        
                        print(f"🆔 ID: {user[0]}")
                        print(f"   Username: @{user[1] or 'не указан'}")
                        print(f"   Имя: {user[2] or 'не указано'}")
                        print(f"   Ассистент: {gender_display}")
                        print(f"   Зарегистрирован: {user[4]}")
                        print()
                else:
                    print("   Нет пользователей\n")
            
            # Статистика сообщений
            print("-" * 60)
            print("💬 СТАТИСТИКА СООБЩЕНИЙ:")
            print("-" * 60)
            async with conn.execute("""
                SELECT user_id, COUNT(*) as count
                FROM messages
                GROUP BY user_id
            """) as cursor:
                stats = await cursor.fetchall()
                if stats:
                    for user_id, count in stats:
                        print(f"🆔 User {user_id}: {count} сообщений")
                    print()
                else:
                    print("   Нет сообщений\n")
            
            # Последние 10 сообщений
            print("-" * 60)
            print("📝 ПОСЛЕДНИЕ 10 СООБЩЕНИЙ:")
            print("-" * 60)
            async with conn.execute("""
                SELECT m.user_id, u.username, m.role, m.content, m.timestamp
                FROM messages m
                LEFT JOIN users u ON m.user_id = u.user_id
                ORDER BY m.timestamp DESC
                LIMIT 10
            """) as cursor:
                messages = await cursor.fetchall()
                if messages:
                    for msg in messages:
                        user_id, username, role, content, timestamp = msg
                        emoji = "👤" if role == "user" else "🤖"
                        content_short = content[:50] + "..." if len(content) > 50 else content
                        print(f"{emoji} @{username or user_id} [{role}] ({timestamp}):")
                        print(f"   {content_short}")
                        print()
                else:
                    print("   Нет сообщений\n")
            
            # Общая статистика
            print("-" * 60)
            print("📈 ОБЩАЯ СТАТИСТИКА:")
            print("-" * 60)
            
            async with conn.execute("SELECT COUNT(*) FROM users") as cursor:
                user_count = (await cursor.fetchone())[0]
                print(f"👥 Всего пользователей: {user_count}")
            
            async with conn.execute("SELECT COUNT(*) FROM messages") as cursor:
                msg_count = (await cursor.fetchone())[0]
                print(f"💬 Всего сообщений: {msg_count}")
            
            async with conn.execute("""
                SELECT COUNT(*) FROM messages WHERE role = 'user'
            """) as cursor:
                user_msg = (await cursor.fetchone())[0]
                print(f"   ├─ От пользователей: {user_msg}")
            
            async with conn.execute("""
                SELECT COUNT(*) FROM messages WHERE role = 'assistant'
            """) as cursor:
                ai_msg = (await cursor.fetchone())[0]
                print(f"   └─ От ассистента: {ai_msg}")
            
            print("\n" + "=" * 60)
    
    await db.close()


if __name__ == "__main__":
    try:
        asyncio.run(check_database())
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

