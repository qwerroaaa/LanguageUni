import http.client
import os
import threading
import time
import urllib.parse
import sys

class FileDownloader:
    def __init__(self, url):
        self.url = url
        self.received_bytes = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def download(self):
        try:
           while True:
                # Парсинг URL
                parsed_url = urllib.parse.urlparse(self.url)
                print(f"Parsed URL: {parsed_url}")

                connection = http.client.HTTPSConnection(parsed_url.netloc)  # Используем HTTPS
                print(f"Connecting to: {parsed_url.netloc}")
                headers = {"User-Agent": "Python Downloader"}
                connection.request("GET", parsed_url.path, headers=headers)
                response = connection.getresponse()
                print(f"Response status: {response.status} {response.reason}")

                # Обработка редиректа (301 или 302)
                if response.status in (301, 302):
                    new_url = response.getheader("Location")
                    print(f"Redirecting to {new_url}")
                    self.url = new_url  # Обновляем URL и повторяем цикл
                    connection.close()
                    continue  # Переходим на следующий цикл для скачивания по новому URL

                if response.status != 200:
                    print(f"Error: {response.status} {response.reason}")
                    return

                # Получение имени файла
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = "downloaded_file"
                print(f"Saving file as: {filename}")

                # Запись данных в файл
                with open(filename, "wb") as file:
                    while not self.stop_event.is_set():
                        chunk = response.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                        with self.lock:
                            self.received_bytes += len(chunk)

                connection.close()
                self.stop_event.set()
                print(f"Download complete: {filename}")
                break  # Завершаем цикл после успешного скачивания
        except Exception as e:
            print(f"Error occurred: {e}")

    def print_progress(self):
        while not self.stop_event.is_set():
            time.sleep(1)
            with self.lock:
                print(f"Downloaded: {self.received_bytes} bytes")

def main():
    # Запрос URL у пользователя
    #url = input("Введите URL файла для скачивания: ").strip()
    #if not url:
        #print("URL не может быть пустым.")
        #return
    # Проверка аргументов командной строки
    if len(sys.argv) < 2:
        print("Usage: py Lab1.py <URL>")
        return

    url = sys.argv[1]  # URL из аргументов командной строки
    print(f"Downloading from: {url}")
    downloader = FileDownloader(url)

    # Поток для скачивания
    download_thread = threading.Thread(target=downloader.download)
    download_thread.start()

    # Поток для отображения прогресса
    progress_thread = threading.Thread(target=downloader.print_progress)
    progress_thread.start()

    # Ожидание завершения скачивания
    download_thread.join()
    downloader.stop_event.set()
    progress_thread.join()

    print("Download complete.")

if __name__ == "__main__":
    main()
