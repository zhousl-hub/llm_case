"""用户服务测试"""
import pytest
from unittest.mock import MagicMock
from services.user_service import UserService
from schemas.user import UserCreate

@pytest.fixture
def mock_db():
    return MagicMock()

def test_create_user(mock_db):
    service = UserService(mock_db)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Test1234",
        full_name="测试用户"
    )
    user = service.create_user(user_data)
    assert mock_db.add.called
    assert mock_db.commit.called

def test_get_user_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    service = UserService(mock_db)
    user = service.get_user(999)
    assert user is None
