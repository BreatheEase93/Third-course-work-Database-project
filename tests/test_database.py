import os
from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from src.db.database import create_database, create_tables, init_database


class TestDatabase:
    """Тесты для функций создания базы данных"""

    @patch("src.db.database.psycopg2.connect")
    def test_create_database_success(self, mock_connect):
        """Тест успешного создания базы данных"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # БД не существует

        with patch.dict(
            os.environ,
            {
                "DB_NAME": "test_db",
                "DB_USER": "user",
                "DB_PASSWORD": "pass",
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
            },
        ):
            create_database()

        # Проверяем вызовы
        assert mock_connect.call_count == 1
        assert mock_cursor.execute.call_count >= 2
        mock_conn.set_isolation_level.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("src.db.database.psycopg2.connect")
    def test_create_database_already_exists(self, mock_connect):
        """Тест: база данных уже существует"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # БД существует

        with patch.dict(os.environ, {"DB_NAME": "test_db"}):
            create_database()

        # Проверяем, что CREATE DATABASE не вызывался
        calls = [call[0][0] for call in mock_cursor.execute.call_args_list]
        assert not any("CREATE DATABASE" in call for call in calls)

    @patch("src.db.database.psycopg2.connect")
    def test_create_database_error(self, mock_connect):
        """Тест ошибки при создании базы данных"""
        mock_connect.side_effect = psycopg2.Error("Connection error")

        with patch.dict(os.environ, {"DB_NAME": "test_db"}):
            with pytest.raises(psycopg2.Error):
                create_database()

    @patch("src.db.database.psycopg2.connect")
    def test_create_tables_success(self, mock_connect):
        """Тест успешного создания таблиц"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        with patch.dict(os.environ, {"DB_NAME": "test_db"}):
            create_tables()

        # Проверяем вызовы
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

        # Проверяем SQL запрос
        sql = mock_cursor.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS organization" in sql
        assert "CREATE TABLE IF NOT EXISTS vacancies" in sql

    @patch("src.db.database.psycopg2.connect")
    def test_create_tables_error(self, mock_connect):
        """Тест ошибки при создании таблиц"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Table creation error")

        with patch.dict(os.environ, {"DB_NAME": "test_db"}):
            with pytest.raises(psycopg2.Error):
                create_tables()

        # Проверяем rollback
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

    @patch("src.db.database.create_database")
    @patch("src.db.database.create_tables")
    def test_init_database(self, mock_create_tables, mock_create_database):
        """Тест инициализации базы данных"""
        init_database()

        mock_create_database.assert_called_once()
        mock_create_tables.assert_called_once()
