"""Database module for storing chat history"""
import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger


class Database:
    """SQLite database for storing user chat history"""
    
    def __init__(self, db_path: Path):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self) -> None:
        """Create tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    assistant_gender TEXT DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Index for faster queries
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_user_id 
                ON messages (user_id, timestamp DESC)
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def add_user(
        self, 
        user_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ) -> None:
        """
        Add or update user in database.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            """, (user_id, username, first_name))
            await db.execute("""
                UPDATE users 
                SET username = ?, first_name = ?
                WHERE user_id = ?
            """, (username, first_name, user_id))
            await db.commit()
            logger.debug(f"User {user_id} added/updated in database")
    
    async def set_assistant_gender(self, user_id: int, gender: str) -> None:
        """
        Set assistant gender preference for user.
        
        Args:
            user_id: Telegram user ID
            gender: 'male' or 'female'
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET assistant_gender = ?
                WHERE user_id = ?
            """, (gender, user_id))
            await db.commit()
            logger.debug(f"User {user_id} set assistant gender to {gender}")
    
    async def get_assistant_gender(self, user_id: int) -> Optional[str]:
        """
        Get assistant gender preference for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            'male', 'female', or None if not set
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT assistant_gender FROM users WHERE user_id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    
    async def add_message(
        self,
        user_id: int,
        role: str,
        content: str
    ) -> None:
        """
        Add message to chat history.
        
        Args:
            user_id: Telegram user ID
            role: Message role (user/assistant/system)
            content: Message content
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO messages (user_id, role, content)
                VALUES (?, ?, ?)
            """, (user_id, role, content))
            await db.commit()
            logger.debug(f"Message from {user_id} ({role}) saved to database")
    
    async def get_history(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get chat history for user (last N messages in chronological order).
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in format [{"role": "user", "content": "..."}]
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # Subquery to get last N messages, then order them chronologically
            async with db.execute("""
                SELECT role, content FROM (
                    SELECT role, content, timestamp
                    FROM messages
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ) ORDER BY timestamp ASC
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                messages = [
                    {"role": row["role"], "content": row["content"]}
                    for row in rows
                ]
                logger.debug(f"Retrieved {len(messages)} messages for user {user_id}")
                return messages
    
    async def clear_history(self, user_id: int) -> int:
        """
        Clear chat history for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Number of deleted messages
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM messages WHERE user_id = ?
            """, (user_id,))
            await db.commit()
            deleted = cursor.rowcount
            logger.info(f"Cleared {deleted} messages for user {user_id}")
            return deleted
    
    async def get_user_stats(self, user_id: int) -> Dict[str, any]:
        """
        Get statistics for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Dictionary with user statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get user info
            async with db.execute("""
                SELECT username, first_name, created_at
                FROM users
                WHERE user_id = ?
            """, (user_id,)) as cursor:
                user = await cursor.fetchone()
            
            # Get message count
            async with db.execute("""
                SELECT COUNT(*) as count
                FROM messages
                WHERE user_id = ?
            """, (user_id,)) as cursor:
                count_row = await cursor.fetchone()
            
            if not user:
                return {}
            
            return {
                "user_id": user_id,
                "username": user["username"],
                "first_name": user["first_name"],
                "registered_at": user["created_at"],
                "total_messages": count_row["count"] if count_row else 0
            }
    
    async def close(self) -> None:
        """Close database connection"""
        logger.info("Database connection closed")

