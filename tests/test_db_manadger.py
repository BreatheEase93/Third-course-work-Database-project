from unittest.mock import MagicMock, patch

import pytest

from src.db.db_manager import DBManager


class TestDBManager:
    """Тесты для DBManager"""

    @patch("src.db.db_manager.psycopg2.connect")
    def test_init_and_connect_success(self, mock_connect):
        """Тест успешного подключения"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        db = DBManager()

        mock_connect.assert_called_once()
        assert db.conn == mock_conn

    @patch("src.db.db_manager.psycopg2.connect")
    def test_init_connect_error(self, mock_connect):
        """Тест ошибки подключения"""
        import psycopg2  # Локальный импорт на случай ошибки

        mock_connect.side_effect = psycopg2.Error("Connection failed")

        with pytest.raises(psycopg2.Error):
            DBManager()

    @patch("src.db.db_manager.psycopg2.connect")
    def test_execute_query_success(self, mock_connect):
        """Тест успешного выполнения запроса"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, "Test")]

        db = DBManager()
        result = db._execute_query("SELECT * FROM test")

        mock_cursor.execute.assert_called_once()
        assert result == [(1, "Test")]

    @patch("src.db.db_manager.psycopg2.connect")
    def test_execute_query_error(self, mock_connect):
        """Тест ошибки выполнения запроса"""
        import psycopg2  # Локальный импорт на случай ошибки

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query error")

        db = DBManager()

        with pytest.raises(psycopg2.Error):
            db._execute_query("SELECT * FROM test")

    @patch("src.db.db_manager.psycopg2.connect")
    def test_get_companies_and_vacancies_count(self, mock_connect):
        """Тест получения компаний и количества вакансий"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Company1", 10), ("Company2", 5)]

        db = DBManager()
        result = db.get_companies_and_vacancies_count()

        assert len(result) == 2
        assert result[0]["company_name"] == "Company1"
        assert result[0]["vacancies_count"] == 10

    @patch("src.db.db_manager.psycopg2.connect")
    def test_get_all_vacancies(self, mock_connect):
        """Тест получения всех вакансий"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Company", "Python Dev", 100000, "RUR", "http://test.com")
        ]

        db = DBManager()
        result = db.get_all_vacancies()

        assert len(result) == 1
        assert result[0]["vacancy_name"] == "Python Dev"
        assert result[0]["salary"] == 100000

    @patch("src.db.db_manager.psycopg2.connect")
    def test_get_avg_salary_with_data(self, mock_connect):
        """Тест получения средней зарплаты (есть данные)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(75000.00,)]

        db = DBManager()
        result = db.get_avg_salary()

        assert result == 75000.00

    @patch("src.db.db_manager.psycopg2.connect")
    def test_get_avg_salary_no_data(self, mock_connect):
        """Тест получения средней зарплаты (нет данных)"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(None,)]

        db = DBManager()
        result = db.get_avg_salary()

        assert result == 0.0

    @patch("src.db.db_manager.psycopg2.connect")
    def test_get_vacancies_with_higher_salary(self, mock_connect):
        """Тест получения вакансий с зарплатой выше средней"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Company", "Senior Dev", 150000, "RUR", "http://test.com")
        ]

        db = DBManager()
        result = db.get_vacancies_with_higher_salary()

        assert len(result) == 1
        assert result[0]["salary"] == 150000

    @patch("src.db.db_manager.psycopg2.connect")
    def test_get_vacancies_with_keyword(self, mock_connect):
        """Тест поиска вакансий по ключевому слову"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Company", "Python Developer", 100000, "RUR", "http://test.com")
        ]

        db = DBManager()
        result = db.get_vacancies_with_keyword("Python")

        assert len(result) == 1
        assert "Python" in result[0]["vacancy_name"]

    @patch("src.db.db_manager.psycopg2.connect")
    def test_close_connection(self, mock_connect):
        """Тест закрытия соединения"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        db = DBManager()
        db.close()

        mock_conn.close.assert_called_once()

    @patch("src.db.db_manager.psycopg2.connect")
    def test_context_manager(self, mock_connect):
        """Тест работы с контекстным менеджером"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        db = DBManager()

        try:
            assert db.conn == mock_conn
        finally:
            db.close()

        mock_conn.close.assert_called_once()
