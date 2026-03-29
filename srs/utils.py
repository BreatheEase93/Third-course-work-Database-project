from typing import Tuple, Optional


def salary_format_translation(salary: dict, rate_usd: float=95, rate_eur: float=102)-> (
        Tuple)[Optional[float], Optional[str]]:
    """Функция изменения формата полученной зарплаты и перевода в рубли"""
    if salary is None:
        return None, None

    currency = salary.get('currency')
    salary_from = salary.get('from')
    salary_to = salary.get('to')

    if salary_from is not None and salary_to is not None:
        avg_salary = (salary_from + salary_to) / 2
    elif salary_from is not None:
        avg_salary = salary_from
    elif salary_to is not None:
        avg_salary = salary_to
    else:
        return None, currency

    if currency == 'USD':
        avg_salary = avg_salary * rate_usd
        currency = 'RUR'
    elif currency == 'EUR':
        avg_salary = avg_salary * rate_eur
        currency = 'RUR'

    return avg_salary, currency


