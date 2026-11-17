import yt_dlp
import time
from threading import Thread


class DynamicThreadOptimizer:
    def __init__(self, url, max_threads=16, min_threads=1):
        self.url = url
        self.max_threads = max_threads
        self.min_threads = min_threads
        self.best_threads = min_threads
        self.speed_history = []
        self.stop_optimization = False

    def optimize_threads(self):
        """Оптимизация количества потоков в реальном времени."""
        while not self.stop_optimization:
            time.sleep(2)  # Проверка каждые 2 секунды

            if len(self.speed_history) < 2:
                continue

            # Рассчитываем скорость
            current_speed = self.speed_history[-1]
            previous_speed = self.speed_history[-2]

            # Если скорость упала более чем на 10%, уменьшаем потоки
            if current_speed < previous_speed * 0.9 and self.best_threads > self.min_threads:
                self.best_threads -= 1
                print(f"⏬ Снижаем потоки до {self.best_threads}")
            # Если скорость выросла на 10%, увеличиваем потоки
            elif current_speed > previous_speed * 1.1 and self.best_threads < self.max_threads:
                self.best_threads += 1
                print(f"⏫ Увеличиваем потоки до {self.best_threads}")

    def download_video(self):
        """Функция для загрузки с оптимизацией потоков."""
        # Запускаем оптимизацию в фоновом потоке
        optimizer_thread = Thread(target=self.optimize_threads)
        optimizer_thread.start()

        # Получаем максимальное качество видео и аудио
        format_options = self.get_best_format()

        # Настройки загрузки
        options = {
            'format': format_options,  # Максимальное качество
            'merge_output_format': 'mp4',
            # downloads/<channel>/<playlist>/<title>.mp4; single videos go to "Без плейлиста"
            'outtmpl': 'downloads/%(channel,uploader|Unknown channel)s/%(playlist_title|Без плейлиста)s/%(title)s.%(ext)s',
            'n_threads': self.best_threads,
            'http_chunk_size': 1048576,  # 1 MB
            'fragment_retries': 10,
            'no_check_certificate': True,
            'progress_hooks': [self.progress_hook]
        }

        print(f"🚀 Начинаем загрузку с {self.best_threads} потоками...")

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])
                self.stop_optimization = True  # Останавливаем оптимизацию
                optimizer_thread.join()
                print("✅ Скачивание завершено!")
        except Exception as e:
            self.stop_optimization = True
            optimizer_thread.join()
            print(f"❌ Произошла ошибка: {e}")

    def get_best_format(self):
        """Выбирает максимальное качество видео и аудио."""
        try:
            ydl = yt_dlp.YoutubeDL()
            info = ydl.extract_info(self.url, download=False)

            # Получаем видео в максимальном качестве
            video_format = max(
                (f for f in info['formats'] if f['vcodec'] != 'none'),
                key=lambda x: (x.get('height', 0), x.get('fps', 0))
            )

            # Получаем аудио в лучшем качестве
            audio_format = max(
                (f for f in info['formats'] if f['acodec'] != 'none'),
                key=lambda x: x.get('abr', 0)
            )

            print(f"🎥 Видео: {video_format['format_id']} ({video_format['height']}p)")
            print(f"🎧 Аудио: {audio_format['format_id']} ({audio_format['abr']} kbps)")

            # Возвращаем строку с форматами
            return f"{video_format['format_id']}+{audio_format['format_id']}"
        except Exception as e:
            print(f"❌ Ошибка при выборе формата: {e}")
            return 'bestvideo+bestaudio/best'

    def progress_hook(self, d):
        """Обновление прогресса и скорости."""
        if d['status'] == 'downloading':
            speed_str = d['_speed_str'].strip()
            percent = d['_percent_str'].strip()

            # Конвертируем строку скорости в байты
            speed = self.parse_speed(speed_str)
            self.speed_history.append(speed)

            print(f"[{self.best_threads} потоков] Прогресс: {percent}, Скорость: {speed_str}")

    def parse_speed(self, speed_str):
        """Преобразование скорости в байты."""
        try:
            if 'KiB/s' in speed_str:
                return float(speed_str.replace('KiB/s', '').strip()) * 1024
            elif 'MiB/s' in speed_str:
                return float(speed_str.replace('MiB/s', '').strip()) * 1024 * 1024
            elif 'GiB/s' in speed_str:
                return float(speed_str.replace('GiB/s', '').strip()) * 1024 * 1024 * 1024
            else:
                return 0
        except:
            return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python main.py <URL>")
    else:
        url = sys.argv[1]
        optimizer = DynamicThreadOptimizer(url)
        optimizer.download_video()



### auto threads

# import yt_dlp
# import time
# from threading import Thread
# from queue import Queue


# class DynamicThreadOptimizer:
#     def __init__(self, url, max_threads=16, min_threads=1):
#         self.url = url
#         self.max_threads = max_threads
#         self.min_threads = min_threads
#         self.best_threads = min_threads
#         self.speed_history = []
#         self.last_speed = 0
#         self.stop_optimization = False

#     def optimize_threads(self):
#         """Оптимизация количества потоков во время загрузки."""
#         while not self.stop_optimization:
#             time.sleep(2)  # Проверка каждые 5 секунд

#             if len(self.speed_history) < 2:
#                 continue

#             # Рассчитываем изменение скорости
#             current_speed = self.speed_history[-1]
#             previous_speed = self.speed_history[-2]

#             # Если скорость упала — уменьшаем потоки
#             if current_speed < previous_speed * 0.9 and self.best_threads > self.min_threads:
#                 self.best_threads -= 1
#                 print(f"Снижаем потоки до {self.best_threads}")
#             # Если скорость растет — увеличиваем потоки
#             elif current_speed > previous_speed * 1.1 and self.best_threads < self.max_threads:
#                 self.best_threads += 1
#                 print(f"Увеличиваем потоки до {self.best_threads}")

#     def download_video(self):
#         """Основная функция загрузки с динамической оптимизацией потоков."""
#         # Запускаем оптимизатор в отдельном потоке
#         optimizer_thread = Thread(target=self.optimize_threads)
#         optimizer_thread.start()

#         options = {
#             'format': 'bestvideo+bestaudio/best',
#             'merge_output_format': 'mp4',
#             'outtmpl': '%(title)s.%(ext)s',
#             'n_threads': self.best_threads,
#             'http_chunk_size': 1048576,  # 1 MB
#             'fragment_retries': 10,
#             'no_check_certificate': True,
#             'progress_hooks': [self.progress_hook]
#         }

#         try:
#             with yt_dlp.YoutubeDL(options) as ydl:
#                 ydl.download([self.url])
#                 self.stop_optimization = True  # Останавливаем оптимизатор после завершения
#                 optimizer_thread.join()
#                 print("Скачивание завершено!")
#         except Exception as e:
#             self.stop_optimization = True
#             optimizer_thread.join()
#             print(f"Произошла ошибка: {e}")

#     def progress_hook(self, d):
#         """Обработка прогресса и запись скорости."""
#         if d['status'] == 'downloading':
#             speed_str = d['_speed_str'].strip()
#             percent = d['_percent_str'].strip()

#             # Парсим скорость из строки (в байтах)
#             speed = self.parse_speed(speed_str)
#             self.speed_history.append(speed)

#             print(f"[{self.best_threads} потоков] Прогресс: {percent}, Скорость: {speed_str}")

#     def parse_speed(self, speed_str):
#         """Парсинг скорости из строки (например, '1.23MiB/s')."""
#         try:
#             if 'KiB/s' in speed_str:
#                 return float(speed_str.replace('KiB/s', '').strip()) * 1024
#             elif 'MiB/s' in speed_str:
#                 return float(speed_str.replace('MiB/s', '').strip()) * 1024 * 1024
#             elif 'GiB/s' in speed_str:
#                 return float(speed_str.replace('GiB/s', '').strip()) * 1024 * 1024 * 1024
#             else:
#                 return 0
#         except:
#             return 0


# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 2:
#         print("Использование: python main.py <URL>")
#     else:
#         url = sys.argv[1]
#         optimizer = DynamicThreadOptimizer(url)
#         optimizer.download_video()


### manual threads
# import yt_dlp

# def download_video(url):
#     options = {
#         'format': 'bestvideo+bestaudio/best',
#         'merge_output_format': 'mp4',
#         'outtmpl': '%(title)s.%(ext)s',
#         'n_threads': 29,  # Многопоточный режим
#         'http_chunk_size': 1048576,  # Размер чанков (1MB)
#         'fragment_retries': 10,  # Повторная попытка при сбое
#         'no_check_certificate': True,  # Пропуск проверки сертификатов
#         'progress_hooks': [progress_hook]  # Прогресс-бар
#     }

#     try:
#         with yt_dlp.YoutubeDL(options) as ydl:
#             ydl.download([url])
#             print("Скачивание завершено!")
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")

# def progress_hook(d):
#     if d['status'] == 'downloading':
#         percent = d['_percent_str'].strip()
#         speed = d['_speed_str'].strip()
#         print(f"Прогресс: {percent}, Скорость: {speed}")

# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 2:
#         print("Использование: python main.py <URL>")
#     else:
#         download_video(sys.argv[1])


