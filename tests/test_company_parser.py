from unittest.mock import Mock, patch

from src.api.company_parser import get_vacancies


def test_get_vacancies_success():
    """Тест успешного получения вакансий"""
    with patch("src.api.company_parser.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": "1", "name": "Python Developer"},
                {"id": "2", "name": "Java Developer"},
            ],
            "pages": 1,  # Добавьте это поле
        }
        mock_get.return_value = mock_response

        result = get_vacancies(123)

        assert len(result) == 2
        assert result[0]["name"] == "Python Developer"
        assert result[1]["name"] == "Java Developer"


def test_get_vacancies_http_error():
    """Тест обработки HTTP ошибки"""
    with patch("src.api.company_parser.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = get_vacancies(123)

        assert result == []


def test_get_vacancies_json_error():
    """Тест обработки ошибки JSON"""
    with patch("src.api.company_parser.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = get_vacancies(123)

        assert result == []


def test_get_vacancies_empty_response():
    """Тест пустого ответа от API"""
    with patch("src.api.company_parser.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "pages": 1}
        mock_get.return_value = mock_response

        result = get_vacancies(123)

        assert result == []
