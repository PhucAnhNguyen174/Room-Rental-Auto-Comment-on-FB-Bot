# Các hàm liên quan đên căn chỉnh bài đăng
import pyautogui
from selenium.webdriver.common.by import By
import time
import random
import TabHandle
from Scrolling import Scrolling  # Import class từ file Scrolling - Nơi chứa các hàm mô phỏng hành vi cuộn trang
from selenium.common.exceptions import NoSuchElementException
import pygetwindow as gw
from Mousemove import MouseMover
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import sys
from datetime import datetime
import SendingGmail
from selenium.webdriver.support import expected_conditions as EC
import math

receiver_email = ["phucanh17042000@gmail.com", "pythonprojectbyphucanh@gmail.com"]

# Khởi tạo đối tượng từ class MouseMover
mover = MouseMover()

# Khởi tạo đối tượng từ class Scrolling
scroll = Scrolling()

def find_x_and_leave(driver, dpr, tab_bar_height):
    # Phát hiện và thoát nếu ấn nhầm vào report hoặc một cái dialog nào đó có dấu X
    print("Đang thực hiện hàm find_x_and_leave")
    try:
        # Tìm trực tiếp nút close (nút X)
        close_button = driver.find_element(
            By.CSS_SELECTOR,
            'div[aria-label="Close"].x1i10hfl.xjqpnuy.xc5r6h4.xqeqjp1.x1phubyo.x13fuv20.x18b5jzi.x1q0q8m5'
            '.x1t7ytsu.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x14z9mp.xat24cr.x1lziwak'
            '.x2lwn1j.xeuugli.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o'
            '.x1lku1pv.x1a2a7pz.x6s0dn4.x1iwo8zk.x1033uif.x179ill4.x1b60jn0.x972fbf.x10w94by'
            '.x1qhh985.x14e42zd.x9f619.x78zum5.xl56j7k.xexx8yu.xyri2b.x18d9i69.x1c1uobl'
            '.x1n2onr6.xc9qbxq.x14qfxbe.x1qhmfi1'
        )

    except NoSuchElementException:
        try:
            # Nếu không có dialog, tìm nút X ngoài
            close_button = driver.find_element(By.CSS_SELECTOR,
                "div.x1i10hfl.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5."
                "x26u7qi.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r."
                "x2lwn1j.xeuugli.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o."
                "x1lku1pv.x1a2a7pz.x6s0dn4.xzolkzo.x12go9s9.x1rnf11y.xprq8jg.x972fbf.xcfux6l."
                "x1qhh985.xm0m39n.x9f619.x78zum5.xl56j7k.xexx8yu.x4uap5.x18d9i69.xkhd6sd."
                "x1n2onr6.xc9qbxq.x14qfxbe.x1qhmfi1"
            )
        except NoSuchElementException:
            print("❌ Không tìm thấy nút X nào.")
            return

    # Lấy vị trí trung tâm nút X
    location = close_button.location
    size = close_button.size
    center_x = int(location['x'] + size['width'] / 2)
    center_y = int(location['y'] + size['height'] / 2)

    # Lệch nhẹ ngẫu nhiên ±4px
    offset_x = random.randint(-4, 4)
    offset_y = random.randint(-4, 4)
    target_x = (center_x + offset_x) * dpr
    target_y = (center_y + offset_y) * dpr + tab_bar_height

    # Di chuyển chuột đến vị trí và click
    current_mouse_pos = pyautogui.position()
    mover.test_move(current_mouse_pos, (target_x, target_y))
    pyautogui.click()
    print("Đã ấn nút X trong hàm find_x_and_leave")
    time.sleep(1)

def bring_debugging_chrome_to_front():
    try:
        chrome_windows = [w for w in gw.getWindowsWithTitle('Chrome')]

        if not chrome_windows:
            print("Không tìm thấy cửa sổ Chrome.")
            return

        # Ưu tiên cửa sổ không có tiêu đề cụ thể nào (thường là tab trống)
        target_window = None
        for w in chrome_windows:
            if w.title.strip() == "" or "New Tab" in w.title or "Google" in w.title:
                target_window = w
                break

        if not target_window:
            target_window = chrome_windows[0]

        print(f"Đưa Chrome '{target_window.title}' ra trước màn hình...")
        target_window.activate()
        time.sleep(1)
        target_window.maximize()
        time.sleep(1)

    except Exception:
        print(f"Lỗi khi đưa Chrome ra trước màn hình")


def check_and_leave(driver, dpr, tab_bar_height):
    # Phát hiện và thoát nếu cảnh báo rời trang xuất hiện
    print("Đang thực hiện hàm check_and_leave")
    try:
        # Tìm phần tử cảnh báo
        alert_element = driver.find_element("css selector",
                                             '.x1n2onr6.x1ja2u2z.x1afcbsf.xdt5ytf.x1a2a7pz.x71s49j.x1qjc9v5.xrjkcco.x58fqnu.x1mh14rs.xfkwgsy.x78zum5.x1plvlek.xryxfnj.xcatxm7.x1n7qst7.xh8yej3')
        print("Đã tìm thấy phần tử cảnh báo")
        if alert_element.is_displayed():
            try:
                # Tìm phần tử kiểm tra nội dung với class mới
                content_element = alert_element.find_element(
                    By.CSS_SELECTOR,
                    'span.x6zurak.x18bv5gf.x184q3qc.xqxll94.x1s928wv.xhkezso.x1gmr53x.'
                    'x1cpjm7i.x1fgarty.x1943h6x.x193iq5w.xeuugli.x13faqbe.x1vvkbs.'
                    'x2b8uid.x1lliihq.xzsf02u.xlh3980.xvmahel.x1x9mg3.x1xlr1w8'
                )
                content_text = content_element.text.strip()
                print(f"Tiêu đề của ô cảnh báo là {content_text}")

                if "leave" in content_text.lower():
                    print("Phát hiện cảnh báo rời trang, đang tìm nút Leave Page...")
                    try:
                        # Tìm nút Leave Page bên trong alert_element
                        leave_button = WebDriverWait(alert_element, 1).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR,
                                'div[aria-label="Leave Page"][role="button"]'
                            ))
                        )

                        print("Đã tìm thấy nút Leave Page")

                        # Tính toán tọa độ click
                        element_x = leave_button.location['x'] * dpr
                        element_y = leave_button.location['y'] * dpr + tab_bar_height
                        random_x = random.randint(int(5 * dpr), int(60 * dpr))
                        random_y = random.randint(int(5 * dpr), int(25 * dpr))
                        end_point = (element_x + random_x, element_y + random_y)

                        start_x, start_y = pyautogui.position()

                        # Di chuyển chuột đến nút Leave Page và click
                        mover.test_move((start_x, start_y), end_point)
                        pyautogui.click()
                        print("Đã ấn nút Leave Page trong hàm check_and_leave")
                    except TimeoutException:
                        print("Không tìm thấy nút Leave Page trong cảnh báo.")
                    pass
                else:
                    print("Phát hiện phần tử không xác định, dừng chương trình.")
                    now = datetime.now()
                    subject = f"Chương trình đã được dừng do phát hiện phần tử không xác định trong hàm check_and_leave"
                    body = f"Thời gian: {now.strftime('%H:%M:%S')}"

                    SendingGmail.send_email(subject, body, receiver_email)
                    sys.exit(0)

            except NoSuchElementException:
                print("Không tìm thấy tiêu đề ô cảnh báo, bỏ qua")
                pass

    except NoSuchElementException:
        print("Không có phần tử cảnh báo")
        pass  # Không có cảnh báo, tiếp tục chạy


def check_misclick_into_picture(driver, dpr, tab_bar_height):
    print("Đang thực hiện hàm check_misclick_into_picture")
    try:
        # Phát hiện vào chế độ xem ảnh
        driver.find_element(By.CSS_SELECTOR,
            '.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.x1dr59a3.xadl8oe'
        )
        print("Phát hiện đã ấn nhầm vào ảnh của bài đăng, đang tìm nút để thoát...")

        try:
            # Tìm nút Close (X) theo đúng selector
            close_button = driver.find_element(By.CSS_SELECTOR,
                                               "div.x1i10hfl.xjqpnuy.xc5r6h4.xqeqjp1.x1phubyo.x13fuv20.x18b5jzi.x1q0q8m5."
                                               "x1t7ytsu.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x14z9mp.xat24cr.x1lziwak."
                                               "x2lwn1j.xeuugli.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o."
                                               "x1lku1pv.x1a2a7pz.x6s0dn4.xzolkzo.x12go9s9.x1rnf11y.xprq8jg.x972fbf.x10w94by."
                                               "x1qhh985.x14e42zd.x9f619.x78zum5.xl56j7k.xexx8yu.xyri2b.x18d9i69.x1c1uobl."
                                               "x1n2onr6.x1vqgdyp.x100vrsf.x18l40ae.x14ctfv"
                                               )

        except NoSuchElementException:
            print("Không tìm thấy nút X để thoát khỏi ảnh.")
            return

        # Tính toán tọa độ trung tâm nút
        location = close_button.location
        size = close_button.size
        center_x = int(location['x'] + size['width'] / 2)
        center_y = int(location['y'] + size['height'] / 2)

        # Lệch ngẫu nhiên ±4px
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)

        target_x = (center_x + offset_x) * dpr
        target_y = (center_y + offset_y) * dpr + tab_bar_height

        # Di chuyển chuột và click
        current_mouse_pos = pyautogui.position()
        mover.test_move(current_mouse_pos, (target_x, target_y))
        pyautogui.click()
        print("Đã click để thoát khỏi ảnh trong hàm check_misclick_into_picture")

        time.sleep(1)

    except NoSuchElementException:
        # Không ở chế độ ảnh, không cần xử lý
        pass


class PostAligner:
    def __init__(self, driver, dpr, tab_bar_height):
        self.driver = driver  # Driver sẽ được truyền vào khi tạo đối tượng
        self.has_scrolled_down_once = False
        self.dpr = dpr
        self.tab_bar_height = tab_bar_height

    def update_driver(self, new_driver):
        """Cập nhật WebDriver mới sau khi đổi tài khoản"""
        self.driver = new_driver

    def is_post_top_in_correct_position(self, post, menu, dpr):
        """Kiểm tra khoảng cách giữa góc trên của bài đăng và góc dưới của menu."""
        menu_bottom = menu.location['y'] + menu.size['height']
        post_top = post.location['y']
        distance_to_menu_bottom = post_top - menu_bottom
        print(f"Khoảng cách giữa góc trên bài đăng và menu: {distance_to_menu_bottom}px")
        return -12 * dpr <= distance_to_menu_bottom <= 100 * dpr, distance_to_menu_bottom

    def scroll_to_post_top(self, post, menu, dpr, driver, tab_bar_height):
        count = 0
        big_count = 0
        """Cuộn để góc trên bài đăng có khoảng cách phù hợp với menu."""

        while True:
            in_position, distance = self.is_post_top_in_correct_position(post, menu, dpr)
            print(f"Đang thực hiện scroll_to_post_top, khoảng cách giữa post_top và menu_bottom hiện tại là {distance}px")
            count += 1

            if count > 20:
                print("Việc scroll_to_post_top được thực hiện quá nhiều lần, thực hiện focus lại")

                big_count += 1
                if big_count > 3:
                    print("Chương trình đã được dừng lại do scroll_to_post_top được gọi quá nhiều")
                    now = datetime.now()
                    subject = f"Chương trình đã được dừng do scroll_to_post_top được gọi quá nhiều"
                    body = f"Thời gian: {now.strftime('%H:%M:%S')}"

                    SendingGmail.send_email(subject, body, receiver_email)

                    sys.exit(0)

                bring_debugging_chrome_to_front()
                find_x_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_misclick_into_picture(driver, dpr, tab_bar_height)
                pyautogui.press('esc')
                TabHandle.switch_tab_to(driver, "facebook")
                time.sleep(random.uniform(0.8, 1.2))
                start = pyautogui.position()
                random_x = random.randint(-20 * dpr, 20 * dpr)
                random_y = random.randint(-90 * dpr, 90 * dpr)
                end = (986 + random_x, 427 + random_y)
                time.sleep(random.uniform(0.4, 0.8))
                mover.test_move(start, end)
                pyautogui.click()
                count = 0

            if in_position:
                # print("Góc trên bài đăng đã nằm ở vị trí phù hợp.")
                break

            elif count % 6 == 0:
                _ , distance = self.is_post_top_in_correct_position(post, menu, dpr)
                x = int(math.copysign(math.ceil(abs(distance / 99)), distance))
                print("Đang thực hiện việc scroll chuẩn xác")
                for _ in range(abs(x)):
                    if x > 0:
                        scroll.scroll_up_one_time()
                        time.sleep(random.uniform(0.04, 0.06))

                    elif x < 0:
                        scroll.scroll_down_one_time()
                        time.sleep(random.uniform(0.04, 0.06))

            elif distance > 300 * dpr:
                print(f"Khoảng cách còn {distance}px (> 300px), sử dụng slow_scroll_down_simulation.")
                scroll.slow_scroll_down_simulation()
                time.sleep(random.uniform(0.1, 0.15))

            elif 0 < distance <= 300 * dpr:
                print(f"Khoảng cách còn {distance}px (≤ 300px), sử dụng scroll_down_one_time để tinh chỉnh.")
                scroll.scroll_down_one_time()
                time.sleep(0.08)

            elif distance < 0:
                print(f"Đã cuộn quá đà ({abs(distance)}px), sử dụng scroll_up_one_time để chỉnh lại.")
                scroll.scroll_up_one_time()
                time.sleep(0.08)
                self.has_scrolled_down_once = False

            if 50 * dpr <= abs(distance) <= 85 * dpr and random.random() < 0.15 and not self.has_scrolled_down_once:
                # print(f"Góc trên bài đăng cách menu {abs(distance)}px, thử kéo xuống thêm một lần (15% xác suất).")
                scroll.scroll_down_one_time()
                time.sleep(0.25)
                self.has_scrolled_down_once = True
                in_position, new_distance = self.is_post_top_in_correct_position(post, menu, dpr)
                if not in_position:
                    # print(f"Sau khi cuộn xuống, khoảng cách vẫn là {abs(new_distance)}px. Cuộn lên để chỉnh lại.")
                    scroll.scroll_up_one_time()
                    time.sleep(0.1)

    def is_post_bottom_in_viewport(self, post, dpr):
        """Kiểm tra xem khoảng cách giữa góc dưới bài đăng và góc dưới viewport có nằm trong khoảng 0-133px không."""
        post_bottom = post.location['y'] + post.size['height']
        viewport_height = self.driver.execute_script("return window.innerHeight")
        viewport_bottom = self.driver.execute_script("return window.pageYOffset") + viewport_height
        distance_to_viewport_bottom = viewport_bottom - post_bottom
        print(f"Khoảng cách giữa góc dưới bài đăng và góc dưới viewport: {distance_to_viewport_bottom}px")
        return 20 <= distance_to_viewport_bottom <= 200 * dpr, distance_to_viewport_bottom

    def scroll_to_post_bottom(self, post, index, dpr, driver, tab_bar_height):
        count = 0
        big_count = 0
        """Cuộn xuống để góc dưới bài đăng nằm cách góc dưới viewport không quá 133px."""
        if index <= 1:
            # print(f"Bỏ qua cuộn vì index = {index} (≤ 1).")
            return

        while True:
            in_viewport, distance = self.is_post_bottom_in_viewport(post, dpr)
            count += 1

            if count > 20:
                print("Việc scroll_to_post_top được thực hiện quá nhiều lần, thực hiện focus lại")

                big_count += 1
                if big_count > 3:
                    print("Chương trình đã được dừng lại do scroll_to_post_top được gọi quá nhiều")
                    now = datetime.now()
                    subject = f"Chương trình đã được dừng do scroll_to_post_top được gọi quá nhiều"
                    body = f"Thời gian: {now.strftime('%H:%M:%S')}"

                    SendingGmail.send_email(subject, body, receiver_email)

                    sys.exit(0)

                bring_debugging_chrome_to_front()
                find_x_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_misclick_into_picture(driver, dpr, tab_bar_height)
                pyautogui.press('esc')
                TabHandle.switch_tab_to(driver, "facebook")
                time.sleep(random.uniform(0.8, 1.2))
                start = pyautogui.position()
                random_x = random.randint(-20 * dpr, 20 * dpr)
                random_y = random.randint(-90 * dpr, 90 * dpr)
                end = (986 + random_x, 427 + random_y)
                time.sleep(random.uniform(0.4, 0.8))
                mover.test_move(start, end)
                pyautogui.click()
                count = 0

            if in_viewport:
                # print("Góc dưới bài đăng đã nằm trong khoảng thích hợp.")
                break

            elif count % 6 == 0:
                time.sleep(0.5)
                _, distance = self.is_post_bottom_in_viewport(post, dpr)
                x = int(math.copysign(math.ceil(abs(distance / 99)), distance))
                print("Đang thực hiện việc scroll chuẩn xác")
                for _ in range(abs(x)):
                    if x > 0:
                        scroll.scroll_up_one_time()
                        time.sleep(random.uniform(0.04, 0.06))

                    elif x < 0:
                        scroll.scroll_down_one_time()
                        time.sleep(random.uniform(0.04, 0.06))

            elif distance > 300 * dpr:
                # print(f"Khoảng cách còn {distance}px (> 300px), sử dụng slow_scroll_up_simulation.")
                scroll.slow_scroll_up_simulation()
                time.sleep(0.2)
            elif 20 < distance <= 300 * dpr:
                # print(f"Khoảng cách còn {distance}px (≤ 300px), sử dụng scroll_down_one_time để tinh chỉnh.")
                scroll.scroll_up_one_time()
                time.sleep(0.2)
            elif distance < 20:
                # print(f"Đã cuộn quá đà ({abs(distance)}px), sử dụng scroll_up_one_time để chỉnh lại.")
                scroll.scroll_down_one_time()
                time.sleep(0.35)


    def scroll_up_to_see_post_content(self, post, menu, dpr):
        """Cuộn lại lên để xem nội dung bài đăng nếu bài đăng có nội dung."""
        try:
            # Tìm phần tử chứa nội dung bài đăng
            content_element = post.find_element(By.CSS_SELECTOR, ".xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs.x126k92a")

            # Kiểm tra xem nội dung có tồn tại hay không
            if content_element:
                # print("Bài đăng có nội dung. Thực hiện cuộn lên để xem.")

                # Xác suất 8% để cuộn lại lên
                if random.random() < 0.08:
                    print("Xác suất cho phép: Cuộn lại lên để xem nội dung bài đăng.")

                    # Lựa chọn ngẫu nhiên giữa slow_scroll_up và scroll_up_one_time
                    if random.random() < 0.5:
                        # print("Sử dụng slow_scroll_up.")
                        scroll.slow_scroll_up_simulation()
                        time.sleep(random.uniform(0.2, 0.5))  # Thời gian nghỉ ngắn giữa các lần cuộn
                    else:
                        # print("Sử dụng scroll_up_one_time.")
                        scroll.scroll_up_one_time()
                        time.sleep(random.uniform(0.2, 0.4))  # Thời gian nghỉ ngắn giữa các lần cuộn

                    # Kiểm tra nếu phần nội dung bài đăng đã vào trong viewport
                    while not self.is_post_top_in_correct_position(post, menu, dpr):
                        scroll.scroll_up_one_time()  # Nếu chưa, tiếp tục cuộn lên
                        time.sleep(0.4)  # Đợi một chút trước khi cuộn tiếp
                else:
                    print("Không cuộn lên vì xác suất không đủ.")
        except NoSuchElementException:
            print("Không tìm thấy nội dung bài đăng. Bỏ qua cuộn lên.")
            return

    def is_content_in_viewport(self, content_element):
        """Kiểm tra xem phần nội dung bài đăng có nằm trong viewport không."""
        location = content_element.location
        size = content_element.size
        viewport_height = self.driver.execute_script("return window.innerHeight")

        # Kiểm tra xem phần tử có nằm trong viewport (từ trên xuống dưới)
        return (location['y'] + size['height'] > 0 and location['y'] < viewport_height)

    def rough_align_post_top_with_menu(self, post, menu, dpr, driver, tab_bar_height):
        """Căn chỉnh nửa vời: chỉ cần góc trên bài đăng nằm cách menu từ 0 đến 300px."""
        count = 0
        big_count = 0

        def is_in_rough_position(post, menu, dpr):
            menu_bottom = menu.location['y'] + menu.size['height']
            post_top = post.location['y']
            distance = post_top - menu_bottom
            return -150 * dpr <= distance <= 300 * dpr, distance

        while True:
            in_position, distance = is_in_rough_position(post, menu, dpr)
            print(f"Đang căn chỉnh rough_align, khoảng cách giữa post_top và menu_bottom hiện tại là {distance}px")
            count += 1

            if count > 50:
                print("Việc rough_align_post_top_with_menu được thực hiện quá nhiều lần, thực hiện focus lại")

                big_count += 1
                if big_count > 3:
                    print("Chương trình đã được dừng lại do rough_align_post_top_with_menu được gọi quá nhiều")
                    now = datetime.now()
                    subject = f"Chương trình đã được dừng do rough_align_post_top_with_menu được gọi quá nhiều"
                    body = f"Thời gian: {now.strftime('%H:%M:%S')}"

                    SendingGmail.send_email(subject, body, receiver_email)
                    sys.exit(0)

                bring_debugging_chrome_to_front()
                find_x_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_misclick_into_picture(driver, dpr, tab_bar_height)
                pyautogui.press('esc')
                TabHandle.switch_tab_to(driver, "facebook")
                time.sleep(random.uniform(0.8, 1.2))
                start = pyautogui.position()
                random_x = random.randint(-20 * dpr, 20 * dpr)
                random_y = random.randint(-90 * dpr, 90 * dpr)
                end = (986 + random_x, 427 + random_y)
                time.sleep(random.uniform(0.4, 0.8))
                mover.test_move(start, end)
                pyautogui.click()
                count = 0

            if in_position:
                break

            if distance > 300 * dpr:
                scroll.slow_scroll_down_simulation()
                # print("Thực hiện việc slow_scroll_down_simulation")
                time.sleep(random.uniform(0.02, 0.03))

            elif distance < -150 * dpr:
                scroll.scroll_up_one_time()
                print("Thực hiện việc scroll_up_one_time")
                time.sleep(0.02)

    def is_post_top_in_correct_position_for_filter(self, post, menu, dpr):
        """Kiểm tra khoảng cách giữa góc trên của bài đăng và góc dưới của menu."""
        menu_bottom = menu.location['y'] + menu.size['height']
        post_top = post.location['y']
        distance_to_menu_bottom = post_top - menu_bottom
        print(f"Khoảng cách giữa góc trên bài đăng và menu: {distance_to_menu_bottom}px")
        return 0 * dpr <= distance_to_menu_bottom <= 120 * dpr, distance_to_menu_bottom

    def scroll_to_post_top_for_filter(self, post, menu, dpr, driver, tab_bar_height):
        count = 0
        big_count = 0
        """Cuộn để góc trên bài đăng có khoảng cách phù hợp với menu."""
        while True:
            in_position, distance = self.is_post_top_in_correct_position_for_filter(post, menu, dpr)
            count += 1

            if count > 20:
                print("Việc scroll_to_post_top được thực hiện quá nhiều lần, thực hiện focus lại")

                big_count += 1
                if big_count > 3:
                    print("Chương trình đã được dừng lại do scroll_to_post_top được gọi quá nhiều")
                    now = datetime.now()
                    subject = f"Chương trình đã được dừng do scroll_to_post_top được gọi quá nhiều"
                    body = f"Thời gian: {now.strftime('%H:%M:%S')}"

                    SendingGmail.send_email(subject, body, receiver_email)

                    sys.exit(0)

                bring_debugging_chrome_to_front()
                find_x_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_and_leave(driver, dpr, tab_bar_height)
                time.sleep(1)
                check_misclick_into_picture(driver, dpr, tab_bar_height)
                pyautogui.press('esc')
                TabHandle.switch_tab_to(driver, "facebook")
                time.sleep(random.uniform(0.8, 1.2))
                start = pyautogui.position()
                random_x = random.randint(-20 * dpr, 20 * dpr)
                random_y = random.randint(-90 * dpr, 90 * dpr)
                end = (986 + random_x, 427 + random_y)
                time.sleep(random.uniform(0.4, 0.8))
                mover.test_move(start, end)
                pyautogui.click()
                count = 0

            if in_position:
                print(f"Góc trên bài đăng đã nằm ở vị trí phù hợp {distance}px")
                break

            elif count % 6 == 0:
                time.sleep(0.5)
                _, distance = self.is_post_top_in_correct_position_for_filter(post, menu, dpr)
                x = int(math.copysign(math.ceil(abs(distance / 99)), distance))
                print("Đang thực hiện việc scroll chuẩn xác")
                for _ in range(abs(x)):
                    if x > 0:
                        scroll.scroll_up_one_time()
                        time.sleep(random.uniform(0.04, 0.06))

                    elif x < 0:
                        scroll.scroll_down_one_time()
                        time.sleep(random.uniform(0.04, 0.06))

            elif distance > 300 * dpr:
                # print(f"Khoảng cách còn {distance}px (> 300px), sử dụng slow_scroll_down_simulation.")
                scroll.slow_scroll_down_simulation()
                time.sleep(random.uniform(0.1, 0.15))

            elif 0 < distance <= 300 * dpr:
                # print(f"Khoảng cách còn {distance}px (≤ 300px), sử dụng scroll_down_one_time để tinh chỉnh.")
                scroll.scroll_down_one_time()
                time.sleep(0.08)

            elif distance < 0 * dpr:
                # print(f"Đã cuộn quá đà ({abs(distance)}px), sử dụng scroll_up_one_time để chỉnh lại.")
                scroll.scroll_up_one_time()
                time.sleep(0.08)
                self.has_scrolled_down_once = False

            if 50 * dpr <= abs(distance) <= 85 * dpr and random.random() < 0 and not self.has_scrolled_down_once:
                # print(f"Góc trên bài đăng cách menu {abs(distance)}px, thử kéo xuống thêm một lần (0% xác suất).")
                scroll.scroll_down_one_time()
                time.sleep(0.25)
                self.has_scrolled_down_once = True
                in_position, new_distance = self.is_post_top_in_correct_position_for_filter(post, menu, dpr)
                if not in_position:
                    # print(f"Sau khi cuộn xuống, khoảng cách vẫn là {abs(new_distance)}px. Cuộn lên để chỉnh lại.")
                    scroll.scroll_up_one_time()
                    time.sleep(0.1)
