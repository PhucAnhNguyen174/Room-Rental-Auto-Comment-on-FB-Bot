import numpy as np
import time
from scipy.special import comb
from pynput.mouse import Controller
import math
import random


class MouseMover:
    def __init__(self):
        self.mouse = Controller()

    @staticmethod
    # Tạo đường cong Bézier Curve
    def bezier_curve(control_points, n=100):
        def bernstein_poly(i, n, t):
            return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

        n_points = len(control_points) - 1
        t_values = np.linspace(0, 1, n)
        curve = np.zeros((n, 2))

        for i in range(n_points + 1):
            curve += np.outer(bernstein_poly(i, n_points, t_values), control_points[i])
        return curve

    @staticmethod
    def apply_gaussian_noise(points, scale=1.0, frequency=1.0):
        # Tạo nhiễu Gaussian với tần suất điều chỉnh
        if random.random() < frequency:
            noise = np.random.normal(0, scale, points.shape)
            points += noise
        return points

    @staticmethod
    def fitts_law_total_time(distance, size, a=0.1, b=0.05):
        # Áp dụng Fitt's Law để tính tổng thời gian di chuyển từ vị trí ban đầu đến mục tiêu
        total_time = a + b * np.log2(distance / size + 1)
        return total_time

    def move_mouse(self, start, end, control_points=None, size=10, noise_scale=0.8, noise_frequency=1.0):
        scale = 0.01  # Độ cong cuả Bézier Curve, scale càng lớn thì càng cong

        # Tính toán khoảng cách và số bước di chuyển
        distance = np.linalg.norm(np.array(end) - np.array(start))
        num_steps = max(math.ceil(distance / 5), 10) # Tối thiểu 10 bước để đảm bảo di chuyển mượt

        # Tạo điểm kết thúc ảo với xác suất nhất định nhằm giả lập hành vi ngẫu nhiên người dùng lỡ di chuyển quá và từ từ điều chỉnh lại
        deviation_prob = 0 if size >= 75 or distance <= 189 else min(0.85, (1 - size / 75) * (distance / 800))
        has_fake_end = random.random() < deviation_prob

        if has_fake_end:
            angle = random.uniform(0, 2 * math.pi) # Chọn góc ngẫu nhiên để đặt fake end
            deviation_distance = random.uniform(5, min(distance / 10, 50)) # Giới hạn độ lệch
            fake_end = (end[0] + deviation_distance * math.cos(angle),
                        end[1] + deviation_distance * math.sin(angle))
            b_fake = 0.05  # Giá trị b khi có fake end để tăng tốc độ (b càng nhỏ di tốc độ di chuển càng nhanh)
        else:
            fake_end = None
            b_fake = 0.05  # Giữ nguyên giá trị b khi không có fake end (b càng nhỏ di tốc độ di chuển càng nhanh)

        # Tạo điểm kiểm soát
        if control_points is None:
            offset = distance * scale
            control_points = [
                start,
                ((start[0] + end[0]) // 2, start[1] - offset),
                end
            ]
        else:
            control_points.append(end)

        control_points = [start]
        if fake_end:
            control_points.append(((start[0] + fake_end[0]) // 2, start[1] - distance * scale))
            control_points.append(fake_end)
        else:
            control_points.append(((start[0] + end[0]) // 2, start[1] - distance * scale))
            control_points.append(end)

        # Tạo đường cong Bézier từ các điểm điều khiển
        curve_points = self.bezier_curve(np.array(control_points), n=num_steps)
        curve_points = self.apply_gaussian_noise(curve_points, scale=noise_scale, frequency=noise_frequency)

        total_time = self.fitts_law_total_time(distance, size, b=b_fake)

        # Tính toán phân phối thời gian theo từng bước di chuyển bằng hàm toán học f(x) = sqrt(0.8 * (1 - (a - 0.6) ** 2 / 2.3))
        num = np.zeros((num_steps, 2))
        temp = 0
        for i in range(1, num_steps + 1):
            a = i * (2 / num_steps)
            temp += 1 / math.sqrt(0.8 * (1 - (a - 0.6) ** 2 / 2.3))

        sum_value = 1 / temp

        for i in range(1, num_steps + 1):
            a = i * (2 / num_steps)
            x = (sum_value / (math.sqrt(0.8 * (1 - (a - 0.6) ** 2 / 2.3))) * total_time)
            num[i - 1, 0] = i
            num[i - 1, 1] = x

        start_time = time.perf_counter()
        last_position = start

        # Di chuyển chuột theo đường cong Bézier
        for i, point in enumerate(curve_points):
            x, y = int(point[0]), int(point[1])

            # Thêm độ ngẫu nhiên vào khoảng cách dịch chuyển của từng bước, tránh việc khoảng cách dịch chuyển mỗi bước quá đều, gây nghi ngờ
            if end[0] > start[0]:
                x += random.choice([0, 1])  # Chỉ cho phép x và y tiến về phía đích, tránh đi lùi
            else:
                x += random.choice([-1, 0])

            if end[1] > start[1]:
                y += random.choice([0, 1])  # Chỉ cho phép x và y tiến về phía đích, tránh đi lùi
            else:
                y += random.choice([-1, 0])

            self.mouse.position = (x, y)

            # Tính khoảng cách di chuyển của bước hiện tại
            step_distance = np.linalg.norm(np.array((x, y)) - np.array(last_position))

            # Tính tỷ lệ x theo công thức để điều phối thời gian
            x_ratio = step_distance / 5

            # Tính time.sleep của từng bước sau khi được phân phối với tỉ lệ x
            sleep_time = num[i, 1] * x_ratio

            # In kiểm tra
            # print(
            #     f"Bước {i}/{num_steps}: Khoảng cách di chuyển: {step_distance:.2f} px, Tỷ lệ x: {x_ratio:.2f}, time.sleep: {sleep_time:.4f} s, di chuyển đến vị trí ({x}, {y})")

            time.sleep(max(0, sleep_time))
            last_position = (x, y)

        # Nếu có điểm kết thúc ảo, di chuyển tiếp đến điểm cuối theo phương pháp tương tự
        if fake_end:
            print(f"Điểm kết thúc ảo đạt được, điều chỉnh về {end}...")

            # Tính toán số bước và thời gian cần thiết
            correction_distance = np.linalg.norm(np.array(end) - np.array(fake_end))
            correction_steps = max(math.ceil(correction_distance / 5), 5)
            correction_time = self.fitts_law_total_time(correction_distance, size)

            # Tạo đường cong Bézier đến end
            control_points = [fake_end, ((fake_end[0] + end[0]) // 2, fake_end[1] - correction_distance * 0.01), end]
            correction_curve = self.bezier_curve(np.array(control_points), n=correction_steps)

            # Điều chỉnh cường độ nhiễu và tần suất nhiều khi di chuyển từ fake end đến end ở đây
            correction_curve = self.apply_gaussian_noise(correction_curve, scale=noise_scale * 1.5, frequency=0.99)

            # Di chuyển theo đường Bézier mới
            for i, point in enumerate(correction_curve):
                x, y = int(point[0]), int(point[1])
                self.mouse.position = (x, y)
                time.sleep(correction_time / correction_steps)

        end_time = time.perf_counter()

        # Cụm hàm đo thời gian di chuyển
        # print(f"Tổng thời gian cần thiết: {total_time}s")
        # print(f"Tổng thời gian phân phối: {np.sum(num[:, 1]):.3f}s")
        # print(f"Thời gian thực tế di chuyển: {end_time - start_time:.3f}s")

    def test_move(self, start, end):
        print(f"Di chuyển chuột từ {start} đến {end}...")
        self.move_mouse(start, end)
        # print("Hoàn tất!")


if __name__ == "__main__":
    mover = MouseMover()
    start_point = (200, 300)
    end_point = (1200, 350)
    mover.test_move(start_point, end_point)
