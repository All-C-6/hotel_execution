import requests
from datetime import date
from difflib import SequenceMatcher
import time
import json


authorization_token: str = "31fd3cf62fe0d5635076d44c1f6e8b4575a076a8"
request_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip",
    "Authorization": f"Bearer {authorization_token}",
    "Origin": "https://otello.ru",
    "Priority": "u=1, i",
    "Referer": "https://otello.ru/",
    "Sec-Ch-Ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Linux"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "X-Otello-Ab-Test": "inspirationReels=reels_2",
    "X-Otello-Platform": "other_web"
}


def get_otello_hotel_rooms(
    hotel_id: str,
    checkin_date: date,
    checkout_date: date,
    adults_count: int = 1,
    children_ages: list[int] = None
) -> dict:
    """
    Получает информацию о доступных номерах отеля через API Otello.

    Args:
        hotel_id: ID отеля в системе 2GIS/otello (например, "70000001021834036")
        checkin_date: Дата заезда
        checkout_date: Дата выезда
        adults_count: Количество взрослых (по умолчанию 1)
        children_ages: Список возрастов детей (по умолчанию пустой)

    Returns:
        Словарь с JSON ответом от API

    Raises:
        requests.exceptions.RequestException: При ошибке HTTP запроса
    """

    base_url = "https://otello.api.2gis.com/api/v2/properties"

    # Формируем URL эндпоинта
    endpoint_url = f"{base_url}/{hotel_id}/offers"

    # Подготавливаем параметры гостей
    if children_ages is None:
        children_ages = []

    guest_groups = [
        {
            "adults": adults_count,
            "children": children_ages
        }
    ]

    # Параметры запроса
    query_parameters = {
        "checkin_date": checkin_date.strftime("%Y-%m-%d"),
        "checkout_date": checkout_date.strftime("%Y-%m-%d"),
        "guest_groups": json.dumps(guest_groups)
    }

    # Заголовки запроса (БЕЗ Accept-Encoding - requests сам разберется)


    # Отправляем GET запрос
    response = requests.get(
        endpoint_url,
        params=query_parameters,
        headers=request_headers,
        timeout=30
    )

    # Проверяем статус ответа
    response.raise_for_status()

    # Возвращаем JSON ответ
    return response.json()


def get_id_for_hotels_by_suggest(search_text: str) -> dict | None:
    """
    Ищет отель через API 2GIS по текстовому запросу.

    Отправляет запрос к API suggest для поиска отелей и городов,
    затем находит наиболее похожее название среди результатов
    на основе текстового сходства. При сравнении учитывается как
    название отеля, так и его адрес.

    Args:
        search_text: Текст для поиска отеля (название, название с адресом)

    Returns:
        dict: Словарь с данными найденного отеля (item из списка items)
              или None, если ничего не найдено или произошла ошибка

    Example:
        >>> hotel_data = get_id_for_hotels_by_suggest("Seven hills")
        >>> if hotel_data:
        ...     print(hotel_data['name'])
        ...     print(hotel_data['id'])
        >>> 
        >>> hotel_data = get_id_for_hotels_by_suggest("Seven Hills Пестовский, 3")
        >>> if hotel_data:
        ...     print(hotel_data['name'])
        ...     print(hotel_data['address']['name'])
    """
    api_url = "https://otello.api.2gis.com/api/v2/suggest/destination"

    request_parameters = {
        "nCities": 3,
        "nHotels": 27,
        "q": search_text,
        "targeting_user_location_id": "1548735142166607"
    }

    try:
        response = requests.get(api_url, params=request_parameters, timeout=10)
        response.raise_for_status()

        response_data = response.json()

        # Проверяем успешность ответа
        if response_data.get("meta", {}).get("code") != 200:
            print(f"API вернул код ошибки: {response_data.get('meta', {})}")
            return None

        items_list = response_data.get("result", {}).get("items", [])

        if not items_list:
            print(f"Не найдено результатов для запроса: '{search_text}'")
            return None

        # Находим наиболее похожее название (с учетом адреса)
        best_match_item = None
        highest_similarity_ratio = 0.0

        search_text_normalized = search_text.lower().strip()

        for current_item in items_list:
            item_name = current_item.get("name", "")
            item_address = current_item.get("address", {}).get("name", "")
            item_city = current_item.get("address", {}).get("city", "")

            # Формируем комбинированную строку: название + адрес
            item_full_text = f"{item_name} {item_address}".lower().strip()

            # Также формируем вариант с городом
            item_full_text_with_city = f"{item_name} {item_address} {item_city}".lower().strip()

            # Вычисляем коэффициент схожести для разных комбинаций
            similarity_ratio_full = SequenceMatcher(
                None, 
                search_text_normalized, 
                item_full_text
            ).ratio()

            similarity_ratio_with_city = SequenceMatcher(
                None, 
                search_text_normalized, 
                item_full_text_with_city
            ).ratio()

            # Также проверяем схожесть только по названию
            similarity_ratio_name_only = SequenceMatcher(
                None, 
                search_text_normalized, 
                item_name.lower().strip()
            ).ratio()

            # Берем максимальную схожесть из всех вариантов
            max_similarity_ratio = max(
                similarity_ratio_full,
                similarity_ratio_with_city,
                similarity_ratio_name_only
            )

            if max_similarity_ratio > highest_similarity_ratio:
                highest_similarity_ratio = max_similarity_ratio
                best_match_item = current_item

        if best_match_item:
            best_match_name = best_match_item.get('name', '')
            best_match_address = best_match_item.get('address', {}).get('name', '')
            print(f"Найден отель: '{best_match_name}', адрес: '{best_match_address}' "
                  f"(схожесть: {highest_similarity_ratio:.2%})")
            return best_match_item
        else:
            print("Не удалось найти подходящий результат")
            return None

    except requests.exceptions.Timeout:
        print(f"Превышено время ожидания ответа от API")
        return None
    except requests.exceptions.RequestException as request_error:
        print(f"Ошибка при выполнении запроса: {request_error}")
        return None
    except ValueError as json_error:
        print(f"Ошибка при разборе JSON ответа: {json_error}")
        return None
    except Exception as unexpected_error:
        print(f"Неожиданная ошибка: {unexpected_error}")
        return None
