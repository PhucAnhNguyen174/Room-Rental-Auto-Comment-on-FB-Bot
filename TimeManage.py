from datetime import datetime, timedelta
import time
import random
from pynput.keyboard import Key, Controller

keyboard = Controller()


def is_valid_time():
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    valid_ranges = [
        (8, 00, 11, 00),  # Ca 1: 08:30 - 11:30
        (11, 00, 18, 30),  # Ca 2: 14:30 - 16:30
        (18, 00, 23, 59),  # Ca 3: 19:30 - 23:59
        (0, 0, 0, 30),  # Ca 4: 00:00 - 00:30
    ]

    for start_h, start_m, end_h, end_m in valid_ranges:
        start = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        end = now.replace(hour=end_h, minute=end_m, second=59, microsecond=0)

        if start <= now <= end:
            return True, 0  # Thời gian hợp lệ

    # Nếu không trong khoảng hợp lệ, tìm thời gian bắt đầu ca làm gần nhất trong tương lai
    future_starts = []
    for start_h, start_m, _, _ in valid_ranges:
        start_time = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        if start_time < now:
            start_time += timedelta(days=1)  # Nếu giờ đã qua, tính sang hôm sau
        future_starts.append(start_time)

    # Tìm thời điểm gần nhất
    next_start = min(future_starts)
    wait_seconds = int((next_start - now).total_seconds())

    # Thêm ngẫu nhiên ±10 phút (tối đa ±600 giây)
    jitter = random.randint(-600, 600)
    final_wait = max(0, wait_seconds + jitter)

    return False, final_wait


def time_counter(time_sleep):
    a = 0  # Đếm thời gian để ấn Shift

    while time_sleep > 0:
        if time_sleep > 60:
            minutes_left = time_sleep // 60
            print(f"Còn khoảng {minutes_left} phút trước khi chương trình chạy")
            time.sleep(60)
            time_sleep -= 60
            a += 60
        else:
            print(f"Còn {time_sleep} giây trước khi chương trình chạy")
            time.sleep(1)
            time_sleep -= 1
            a += 1

        if a >= 180:
            keyboard.press(Key.shift)
            keyboard.release(Key.shift)
            print(">>> Đã nhấn Shift để giữ máy tỉnh <<<")
            a = 0


def wait_for_valid_time():
    """Chờ đến thời điểm hợp lệ mới chạy chương trình"""
    is_valid, wait_time = is_valid_time()
    if is_valid:
        print("Thời gian hợp lệ, tiếp tục chương trình.")
    else:
        minutes = wait_time // 60
        seconds = wait_time % 60
        print(f"Chưa tới ca làm. Sẽ đợi khoảng {minutes} phút {seconds} giây (đã bao gồm ±10 phút ngẫu nhiên)...")
        time_counter(wait_time)
        print("Đã đến giờ hợp lệ, tiếp tục chương trình.")
