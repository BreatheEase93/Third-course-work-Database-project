import os
from typing import List

import psycopg2

from srs.utils import salary_format_translation


def save_vacancies_to_db(vacancies_data: List) -> None:
    """Сохраняет данные о вакансиях в базу данных"""
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )

        cursor = conn.cursor()

        for vacancy in vacancies_data:
            employer = vacancy.get('employer', {})
            employer_id = employer.get('id')
            company_name = employer.get('name')

            cursor.execute("""
                INSERT INTO organization (company_name, employer_id)
                VALUES (%s, %s)
                ON CONFLICT (company_name) DO UPDATE 
                SET employer_id = EXCLUDED.employer_id
                RETURNING id
            """, (company_name, employer_id))

            organization_id = cursor.fetchone()[0]

            vacancy_id = str(vacancy.get('id'))
            vacancy_name = vacancy.get('name')
            salary = vacancy.get('salary')
            new_salary, currency = salary_format_translation(salary)
            description = vacancy.get('description')
            vacancy_url = vacancy.get('alternate_url')

            cursor.execute("""
                INSERT INTO vacancies (
                    vacancy_id, company_name, organization_id, 
                    vacancy_name, salary, currency, description, vacancy_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO NOTHING
            """, (vacancy_id, company_name, organization_id,
                  vacancy_name, new_salary, currency, description, vacancy_url))

        conn.commit()
        print(f"Успешно сохранено {len(vacancies_data)} вакансий")

    except psycopg2.Error as e:
        print(f"Ошибка при сохранении данных: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()