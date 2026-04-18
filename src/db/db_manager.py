import os
from typing import Any, Dict, List, Optional

import psycopg2


class DBManager:
    """Класс для работы с базой данных вакансий"""

    def __init__(self):
        """Инициализация подключения к базе данных"""
        self.conn = None
        self._connect()

    def _connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
        except psycopg2.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def _execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Выполняет SQL запрос и возвращает результат"""
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        query = """
            SELECT
                o.company_name,
                COUNT(v.id) as vacancies_count
            FROM organization o
            LEFT JOIN vacancies v ON o.id = v.organization_id
            GROUP BY o.id, o.company_name
            ORDER BY vacancies_count DESC;
        """

        result = self._execute_query(query)

        return [{"company_name": row[0], "vacancies_count": row[1]} for row in result]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию."""
        query = """
            SELECT
                v.company_name,
                v.vacancy_name,
                v.salary,
                v.currency,
                v.vacancy_url
            FROM vacancies v
            ORDER BY v.company_name, v.vacancy_name;
        """

        result = self._execute_query(query)

        return [
            {
                "company_name": row[0],
                "vacancy_name": row[1],
                "salary": row[2],
                "currency": row[3],
                "vacancy_url": row[4],
            }
            for row in result
        ]

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям."""
        query = """
            SELECT
                ROUND(AVG(salary)::numeric, 2) as avg_salary
            FROM vacancies
            WHERE salary IS NOT NULL;
        """

        result = self._execute_query(query)
        avg_salary = float(result[0][0]) if result and result[0][0] else 0.0

        return avg_salary

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получает список всех вакансий,
        у которых зарплата выше средней по всем вакансиям."""
        query = """
            WITH avg_salary_cte AS (
                SELECT AVG(salary) as avg_salary
                FROM vacancies
                WHERE salary IS NOT NULL
            )
            SELECT
                v.company_name,
                v.vacancy_name,
                v.salary,
                v.currency,
                v.vacancy_url
            FROM vacancies v
            CROSS JOIN avg_salary_cte a
            WHERE v.salary > a.avg_salary
            ORDER BY v.salary DESC;
        """

        result = self._execute_query(query)

        return [
            {
                "company_name": row[0],
                "vacancy_name": row[1],
                "salary": row[2],
                "currency": row[3],
                "vacancy_url": row[4],
            }
            for row in result
        ]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получает список всех вакансий,
        в названии которых содержится переданное слово."""
        query = """
            SELECT
                v.company_name,
                v.vacancy_name,
                v.salary,
                v.currency,
                v.vacancy_url
            FROM vacancies v
            WHERE LOWER(v.vacancy_name) LIKE LOWER(%s)
            ORDER BY v.company_name, v.vacancy_name;
        """

        search_pattern = f"%{keyword}%"
        result = self._execute_query(query, (search_pattern,))

        return [
            {
                "company_name": row[0],
                "vacancy_name": row[1],
                "salary": row[2],
                "currency": row[3],
                "vacancy_url": row[4],
            }
            for row in result
        ]

    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие соединения при выходе из контекста"""
        self.close()
