from typing import Any, Dict, List

import requests


def get_vacancies(employer_id: int) -> List:
    """Функция получает на вход ID компании, а возвращает список,
    определённых доступных вакансий связанных с IT"""
    all_vacancies = []
    page = 0
    per_page = 100

    while True:
        params: Dict[str, Any] = {
            "employer_id": employer_id,
            "professional_role": [
                10,
                73,
                83,
                96,
                104,
                107,
                112,
                113,
                114,
                124,
                125,
                148,
                150,
                156,
                157,
                158,
                160,
                164,
                165,
            ],
            "per_page": per_page,
            "page": page,
        }
        try:
            response = requests.get("https://api.hh.ru/vacancies", params=params)
            if response.status_code == 200:
                data = response.json()

                items = data.get("items", [])
                all_vacancies.extend(items)

                if len(items) < per_page:
                    break
                page += 1

                if page > 20:
                    break
            else:
                print(f"Неожиданный код ответа: {response.status_code}")
                break
        except ValueError as e:
            print(f"Ошибка при разборе JSON ответа: {e}")
            break

    return all_vacancies


vacancies = get_vacancies(1740)

print(f"Найдено вакансий: {len(vacancies)}")

print("\nПервые 10 вакансий:")
for i, vac in enumerate(vacancies[:10], 1):
    print(f"{i}. {vac.get('name', 'Название не указано')}")
    print(f"   Зарплата: {vac.get('salary', 'Не указана')}")
    print(f"   URL: {vac.get('alternate_url', 'Нет ссылки')}")
    print()
