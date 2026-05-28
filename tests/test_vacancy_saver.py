from unittest.mock import MagicMock, patch

import psycopg2

from src.db.vacancy_saver import save_vacancies_to_db


class TestVacancySaver:
    """Тесты для сохранения вакансий"""

    @patch("src.db.vacancy_saver.psycopg2.connect")
    def test_save_vacancies_success(self, mock_connect):
        """Тест успешного сохранения вакансий"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = [1]  # organization_id

        vacancies_data = [
            {
                "id": 123,
                "name": "Python Developer",
                "employer": {"id": 456, "name": "Test Company"},
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                "description": "Test description",
                "alternate_url": "https://test.com/123",
            }
        ]

        save_vacancies_to_db(vacancies_data)

        assert mock_cursor.execute.call_count >= 2
        mock_conn.commit.assert_called_once()

    @patch("src.db.vacancy_saver.psycopg2.connect")
    def test_save_vacancies_empty_list(self, mock_connect):
        """Тест сохранения пустого списка"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        save_vacancies_to_db([])

        mock_conn.commit.assert_called_once()

    @patch("src.db.vacancy_saver.psycopg2.connect")
    def test_save_vacancies_without_salary(self, mock_connect):
        """Тест сохранения вакансии без зарплаты"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]

        vacancies_data = [
            {
                "id": 124,
                "name": "Junior Developer",
                "employer": {"id": 457, "name": "Another Company"},
                "salary": None,
                "description": "Test",
                "alternate_url": "https://test.com/124",
            }
        ]

        save_vacancies_to_db(vacancies_data)

        mock_conn.commit.assert_called_once()

    @patch("src.db.vacancy_saver.psycopg2.connect")
    def test_save_vacancies_db_error(self, mock_connect):
        """Тест ошибки при сохранении"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Симулируем ошибку при execute
        mock_cursor.execute.side_effect = psycopg2.Error("DB Error")

        vacancies_data = [
            {"id": 125, "name": "Test", "employer": {"id": 458, "name": "Test Company"}}
        ]

        # Функция не выбрасывает исключение, а просто печатает ошибку
        save_vacancies_to_db(vacancies_data)

        # Проверяем, что был rollback
        mock_conn.rollback.assert_called_once()
        # Проверяем, что commit НЕ вызывался
        mock_conn.commit.assert_not_called()
