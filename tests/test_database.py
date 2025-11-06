"""Tests for database functionality"""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

from data.database import Database


@pytest.fixture
async def test_db():
    """Create temporary test database"""
    # Create temp file
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    
    db = Database(db_path)
    await db.init_db()
    
    yield db
    
    # Cleanup
    await db.close()
    if db_path.exists():
        os.remove(db_path)
    os.rmdir(temp_dir)


@pytest.mark.asyncio
async def test_add_user(test_db):
    """Test adding user to database"""
    await test_db.add_user(
        user_id=123456,
        username="testuser",
        first_name="Test"
    )
    
    stats = await test_db.get_user_stats(123456)
    assert stats["user_id"] == 123456
    assert stats["username"] == "testuser"
    assert stats["first_name"] == "Test"


@pytest.mark.asyncio
async def test_add_and_get_messages(test_db):
    """Test adding and retrieving messages"""
    user_id = 123456
    
    # Add user
    await test_db.add_user(user_id, "testuser", "Test")
    
    # Add messages
    await test_db.add_message(user_id, "user", "Hello")
    await test_db.add_message(user_id, "assistant", "Hi there!")
    await test_db.add_message(user_id, "user", "How are you?")
    
    # Get history (возвращается в хронологическом порядке - сначала старые)
    history = await test_db.get_history(user_id, limit=10)
    
    assert len(history) == 3
    # Проверяем что все роли правильные
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"  
    assert history[2]["role"] == "user"
    # Проверяем что сообщения в правильном порядке
    contents = [h["content"] for h in history]
    assert "Hello" in contents
    assert "Hi there!" in contents
    assert "How are you?" in contents


@pytest.mark.asyncio
async def test_clear_history(test_db):
    """Test clearing user history"""
    user_id = 123456
    
    # Add user and messages
    await test_db.add_user(user_id, "testuser", "Test")
    await test_db.add_message(user_id, "user", "Message 1")
    await test_db.add_message(user_id, "user", "Message 2")
    await test_db.add_message(user_id, "user", "Message 3")
    
    # Clear history
    deleted = await test_db.clear_history(user_id)
    
    assert deleted == 3, "Should delete 3 messages"
    
    # Check history is empty
    history = await test_db.get_history(user_id)
    assert len(history) == 0, "History should be empty after clearing"


@pytest.mark.asyncio
async def test_history_limit(test_db):
    """Test that history limit works"""
    user_id = 789012  # Different user to avoid conflicts
    
    # Add user and 10 messages
    await test_db.add_user(user_id, "testuser2", "Test2")
    for i in range(10):
        await test_db.add_message(user_id, "user", f"Msg {i}")
    
    # Get limited history with different limits
    history_3 = await test_db.get_history(user_id, limit=3)
    history_5 = await test_db.get_history(user_id, limit=5)
    history_all = await test_db.get_history(user_id, limit=100)
    
    # Test that limit parameter works correctly
    assert len(history_3) == 3, "Should return only 3 messages"
    assert len(history_5) == 5, "Should return only 5 messages"
    assert len(history_all) == 10, "Should return all 10 messages"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

