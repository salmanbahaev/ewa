"""Скрипт для сброса выбора пола ассистента"""
import asyncio
import aiosqlite
import config


async def reset_gender(user_id: int = None):
    """Сбросить выбор ассистента для пользователя или всех"""
    async with aiosqlite.connect(config.DATABASE_PATH) as db:
        if user_id:
            await db.execute("""
                UPDATE users 
                SET assistant_gender = NULL
                WHERE user_id = ?
            """, (user_id,))
            print(f"✅ Сброшен выбор ассистента для пользователя {user_id}")
        else:
            await db.execute("""
                UPDATE users 
                SET assistant_gender = NULL
            """)
            print("✅ Сброшен выбор ассистента для всех пользователей")
        
        await db.commit()


if __name__ == "__main__":
    import sys
    
    user_id = None
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])
    
    asyncio.run(reset_gender(user_id))

