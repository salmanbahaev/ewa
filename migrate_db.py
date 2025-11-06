"""Скрипт для миграции БД - добавление поля assistant_gender"""
import asyncio
import aiosqlite
import config


async def migrate():
    """Добавить поле assistant_gender в таблицу users"""
    print("🔄 Миграция базы данных...")
    
    try:
        async with aiosqlite.connect(config.DATABASE_PATH) as db:
            # Проверяем есть ли уже поле
            async with db.execute("PRAGMA table_info(users)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if "assistant_gender" in column_names:
                    print("✅ Поле assistant_gender уже существует!")
                    return
            
            # Добавляем новое поле
            await db.execute("""
                ALTER TABLE users 
                ADD COLUMN assistant_gender TEXT DEFAULT NULL
            """)
            await db.commit()
            
            print("✅ Поле assistant_gender успешно добавлено!")
            print("📝 Теперь пользователи смогут выбрать пол ассистента.")
    
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")


if __name__ == "__main__":
    asyncio.run(migrate())

