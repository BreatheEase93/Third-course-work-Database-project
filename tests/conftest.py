from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_db_connection():
    """Фикстура для мока подключения к БД"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor
