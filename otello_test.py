# Пример использования
import time
from otello_requests import get_id_for_hotels_by_suggest


if __name__ == "__main__":
    # Тест 1: только название
    search_query_1 = "Seven hills"
    print(f"\n=== Поиск: '{search_query_1}' ===")
    hotel_result_1 = get_id_for_hotels_by_suggest(search_query_1)

    if hotel_result_1:
        print(f"ID: {hotel_result_1.get('id')}")
        print(f"Название: {hotel_result_1.get('name')}")
        print(f"Адрес: {hotel_result_1.get('address', {}).get('name')}")
        print(f"Город: {hotel_result_1.get('address', {}).get('city')}")

    time.sleep(2)
    # Тест 2: название с адресом
    search_query_2 = "Seven Hills Оружейный, 3"
    print(f"\n=== Поиск: '{search_query_2}' ===")
    hotel_result_2 = get_id_for_hotels_by_suggest(search_query_2)

    if hotel_result_2:
        print(f"ID: {hotel_result_2.get('id')}")
        print(f"Название: {hotel_result_2.get('name')}")
        print(f"Адрес: {hotel_result_2.get('address', {}).get('name')}")
        print(f"Город: {hotel_result_2.get('address', {}).get('city')}")