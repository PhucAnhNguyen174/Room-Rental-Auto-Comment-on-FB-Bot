# Các hàm thực hiện việc giả lập hành vi cuộn bài đăng trong Facebook


import time
import random
import pyautogui
from pynput.mouse import Controller


class Scrolling:
    def __init__(self):
        self.mouse = Controller()

    def fast_scroll_down_simulation(self, step_delay=0.02):
        offset = random.uniform(0.001, 0.005)  # Thêm độ ngẫu nhiên vào time.sleep
        steps = random.choice([4] * 35 + [5] * 30 + [6] * 25 + [7] * 10)
        print(f"Đang cuộn nhanh xuống với {steps} bước, mỗi bước dừng {step_delay:.2f} giây...")

        for _ in range(steps):
            try:
                self.mouse.scroll(0, -1)
            except Exception as e:
                print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(-1)")
                pyautogui.scroll(-1)
            time.sleep(step_delay + offset)

    def slow_scroll_down_simulation(self):
        scroll_type = random.choice([1, 2, 3])
        offset_1 = random.uniform(0.001, 0.005)
        offset_2 = random.uniform(0.001, 0.01)
        # print(f"Lựa chọn random: {scroll_type}\n")

        if scroll_type == 1:
            # print("Type 1: Lướt đều 3 khấc, mỗi lần nghỉ 0.022 giây...")
            for _ in range(3):
                try:
                    self.mouse.scroll(0, -1)
                except Exception as e:
                    print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(-1)")
                    pyautogui.scroll(-1)
                time.sleep(0.022 + offset_1)

        elif scroll_type == 2:
            # print("Type 2: Lướt 2 khấc liên tiếp, mỗi lần nghỉ 0.022 giây...")
            for _ in range(2):
                try:
                    self.mouse.scroll(0, -1)
                except Exception as e:
                    print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(-1)")
                    pyautogui.scroll(-1)
                time.sleep(0.022 + offset_1)

        elif scroll_type == 3:
            # print("Type 3: Lướt 3 khấc, 2 khấc đầu nghỉ 0.02 giây, khấc cuối nghỉ 0.045 giây...")
            for i in range(3):
                try:
                    self.mouse.scroll(0, -1)
                except Exception as e:
                    print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(-1)")
                    pyautogui.scroll(-1)

                if i < 2:
                    time.sleep(0.02 + offset_1)
                else:
                    time.sleep(0.045 + offset_2)

    def slow_scroll_up_simulation(self):
        scroll_type = random.choice([1, 2, 3])
        offset_1 = random.uniform(0.001, 0.005)
        offset_2 = random.uniform(0.001, 0.01)
        # print(f"Lựa chọn random: {scroll_type}\n")

        if scroll_type == 1:
            # print("Type 1: Lướt đều 3 khấc, mỗi lần nghỉ 0.022 giây...")
            for _ in range(3):
                try:
                    self.mouse.scroll(0, 1)
                except Exception as e:
                    print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(1)")
                    pyautogui.scroll(1)
                time.sleep(0.022 + offset_1)

        elif scroll_type == 2:
            # print("Type 2: Lướt 2 khấc liên tiếp, mỗi lần nghỉ 0.022 giây...")
            for _ in range(2):
                try:
                    self.mouse.scroll(0, 1)
                except Exception as e:
                    print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(1)")
                    pyautogui.scroll(1)
                time.sleep(0.022 + offset_1)

        elif scroll_type == 3:
            # print("Type 3: Lướt 3 khấc, 2 khấc đầu nghỉ 0.02 giây, khấc cuối nghỉ 0.045 giây...")
            for i in range(3):
                try:
                    self.mouse.scroll(0, 1)
                except Exception as e:
                    print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(1)")
                    pyautogui.scroll(1)
                if i < 2:
                    time.sleep(0.02 + offset_1)
                else:
                    time.sleep(0.045 + offset_2)

    def scroll_up_one_time(self):
        try:
            self.mouse.scroll(0, 1)
        except Exception as e:
            print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(1)")
            pyautogui.scroll(1)

    def scroll_down_one_time(self):
        try:
            self.mouse.scroll(0, -1)
        except Exception as e:
            print(f"[Fallback] pynput.scroll lỗi: {e} -> dùng pyautogui.scroll(-1)")
            pyautogui.scroll(-1)
