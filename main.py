from dotenv import load_dotenv

from src.api.company_parser import get_vacancies
from src.company_list import companies
from src.db.database import init_database
from src.db.db_manager import DBManager
from src.db.vacancy_saver import save_vacancies_to_db

load_dotenv(encoding="utf-8")


def load_vacancies():
    """Сбор вакансий со всех компаний"""
    all_vacancies = []
    print("Сбор вакансий...")

    for company in companies:
        vacancies = get_vacancies(company["employer_id"])
        all_vacancies.extend(vacancies)
        print(f"  {company['name']}: {len(vacancies)} вакансий")

    print(f"Всего собрано: {len(all_vacancies)} вакансий")
    return all_vacancies


def main():
    while True:
        print("\n" + "=" * 50)
        print("1. Инициализация БД")
        print("2. Загрузить вакансии")
        print("3. Компании и кол-во вакансий")
        print("4. Все вакансии")
        print("5. Средняя зарплата")
        print("6. Вакансии с зарплатой выше средней")
        print("7. Поиск по ключевому слову")
        print("0. Выход")

        choice = input("\nВыберите действие: ")

        if choice == "0":
            break

        if choice == "1":
            init_database()
            print("✓ База данных создана")

        elif choice == "2":
            vacancies = load_vacancies()
            if vacancies:
                save_vacancies_to_db(vacancies)

        elif choice in ["3", "4", "5", "6", "7"]:
            try:
                db = DBManager()

                if choice == "3":
                    data = db.get_companies_and_vacancies_count()
                    print("\nКомпании и количество вакансий:")
                    for item in data:
                        print(f"  {item['company_name']}: {item['vacancies_count']}")

                elif choice == "4":
                    data = db.get_all_vacancies()
                    print(f"\nВсего вакансий: {len(data)}")
                    for i, v in enumerate(data[:10], 1):
                        salary = (
                            f"{v['salary']} {v['currency']}"
                            if v["salary"]
                            else "не указана"
                        )
                        print(
                            f"{i}. {v['vacancy_name']} ({v['company_name']}) - "
                            f"{salary} {v['vacancy_url']}"
                        )
                    if len(data) > 10:
                        print(f"... и еще {len(data) - 10}")

                elif choice == "5":
                    avg = db.get_avg_salary()
                    print(f"\nСредняя зарплата: {avg:,.2f} руб.")

                elif choice == "6":
                    data = db.get_vacancies_with_higher_salary()
                    print(f"\nВакансий с зарплатой выше средней: {len(data)}")
                    for i, v in enumerate(data[:10], 1):
                        print(
                            f"{i}. {v['vacancy_name']} - {v['salary']} "
                            f"{v['currency']}. {v['vacancy_url']}"
                        )

                elif choice == "7":
                    keyword = input("Введите ключевое слово: ")
                    data = db.get_vacancies_with_keyword(keyword)
                    print(f"\nНайдено вакансий: {len(data)}")
                    for i, v in enumerate(data[:10], 1):
                        print(
                            f"{i}. {v['vacancy_name']} ({v['company_name']}). "
                            f"{v['vacancy_url']}"
                        )

                db.close()

            except Exception as e:
                print(f"Ошибка: {e}")
                print("Сначала выполните пункт 1 (инициализация БД)")


if __name__ == "__main__":
    main()
