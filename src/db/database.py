import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database():
    """Создает базу данных если она не существует"""
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = conn.cursor()
        db_name = os.getenv("DB_NAME")

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"База данных {db_name} успешно создана")
        else:
            print(f"База данных {db_name} уже существует")

    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def create_tables():
    """Создает таблицы organization и vacancies в базе данных"""
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization (
                id SERIAL PRIMARY KEY,
                company_name VARCHAR(50) NOT NULL UNIQUE,
                employer_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                vacancy_id TEXT UNIQUE,
                company_name VARCHAR(50),
                organization_id INTEGER REFERENCES organization(id) ON DELETE CASCADE,
                vacancy_name TEXT,
                salary FLOAT,
                currency TEXT,
                description TEXT,
                vacancy_url TEXT
            );
        """)

        conn.commit()
        print("Таблицы успешно созданы")

    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def init_database():
    """Инициализация базы данных и таблиц"""
    create_database()
    create_tables()
