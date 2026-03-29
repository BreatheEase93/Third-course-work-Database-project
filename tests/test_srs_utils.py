from srs.utils import salary_format_translation


class TestSalaryFormatTranslation:

    def test_salary_none(self):
        """Тест: когда зарплата отсутствует (None)"""
        result = salary_format_translation(None)
        assert result == (None, None)

    def test_salary_rub(self):
        """Тест: когда зарплата в рублях"""
        salary_data = {
            'currency': 'RUR',
            'from': 50000,
            'to': 70000
        }

        result = salary_format_translation(salary_data)


        assert result == (60000.0, 'RUR')

    def test_salary_usd(self):
        """Тест: когда зарплата в долларах с конвертацией в рубли"""
        salary_data = {
            'currency': 'USD',
            'from': 1000,
            'to': 1500
        }

        result = salary_format_translation(salary_data)

        assert result == (118750.0, 'RUR')

    def test_salary_eur(self):
        """Дополнительный тест: когда зарплата в евро"""
        salary_data = {
            'currency': 'EUR',
            'from': 2000,
            'to': 3000
        }

        result = salary_format_translation(salary_data)
        assert result == (255000.0, 'RUR')

    def test_salary_only_from(self):
        """Дополнительный тест: только нижняя граница зарплаты"""
        salary_data = {
            'currency': 'RUR',
            'from': 80000,
            'to': None
        }

        result = salary_format_translation(salary_data)
        assert result == (80000.0, 'RUR')

    def test_salary_only_to(self):
        """Дополнительный тест: только верхняя граница зарплаты"""
        salary_data = {
            'currency': 'RUR',
            'from': None,
            'to': 120000
        }

        result = salary_format_translation(salary_data)
        assert result == (120000.0, 'RUR')

    def test_salary_no_range(self):
        """Дополнительный тест: зарплата без указания from и to"""
        salary_data = {
            'currency': 'RUR',
            'from': None,
            'to': None
        }

        result = salary_format_translation(salary_data)
        assert result == (None, 'RUR')