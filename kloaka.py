import aiohttp
import asyncio
import time
from random import randint, choice
from aiohttp import ClientSession, ClientTimeout
from urllib.parse import urljoin

# Список User-Agent'ов для обхода блокировок
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
]

# Функция для асинхронного запроса
async def make_request(session, url):
    try:
        headers = {'User-Agent': choice(USER_AGENTS)}
        timeout = ClientTimeout(total=10, connect=10)  # Тайм-аут для соединения и ответа

        # Выполняем запрос
        async with session.get(url, headers=headers, timeout=timeout, ssl=False) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Ошибка при обработке сайта {url}: {response.status}")
                return None
    except asyncio.TimeoutError:
        print(f"Тайм-аут при подключении к {url}")
    except aiohttp.ClientError as e:
        print(f"Ошибка клиента при подключении к {url}: {str(e)}")
    except Exception as e:
        print(f"Неизвестная ошибка при подключении к {url}: {str(e)}")
    return None

# Функция для использования прокси, если нужно
async def fetch_with_proxy(session, url, proxy=None):
    try:
        headers = {'User-Agent': choice(USER_AGENTS)}
        timeout = ClientTimeout(total=10, connect=10)  # Тайм-аут для соединения и ответа

        # Прокси можно передавать, если это необходимо
        async with session.get(url, headers=headers, timeout=timeout, ssl=False, proxy=proxy) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Ошибка при обработке сайта {url}: {response.status}")
                return None
    except Exception as e:
        print(f"Ошибка при подключении к {url} с прокси: {str(e)}")
    return None

# Основная функция для обработки сайтов
async def process_sites(urls, proxies=None):
    async with aiohttp.ClientSession() as session:
        for url in urls:
            # Если указан прокси, будем использовать его
            if proxies:
                html_content = await fetch_with_proxy(session, url, proxy=proxies)
            else:
                html_content = await make_request(session, url)

            if html_content:
                print(f"Успешно обработан сайт: {url}")
            else:
                print(f"Не удалось подключиться к сайту: {url}")

            # Задержка между запросами для предотвращения блокировки
            time.sleep(randint(1, 3))  # Случайная задержка от 1 до 3 секунд

# Пример списка сайтов
urls = [
    "https://example.com",
    "https://anotherexample.com",
    "https://nonexistentwebsite.com"
]

# Пример прокси (если нужно)
proxies = "http://your_proxy:your_port"

# Запуск асинхронного процесса
asyncio.run(process_sites(urls, proxies))
