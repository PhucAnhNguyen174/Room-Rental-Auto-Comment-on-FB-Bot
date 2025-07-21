import pyperclip
import os
import sys
import TabHandle
import Start2
import time
import random
import TimeManage
import pyautogui
import SendingGmail
from datetime import datetime
from selenium.webdriver.common.by import By
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key
from pynput.mouse import Button, Controller
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from Scrolling import Scrolling  # Import class từ file Scrolling - Nơi chứa các hàm mô phỏng hành vi cuộn trang
from Mousemove import MouseMover  # Import class từ file Mousemove - Nơi chứa các hàm mô phỏng hành vi di chuyển con trỏ chuột
from Align import PostAligner
from selenium.common.exceptions import WebDriverException
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib3
import http.client

# Khởi tạo đối tượng từ class MouseMover
mover = MouseMover()

# Khởi tạo đối tượng từ class Scrolling
scroll = Scrolling()

# Điều khiển chuột và bàn phím
mouse = Controller()
keyboard = KeyboardController()

first_message_sent = False  # Biến kiểm tra xem đã gửi tin nhắn lần đầu hay chưa
found_post = False  # Biến cờ kiểm soát xem bài đăng đã xuất hiện chưa
preprocess_successful = False
content_not_available_anymore = False
question_send_to_chatgpt_count = 0  # Biến xác định conservation-turn
answer_from_chatgpt_try_time = 0
reopen_chatgpt_time = 0
comment_count = 0
number_of_processed_post = 0
number_of_post_commented = 0
menu = None
width_screen, height_screen = pyautogui.size()
screen_scale_x = width_screen / 1366
screen_scale_y = height_screen / 768
screen_scale = min(screen_scale_x, screen_scale_y)
pos = 1
i = 0
reset_facebook_web_time = 0
reset_flag = False

# Danh sách từ khóa cần chặn khi quét nội dung bài đăng
def load_keywords(filename):
    path = f'keywords/{filename}'  # hoặc os.path.join nếu cần đa nền tảng
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

post_content_valid_keywords = load_keywords('valid_keywords.txt')
post_content_invalid_keywords1 = load_keywords('invalid_keywords1.txt')
post_content_invalid_keywords2 = load_keywords('invalid_keywords2.txt')
post_content_extreme_invalid_keywords = load_keywords('extreme_invalid_keywords.txt')

# Danh sách theo từng vùng
group_keywords_A1 = [
    "cầu giấy", "xuân thuỷ", "dịch vọng", "yên hoà", "trung hoà", "trung kính",
    "nghĩa tân", "hoàng quốc việt", "trần duy hưng", "phạm văn đồng",
    "hồ tùng mậu", "quan hoa", "nghĩa đô", "phong sắc"
]
group_keywords_A2 = [
    "ba đình", "hoàng hoa thám", "tây hồ", "hoàn kiếm", "đội cấn", "kim mã",
    "đào tấn", "ngọc khánh", "bưởi", "trích sài", "thuỵ khuê",
]
group_keywords_A3 = [
    "đống đa", "ngã tư sở", "láng", "trần duy hưng", "hào nam", "ô chợ dừa",
    "đê la thành", "lê duẩn", "xã đàn", "hoàng cầu"
]
group_keywords_A5 = [
    "bắc từ liêm",
]
group_keywords_A6 = [
    "mỹ đình", "đình thôn", "nam từ liêm",
]
group_keywords_A7 = [
    "hai bà trưng", "bách - kinh - xây", "bách khoa", "đh xây dựng", "dh xây dựng", "đại học xây dựng"
]
group_keywords_A8 = [
    "tây hồ",
]
group_keywords_A9 = [
    "hà nội", "nhà trọ", "phòng trọ", "sinh viên", "giá rẻ"
]

# Danh sách từ khoá hợp lệ khi quét tên nhóm
group_name_valid_keywords = ["trọ", "giá rẻ", "sinh viên", "cho thuê", "cầu giấy", "đống đa", "đình thôn", "mỹ đình",
                             "ngã tư sở", "ba đình", "mễ trì", "láng", "hai bà trưng", "dịch vọng", "từ liêm",
                             "mễ trì", ]

# Vị trí của profile cá nhân
# Toạ độ x - Toạ độ y - Tên Facebook - Loại file comment
profile_location = {
    "profile1": (415, 431, "Phi Dong", "x", 15),
    "profile2": (771, 431, "Phi Truong", "y", 27),
    "profile3": (592, 431, "Phuc Anh", "x", 34),
    "profile4": (592, 431, "Nguyễn Phúc Anh", "x", 24),
    "profile5": (592, 431, "Hai Anh", "y", 29),
    "profile6": (592, 431, "Ha Linh", "z", 29),
    "profile7": (592, 431, "Trieu Tu Long", "x", 29),
    "profile8": (592, 431, "Nhat Linh", "y", 29),
}
profile_count = 1

file_path = "info.txt"

if not os.path.exists(file_path):
    # File chưa tồn tại → tạo và ghi ---
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("---\n")
    print(f"📁 File '{file_path}' chưa tồn tại, đã tạo mới và ghi dấu '---'")
else:
    # File đã tồn tại → kiểm tra nội dung
    with open(file_path, "r+", encoding="utf-8") as f:
        content = f.read().strip()
        if content == "":
            f.write("---\n")
            print(f"⚠️ File '{file_path}' tồn tại nhưng trống → đã ghi bổ sung dấu '---'")
        else:
            print(f"✅ File '{file_path}' đã tồn tại và có nội dung → không cần thay đổi")

target = profile_location[f"profile{profile_count}"][4]

receiver_email = ["phucanh17042000@gmail.com", "pythonprojectbyphucanh@gmail.com"]

number_of_profile = len(profile_location)

TimeManage.wait_for_valid_time()  # Kiểm tra thời gian trước khi quét bài đăng
driver, tab_bar_height, dpr, theme, taskbar_height = Start2.start_browsers(profile_count, screen_scale_x,
                                                                           screen_scale_y)
time.sleep(2)

# Tạo đối tượng PostAligner
aligner = PostAligner(driver, dpr, tab_bar_height)

MENU_SELECTOR = 'div[aria-hidden="false"].xtijo5x.x1o0tod.xixxii4.x13vifvy.x1vjfegm'
POST_SELECTOR_TEMPLATE = 'div[aria-posinset="{pos}"]'
ADS_SPAN_SELECTOR = 'span.xmper1u.xt0psk2.xjb2p0i.x1qlqyl8.x15bjb6t.x1n2onr6.x17ihmo5.x1g77sc7'
REELS_SPAN_SELECTOR = 'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x676frb.x1lkfr7t.x1lbecb7.x1s688f.xzsf02u'


def handle_post(post, menu, index):
    group_name = get_group_name(post)
    print(f"Tên nhóm là: {group_name}")

    if group_name is None:
        pass

    elif not analyze_group_name(group_name, post):
        print(f"Bài đăng có nội dung không liên quan đến việc thuê nhà trọ")

        random_value = random.random()

        if random_value < 0:  # 0% xác suất ở lại xem

            print("Quyết định ở lại xem bài đăng mặc dù không liên quan")
            aligner.scroll_to_post_top(post, menu, dpr, driver, tab_bar_height)
            wait_time = random.uniform(1, 1.5)
            print(f"Dừng lại {wait_time:.1f} giây rồi lướt tiếp.")
            time.sleep(wait_time)
            aligner.scroll_to_post_bottom(post, index, dpr, driver, tab_bar_height)

        elif 0 < random_value < 1:
            aligner.scroll_to_post_top_for_filter(post, menu, dpr, driver, tab_bar_height)
            filter_spam_and_click(post, menu, action_type="super negative")

        else:
            print("Quyết định bỏ qua bài đăng")
            # Thực hiện hành động cuộn nhanh qua bài đăng
        # pass
    else:
        print("Bài đăng thông thường. Đang xử lý...")
        aligner.scroll_to_post_top(post, menu, dpr, driver, tab_bar_height)
        print("Bài đăng đã được căn chỉnh")

        if preprocess_content_stage_1(post):
            filter_spam_and_click(post, menu, action_type="super negative")
            return

            # Thử lấy nội dung văn bản trước
        text_content = get_post_text_2ndgen(post)

        if text_content:
            print(f"📋 Nội dung bài đăng: {text_content}")
            write_content(text_content)
            response_text_content = process_data(text_content, group_name, post, menu)
            handle_response(response_text_content, post, index, menu)
        else:
            print("Không thể lấy được nội dung bài đăng")


def read_file(filename):
    """Đọc nội dung từ file nếu tồn tại."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return [line for line in f.readlines()]
    return []


def write_content(text_content, file_path="info.txt"):
    # Tách text_content thành từng đoạn dựa vào dòng trắng
    blocks = [block.strip() for block in text_content.strip().split('\n\n') if block.strip()]

    with open(file_path, "a", encoding="utf-8") as f:
        for block in blocks:
            f.write("Content: ")
            f.write(block.replace('\r\n', '\n').replace('\r', '\n'))
            f.write("\n")  # đảm bảo xuống dòng sau mỗi content


def write_label(label, file_path="info.txt"):
    print(f"Ghi label: {label}")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"Label: {label}\n")
        f.write("---\n")


def process_data(post_content, group_name, post, menu):
    """
    Chuyển sang tab ChatGPT, tìm ô nhập chat, dán nội dung, gửi và lấy phản hồi.
    """
    global question_send_to_chatgpt_count, answer_from_chatgpt_try_time, reopen_chatgpt_time
    cloudflare_bypass_try_time = 0
    input_box = None

    # 🔹 Kiểm tra trước khi gửi lên ChatGPT
    response_text = preprocess_content_stage_2(post_content, group_name)
    if response_text:
        ran = random.random()
        if response_text == "Y1" and ran < 1: # Điều chỉnh tỉ lệ khi cần
            aligner.scroll_to_post_top(post, menu, dpr, driver, tab_bar_height)
            filter_spam_and_click(post, menu, action_type="super negative")
            write_label("N")
            return response_text
        elif response_text == "Y2" and ran < 1:
            aligner.scroll_to_post_top(post, menu, dpr, driver, tab_bar_height)
            filter_spam_and_click(post, menu, action_type="negative")
            write_label("N")
            return response_text
        else:
            return response_text

    # Chuyển sang tab ChatGPT
    TabHandle.switch_tab_to(driver, "chatgpt")
    print("Thực hiện chuyển sang ChatGPT trong hàm process_data")
    driver.implicitly_wait(2)

    pyautogui.click()
    time.sleep(0.5)

    additional_text = " ".join(read_file("content.txt"))
    final_content = f"{additional_text} \n-Tên nhóm: {group_name}\n-Nội dung:\n {post_content}"

    # 🔹 Dán nội dung vào clipboard
    pyperclip.copy(final_content)

    while not response_text:
        if answer_from_chatgpt_try_time > 0:
            print(f"Đã reset tab ChatGPT, đang thực hiện lại việc gửi câu hỏi và lấy câu trả lời từ ChatGPT")

        if reopen_chatgpt_time == 2:
            print("Không thể lấy được câu trả lời sau nhiều lần mở lại tab, đổi tài khoản")
            change_account()

        # Tìm ô nhập liệu của ChatGPT
        try:
            input_box = driver.find_element(By.ID, "prompt-textarea")
            print("✅ Đã tìm thấy ô nhập liệu bằng ID")

            input_box.click()  # Click trực tiếp bằng Selenium
            time.sleep(0.5)  # Chờ một chút để đảm bảo trang phản hồi

        except:
            print("❌ Không tìm thấy ô nhập liệu:")  # Thử nghiệm chưa áp dụng
            time.sleep(10)
            start = pyautogui.position()
            random_x = random.randint(-3 * dpr, 3 * dpr)
            random_y = random.randint(-3 * dpr, 3 * dpr)
            end = (561 + random_x, 455 + random_y)
            time.sleep(random.uniform(0.4, 0.8))
            mover.test_move(start, end)
            mouse.press(Button.left)
            time.sleep(random.uniform(0.08, 0.15))
            mouse.release(Button.left)
            time.sleep(15)
            open_new_chatgpt_tab(driver)
            time.sleep(5)
            continue
            # Có thể thêm logic xử lý như reload hoặc đổi tab ở đây

        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.5)

        # 🔹 Dán nội dung bằng tổ hợp phím (an toàn hơn `pyperclip.paste()`)
        pyautogui.hotkey("ctrl", "v")

        try:
            try:
                send_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Send prompt"]'))
                )

                print(
                    f"✅ Đã tìm thấy nút gửi tin nhắn và gửi nội dung lên ChatGPT - Câu hỏi #{question_send_to_chatgpt_count + 1}")

                send_button.click()  # Thực hiện click nếu tìm thấy nút
                question_send_to_chatgpt_count += 1
                print("Đã ấn nút gửi tin nhắn.")

            except Exception as e:
                print(f"Lỗi khi ấn nút gửi tin nhắn: {e}")
                try:
                    # 🔹 Kiểm tra và ấn nút ngăn cản việc gửi tin nhắn
                    stop_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, 'button[aria-label="Stop streaming"], button[data-testid="stop-button"]'))
                    )
                    stop_button.click()  # Thực hiện click vào nút ngừng (nếu có)
                    print("Đã ấn nút dừng trả lời")

                    time.sleep(1)  # Thêm một khoảng nghỉ trước khi thử lại

                    # Sau khi ấn nút ngừng, tiếp tục ấn nút gửi tin nhắn
                    send_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.icon-2xl"))
                    )
                    send_button.click()  # Thực hiện click nút gửi tin nhắn
                    question_send_to_chatgpt_count += 1
                    print("Đã ấn lại nút gửi tin nhắn.")

                except Exception as inner_e:
                    print(f"Lỗi khi ấn nút ngừng hoặc gửi tin nhắn: {inner_e}")

            # 🔹 Lấy câu trả lời từ ChatGPT (thêm WebDriverWait)
            conversation_turn = question_send_to_chatgpt_count * 2  # ChatGPT có thể thay đổi conversation_turn hoặc cấu trúc HTML

            # Gọi hàm wait_for_response_content để lấy nội dung từ response_block
            response_text = wait_for_response_content(driver, conversation_turn, timeout=20)

            if response_text:
                print("📩 Câu trả lời từ ChatGPT:")
                print(response_text)
                answer_from_chatgpt_try_time = 0
                return response_text

            elif not response_text:
                answer_from_chatgpt_try_time += 1
                if answer_from_chatgpt_try_time < 2:
                    print(
                        f"❌ Không lấy được câu trả lời từ ChatGPT! Reset lại tab - Thử lại lần {answer_from_chatgpt_try_time}")
                    pyautogui.hotkey('ctrl', 'r')
                    time.sleep(10)
                    continue
                elif answer_from_chatgpt_try_time == 3:
                    print("Không thể lấy câu trả lời từ ChatGPT sau 3 lần reset tab, thực hiện deep reset")
                    reopen_chatgpt_time += 1
                    open_new_chatgpt_tab(driver)
                    continue

        except Exception as e:
            print(f"❌ Không thể lấy câu trả lời từ ChatGPT! Lỗi chi tiết: {e}")

            if answer_from_chatgpt_try_time < 2:
                answer_from_chatgpt_try_time += 1
                print(
                    f"❌ Không lấy được câu trả lời từ ChatGPT! Reset lại tab - Thử lại lần {answer_from_chatgpt_try_time}")
                pyautogui.hotkey('ctrl', 'r')
                time.sleep(8)
                continue
            else:
                print("Không thể lấy câu trả lời từ ChatGPT sau 3 lần reset tab, thực hiện deep reset")
                open_new_chatgpt_tab(driver)
                continue


def handle_response(response_text, post, index, menu):
    global preprocess_successful
    """Phân tích phản hồi từ ChatGPT và thực hiện comment trên Facebook."""
    keywords = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
                "A9"]  # Nếu phản hồi của ChatGPT có từ nào nằm trong keywords này thì là nội dung hợp lệ
    skip_keywords_minor_warning = ["X3", "X4",
                                   "X5"]  # Nếu phản hồi của ChatGPT có từ nào nằm trong này thì là ngược lại
    skip_keywords_severe_warning = ["X1", "X2", "X6",
                                    "Z1"]  # Nếu phản hồi của ChatGPT có từ nào nằm trong này thì là ngược lại

    if any(kw in response_text for kw in skip_keywords_minor_warning):
        print("ChatGPT phản hồi rằng bài đăng không phù hợp, cảnh báo nhẹ")

        # Chuyển sang tab còn lại (Facebook)
        print("Thực hiện chuyển sang Facebook trong hàm handle_response")
        TabHandle.switch_tab_to(driver, "facebook")
        filter_spam_and_click(post, menu, action_type="negative")
        write_label("N")
        return  # Kết thúc hàm ngay sau khi chuyển tab

    elif any(kw in response_text for kw in skip_keywords_severe_warning):
        print("ChatGPT phản hồi rằng bài đăng không phù hợp, cảnh báo nặng")

        # Chuyển sang tab còn lại (Facebook)
        print("Thực hiện chuyển sang Facebook trong hàm handle_response, cảnh báo nặng")
        TabHandle.switch_tab_to(driver, "facebook")
        filter_spam_and_click(post, menu, action_type="super negative")
        write_label("N")
        return

    for keyword in keywords:
        if keyword in response_text:
            print(f"Bài đăng có nội dung hợp lệ ({keyword}), đang đọc file để lấy nội dung comment.")
            comments = read_file(f"info_{profile_location[f"profile{profile_count}"][3]}/{keyword}.txt")

            # Kiểm tra nếu file rỗng hoặc không có nội dung
            if not comments:
                print(f"⚠ File {keyword}.txt không có nội dung, bỏ qua comment.")
                if preprocess_successful:
                    print("Do câu trả lời được lấy từ preprocess_content_stage_2 nên không thực hiện việc chuyển tab")
                    preprocess_successful = False
                    return
                elif not preprocess_successful:
                    print("Thực hiện chuyển sang Facebook trong hàm handle_response")
                    TabHandle.switch_tab_to(driver, "facebook")
                    return

            if preprocess_successful:
                print("Đang thực hiện comment trên facebook bằng hàm comment_on_facebook, comment trực tiếp")
                comment_on_facebook(comments, post, index, menu)
            elif not preprocess_successful:
                print("Đang thực hiện comment trên facebook bằng hàm comment_on_facebook, comment qua ChatGPT")
                comment_on_facebook(comments, post, index, menu)


def comment_on_facebook(comment_list, post, index, menu):
    """Tìm ô comment trên bài đăng hiện tại và nhập nhiều nội dung cùng lúc."""
    global comment_count, reset_flag, pos, tab_bar_height, taskbar_height, dpr, preprocess_successful, content_not_available_anymore, number_of_post_commented
    element_y = 0

    if not preprocess_successful:
        TabHandle.switch_tab_to(driver, "facebook")
        print("Đã thực hiện chuyển sang Facebook trong hàm comment_on_facebook")
        driver.implicitly_wait(2)

    preprocess_successful = False

    random_value = random.random()
    if random_value < 1:
        aligner.scroll_to_post_top(post, menu, dpr, driver, tab_bar_height)
        print("Đang thực hiện hàm filter_spam_and_click chế độ positive")
        filter_spam_and_click(post, menu, action_type="positive")
        write_label("Y")
    try:
        # Cuộn trang xuống để bài đăng ở vị trí phù hợp
        aligner.scroll_to_post_bottom(post, index, dpr, driver, tab_bar_height)
    except StaleElementReferenceException:
        print(f"❌ Bài đăng {pos} đã bị stale")
        reset_flag = True
        print(f"Đã bật reset_flag do bài đăng {pos} bị stale trong comment_on_facebook")
        return

    like_post(post)
    if content_not_available_anymore:
        print("Bài đăng không còn tồn tại, bỏ qua")
        return None

    number_of_post_commented += 1

    while True:
        try:
            # Tìm nút comment
            try:
                comment_box = WebDriverWait(post, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Leave a comment']"))
                )
                print("Đã tìm thấy nút comment")
            except TimeoutException:
                print("Không tìm thấy nút comment bằng aria-label, thử tìm theo data-ad-rendering-role...")
                try:
                    comment_box = post.find_element(By.CSS_SELECTOR, "span[data-ad-rendering-role='comment_button']")
                    print("✅ Đã tìm thấy nút comment bằng data-ad-rendering-role")
                except Exception:
                    try:
                        comment_box = post.find_element(By.XPATH, ".//span[@data-ad-rendering-role='comment_button']")
                        print("✅ Đã tìm thấy nút comment bằng XPath")
                    except Exception:
                        print("❌ Không tìm thấy nút comment, thoát vòng lặp.")
                        return  # Không tìm thấy thì dừng luôn

            # Lấy vị trí của viewport
            viewport_top = driver.execute_script("return window.scrollY;")

            # Tính toán tọa độ click
            element_x = comment_box.location['x'] * dpr
            element_y = (comment_box.location['y'] - viewport_top) * dpr + tab_bar_height  # Điều chỉnh theo viewport
            random_x = random.randint(int(5 * dpr), int(105 * dpr))
            random_y = random.randint(int(3 * dpr), int(29 * dpr))
            end_point = (element_x + random_x, element_y + random_y)

            start_x, start_y = pyautogui.position()

            # Di chuyển chuột đến nút comment và click
            mover.test_move((start_x, start_y), end_point)
            pyautogui.click()
            time.sleep(random.uniform(1, 2))  # Chờ một chút để ô comment hiển thị

            # 🔹 Kiểm tra sự tồn tại của ảnh profileCoverPhoto
            try:
                WebDriverWait(driver, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'img[data-imgperflogname="profileCoverPhoto"]'))
                )
                print("Ấn nhầm vào nhóm rồi nên quay lại trang trước")

                # Ấn quay lại
                pyautogui.hotkey('alt', 'left')
                time.sleep(2)  # Đợi trang tải lại

                # Thử lại việc ấn nút comment
                continue  # Quay lại vòng lặp while để thử lại

            except TimeoutException:
                print("Không phát hiện profileCoverPhoto, tiếp tục bình thường.")
                break  # Nếu không có lỗi, thoát vòng lặp

        except Exception as e:
            print(f"⚠️ Lỗi: {e}, thử lại sau 1s")
            time.sleep(1)
            continue  # Thử lại từ đầu nếu có lỗi

    for idx, comment_text in enumerate(comment_list):
        if idx == 1:  # Chỉ xử lý logic đặc biệt cho comment thứ hai
            print("🔎 Kiểm tra trước khi click vào ô comment...")

            # Kiểm tra xem có nút đóng cửa sổ comment hay không
            try:
                comment_dialog = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.x1n2onr6.x1ja2u2z.x1afcbsf.xdt5ytf.x1a2a7pz.x71s49j.x1qjc9v5.xazwl86.x1hl0hii.x1aq6byr.x2k6n7x.x78zum5.x1plvlek.xryxfnj.xcatxm7.xrgej4m.xh8yej3"
                )

                print("🚪 Cửa sổ comment đã mở sẵn, bỏ qua việc click.")
            except:
                print("🔘 Cửa sổ comment chưa mở, sẽ thực hiện click vào ô comment.")
                try:
                    # Lặp đến khi toạ độ Y hợp lệ
                    while True:
                        comment_box = WebDriverWait(post, 0.5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Leave a comment']"))
                        )
                        print("✅ Đã tìm thấy ô comment")

                        viewport_top = driver.execute_script("return window.scrollY;")
                        element_x = comment_box.location['x'] * dpr
                        element_y = (comment_box.location['y'] - viewport_top) * dpr + tab_bar_height
                        random_x = random.randint(int(5 * dpr), int(105 * dpr))
                        random_y = random.randint(int(3 * dpr), int(29 * dpr))
                        end_point = (element_x + random_x, element_y + random_y)

                        if end_point[1] < (90 * dpr + tab_bar_height):
                            print("🔼 Nút comment nằm quá cao, scroll lên để hiển thị rõ...")
                            scroll.scroll_up_one_time()
                            time.sleep(0.2)
                        else:
                            break  # Toạ độ Y đã hợp lệ → thoát khỏi vòng lặp

                    # Sau khi toạ độ Y hợp lệ, thực hiện click
                    start_x, start_y = pyautogui.position()
                    mover.test_move((start_x, start_y), end_point)
                    pyautogui.click()
                    time.sleep(random.uniform(1, 2))

                    try:
                        WebDriverWait(driver, 0.5).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'img[data-imgperflogname="profileCoverPhoto"]'))
                        )
                        print("⚠️ Click nhầm vào nhóm, quay lại...")
                        pyautogui.hotkey('alt', 'left')
                        time.sleep(2)
                        continue  # Quay lại comment thứ hai
                    except TimeoutException:
                        print("✅ Không phát hiện nhầm nhóm, tiếp tục.")


                except TimeoutException:
                    print("❌ Không tìm thấy ô comment, bỏ qua bước click.")

        # Thực hiện comment như bình thường
        pyperclip.copy(comment_text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(random.uniform(2.5, 3.5))

        pyautogui.press("enter")
        check_and_exit()
        print(f"✅ Đã comment {comment_count + 1}: {comment_text}")
        comment_count += 1
        time.sleep(random.uniform(2.5, 4.5))

    # Đóng cửa sổ comment sau khi hoàn tất
    try:
        # Tìm nút đóng cửa sổ comment bằng đầy đủ danh sách class
        close_button = driver.find_element(
            By.CSS_SELECTOR,
            "div.x1i10hfl.xjqpnuy.xc5r6h4.xqeqjp1.x1phubyo.x13fuv20.x18b5jzi.x1q0q8m5.x1t7ytsu.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx"
            ".xdj266r.x14z9mp.xat24cr.x1lziwak.x2lwn1j.xeuugli.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o"
            ".x1lku1pv.x1a2a7pz.x6s0dn4.x1iwo8zk.x1033uif.x179ill4.x1b60jn0.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.x78zum5"
            ".xl56j7k.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1n2onr6.xc9qbxq.x14qfxbe.x1qhmfi1"
        )

        if close_button:
            print("Đã tìm thấy nút close_button trong cửa sổ comment")

            # Lấy tọa độ của nút đóng cửa sổ comment
            location = close_button.location
            size = close_button.size
            element_x2 = (location['x'] + size['width'] // 2) * dpr
            element_y2 = (location['y'] + size['height'] // 2) * dpr + tab_bar_height

            # Thêm độ lệch ngẫu nhiên
            random_x = random.randint(int(-10 * dpr), int(10 * dpr))
            random_y = random.randint(int(-10 * dpr), int(10 * dpr))
            close_end_point = (element_x2 + random_x, element_y2 + random_y)

            print("Đang di chuyển chuột đến ô X của cửa sổ comment")

            start_x, start_y = pyautogui.position()
            mover.test_move((start_x, start_y), close_end_point)
            pyautogui.click()

    except:
        print("Không có nút đóng cửa sổ comment")

        x_raw = post.location['x']
        x = x_raw * dpr
        size = post.size
        post_width_raw = size['width']
        post_width = post_width_raw * dpr
        random_x = random.randint(int(35 * dpr), int(45 * dpr))
        random_y = random.randint(int(-10 * dpr), int(10 * dpr))
        width, height = pyautogui.size()

        start_x, start_y = pyautogui.position()
        target_x = x + post_width + random_x
        target_y = start_y + random_y

        # Giới hạn tọa độ để không chạm vào tab bar hoặc taskbar
        safe_y_min = tab_bar_height + 10 * dpr  # +10 để tránh dính mép
        safe_y_max = height - taskbar_height - 10 * dpr

        # Nếu vị trí đích nằm ngoài vùng an toàn thì điều chỉnh lại
        if target_y < safe_y_min:
            target_y = safe_y_min
        elif target_y > safe_y_max:
            target_y = safe_y_max

        # Tùy bạn có thể làm tương tự với target_x nếu cần tránh mép trái/phải

        mover.test_move((start_x, start_y), (target_x, target_y))


def like_post(post):
    global content_not_available_anymore

    try:
        like_button = WebDriverWait(post, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Like']"))
        )
        print("👍 Đã tìm thấy nút Like")
    except Exception:
        print("❌ Không tìm thấy nút Like, thoát vòng lặp.")
        return

    # Lấy vị trí của viewport
    viewport_top = driver.execute_script("return window.scrollY;")

    # Tính toán tọa độ click
    element_x = like_button.location['x'] * dpr
    element_y = (like_button.location['y'] - viewport_top) * dpr + tab_bar_height
    random_x = random.randint(int(5 * dpr), int(65 * dpr))
    random_y = random.randint(int(3 * dpr), int(29 * dpr))
    end_point = (element_x + random_x, element_y + random_y)

    start_x, start_y = pyautogui.position()

    # Di chuyển chuột và click
    mover.test_move((start_x, start_y), end_point)
    pyautogui.click()
    time.sleep(random.uniform(0.1, 0.25))
    check_and_exit()
    if content_not_available_anymore:
        return None

    # Kiểm tra nếu ấn nhầm vào trang cá nhân
    try:
        WebDriverWait(driver, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img[data-imgperflogname="profileCoverPhoto"]'))
        )
        print("Ấn nhầm vào nhóm hoặc trang cá nhân, quay lại trang trước.")
        pyautogui.hotkey('alt', 'left')
        time.sleep(2)
        return  # Sau khi quay lại không cần tiếp tục
    except TimeoutException:
        print("Không phát hiện profileCoverPhoto, tiếp tục bình thường.")


def get_post_text_2ndgen(post):
    """
    Hàm trích xuất nội dung bài đăng từ phần tử post.
    Sử dụng các khối try-except lồng nhau để kiểm tra từng loại bài đăng.
    Nếu không khớp với loại nào, sẽ in ra thông báo cuối cùng.
    """

    try:
        # 1️⃣ Bài đăng loại 1 - ảnh nội dung
        try:
            container_v1 = post.find_element(By.CSS_SELECTOR,
                                             'div.x1cy8zhl.x78zum5.x1nhvcw1.x1n2onr6.xh8yej3')
            print("🔍 Đã phát hiện container bài đăng loại 1")

            # Tìm tất cả các khối nội dung trong container
            text_blocks = container_v1.find_elements(By.CSS_SELECTOR,
                                                     'div.xdj266r.x14z9mp.xat24cr.x1lziwak.x1vvkbs')

            combined_text = "\n".join([tb.text.strip() for tb in text_blocks if tb.text.strip()])
            if combined_text:
                print("🟢 Đã phát hiện bài đăng loại 1 (ảnh nội dung)")
                print(f"📜 Nội dung bài đăng:\n{combined_text}")
                return combined_text
            else:
                print("❌ Không tìm thấy nội dung bài đăng loại 1 (ảnh nội dung)")

        except Exception:
            print("❌ Không tìm thấy nội dung bài đăng loại 1 (ảnh nội dung)")

        # 2️⃣ Bài đăng loại 2 - bài viết dạng văn bản thường
        try:
            container_v2 = post.find_element(By.CSS_SELECTOR,
                                             '.x6zurak.x18bv5gf.x184q3qc.xqxll94.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1yc453h.x1lliihq.xzsf02u.xlh3980.xvmahel.x1x9mg3.xo1l8bm')
            print("🔍 Đã phát hiện container bài đăng loại 2 (văn bản thường)")

            # Tìm toàn bộ div hoặc span có dir="auto" nằm sâu bên trong
            text_elements = container_v2.find_elements(By.CSS_SELECTOR, 'div[dir="auto"], span[dir="auto"]')

            # Duyệt qua từng phần tử, lấy text nếu có nội dung
            collected_lines = []
            for el in text_elements:
                text = el.text.strip()
                if text:
                    collected_lines.append(text)

            if collected_lines:
                text_v2 = '\n'.join(collected_lines)
                print("🟢 Đã phát hiện bài đăng loại 2 (văn bản thường)")
                print(f"📜 Nội dung bài đăng:\n{text_v2}")
                return text_v2

            print("❌ Không tìm thấy nội dung bài đăng loại 2 (văn bản thường)")
        except Exception as e:
            print("❌ Không tìm thấy nội dung bài đăng loại 2 (văn bản thường)")

        # 3️⃣ Bài đăng loại 3 - văn bản in đậm, không ảnh
        try:
            container_v3 = post.find_element(By.CSS_SELECTOR,
                                             'div.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xf7dkkf.xv54qhq.x18d9i69')
            print("🔍 Đã phát hiện container bài đăng loại 3")

            spans_v3 = container_v3.find_elements(By.CSS_SELECTOR,
                                                  'span.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1hl2dhg.x16tdsg8.x1vvkbs.xzsf02u.xngnso2.xo1l8bm.x1qb5hxa')

            all_lines = []
            for span in spans_v3:
                divs = span.find_elements(By.CSS_SELECTOR,
                                          'div.xdj266r.x14z9mp.xat24cr.x1lziwak.x1vvkbs')
                for div in divs:
                    text = div.text.strip()
                    if text:
                        all_lines.append(text)

            if all_lines:
                full_text_v3 = '\n'.join(all_lines)
                print("🟢 Đã phát hiện bài đăng loại 3 (văn bản in đậm, không ảnh)")
                print(f"📜 Nội dung bài đăng:\n{full_text_v3}")
                return full_text_v3
            else:
                print("❌ Không tìm thấy nội dung trong container bài đăng loại 3")
        except Exception as e:
            print("❌ Không tìm thấy nội dung bài đăng loại 3 (văn bản in đậm, không ảnh)")


        # 4️⃣ Bài đăng loại 4 - văn bản có ảnh
        try:
            container_v4 = post.find_element(By.CSS_SELECTOR,
                                             'div.xdj266r.x14z9mp.xat24cr.x1lziwak.xv54qhq.xf7dkkf.x1iorvi4.xsag5q8')
            print("🔍 Đã phát hiện container bài đăng loại 4")

            spans_v4 = container_v4.find_elements(By.CSS_SELECTOR,
                                                  'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x6prxxf.xvq8zen.xo1l8bm.xzsf02u')

            all_lines = []
            for span in spans_v4:
                text = span.text.strip()
                if text:
                    all_lines.append(text)

            if all_lines:
                full_text_v4 = '\n'.join(all_lines)
                print("🟢 Đã phát hiện bài đăng loại 4 (văn bản có ảnh)")
                print(f"📜 Nội dung bài đăng:\n{full_text_v4}")
                return full_text_v4
            else:
                print("❌ Không tìm thấy nội dung trong container bài đăng loại 4")
        except Exception as e:
            print("❌ Không tìm thấy nội dung bài đăng loại 4 (văn bản có ảnh)")

        # 5️⃣ Bài đăng loại 5 - bài viết nhúng iframe hoặc liên kết ngoài (YouTube, báo chí...)
        try:
            container_v5_root = post.find_element(By.CSS_SELECTOR,
                                                  'div.x1l90r2v.x1iorvi4.x1g0dm76.xpdmqnj[data-ad-comet-preview="message"][data-ad-preview="message"]')

            print("🔍 Đã phát hiện container gốc của bài đăng loại 5")

            container_v5 = container_v5_root.find_element(By.CLASS_NAME,
                                                          'html-div')

            print("🔍 Đã phát hiện vùng chứa nội dung iframe của bài đăng loại 5")

            span_elements_v5 = container_v5.find_elements(By.TAG_NAME, 'span')

            all_lines_v5 = []
            for span in span_elements_v5:
                text = span.text.strip()
                if text:
                    all_lines_v5.append(text)

            # Ngoài ra, có thể có một số đoạn text không nằm trong <span>, nằm trực tiếp trong <div>
            div_elements_v5 = container_v5.find_elements(By.TAG_NAME, 'div')
            for div in div_elements_v5:
                text = div.text.strip()
                if text and text not in all_lines_v5:
                    all_lines_v5.append(text)

            if all_lines_v5:
                full_text_v5 = '\n'.join(all_lines_v5)
                print("🟢 Đã phát hiện bài đăng loại 5 (iframe/liên kết ngoài)")
                print(f"📜 Nội dung bài đăng:\n{full_text_v5}")
                return full_text_v5
            else:
                print("❌ Không tìm thấy nội dung trong container bài đăng loại 5")
        except Exception as e:
            print("❌ Không tìm thấy nội dung bài đăng loại 5 (iframe/liên kết ngoài)")

        # 6️⃣ Bài đăng loại 6 - văn bản thường không ảnh, kết hợp in đậm, in nghiêng
        try:
            container_v6_root = post.find_element(By.CSS_SELECTOR,
                                                  'div#_r_p9_.html-div.xdj266r.x14z9mp.xat24cr.x1lziwak.xv54qhq.xf7dkkf.x1iorvi4.x18d9i69')

            print("🔍 Đã phát hiện container gốc bài đăng loại 6")

            # Tìm tất cả các <div> con chứa từng đoạn văn bản hoặc phần tử có in đậm, in nghiêng
            paragraph_divs_v6 = container_v6_root.find_elements(By.CSS_SELECTOR,
                                                                'div.html-div.xdj266r.x14z9mp.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1e56ztr')

            all_lines_v6 = []
            for div in paragraph_divs_v6:
                # Lấy text trong <span> bên trong <div> này
                span_elements = div.find_elements(By.CSS_SELECTOR,
                                                  'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x6prxxf.xvq8zen.xo1l8bm.xzsf02u')

                for span in span_elements:
                    text = span.text.strip()
                    if text:
                        all_lines_v6.append(text)

            if all_lines_v6:
                full_text_v6 = '\n'.join(all_lines_v6)
                print("🟢 Đã phát hiện bài đăng loại 6 (văn bản thường không ảnh, có in đậm)")
                print(f"📜 Nội dung bài đăng:\n{full_text_v6}")
                return full_text_v6
            else:
                print("❌ Không tìm thấy nội dung trong container bài đăng loại 6")
        except Exception as e:
            print("❌ Không tìm thấy nội dung bài đăng loại 6 (văn bản thường không ảnh, có in đậm)")

        # 7️⃣ Bài đăng loại 7 - văn bản thường, có nhiều dòng, không ảnh
        try:
            # Bọc ngoài là <span> với class đặc trưng
            wrapper_span_v7 = post.find_element(By.CSS_SELECTOR,
                                                'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x6prxxf.xvq8zen.xo1l8bm.xzsf02u.x1yc453h')

            print("🔍 Đã phát hiện wrapper <span> bài đăng loại 7")

            # Tìm div chứa nội dung văn bản bên trong
            content_container_v7 = wrapper_span_v7.find_element(By.CSS_SELECTOR,
                                                                'div.xdj266r.x14z9mp.xat24cr.x1lziwak.x1vvkbs.x126k92a')

            # Tìm tất cả các <div> dòng văn bản thực tế bên trong (style: text-align: start)
            line_divs_v7 = content_container_v7.find_elements(By.CSS_SELECTOR, 'div[dir="auto"]')

            all_lines_v7 = []
            for div in line_divs_v7:
                line = div.text.strip()
                if line:
                    all_lines_v7.append(line)

            if all_lines_v7:
                full_text_v7 = '\n'.join(all_lines_v7)
                print("🟢 Đã phát hiện bài đăng loại 7 (văn bản thường, nhiều dòng)")
                print(f"📜 Nội dung bài đăng:\n{full_text_v7}")
                return full_text_v7
            else:
                print("❌ Không tìm thấy nội dung trong bài đăng loại 7")
        except Exception as e:
            print("❌ Không tìm thấy bài đăng loại 7 (văn bản thường, nhiều dòng)")

        # 8️⃣ Bài đăng loại 8 - in đậm không ảnh
        try:
            # Bọc ngoài bắt đầu từ div có ID và class đặc trưng
            wrapper_div_v8 = post.find_element(By.CSS_SELECTOR,
                                               'div#_r_6b_.html-div.xdj266r.x14z9mp.xat24cr.x1lziwak.x1l90r2v.xv54qhq.xf7dkkf.x1iorvi4')

            print("🔍 Đã phát hiện wrapper <div> bài đăng loại 8")

            # Tìm <span> có inline style chứa fontSize (dấu hiệu in đậm, phông lớn)
            outer_span_v8 = wrapper_div_v8.find_element(By.CSS_SELECTOR,
                                                        'span.x6zurak.x18bv5gf.x193iq5w.xeuugli.x13faqbe.x1vvkbs.xt0psk2.xzsf02u.xlh3980.xvmahel.x1x9mg3.xo1l8bm[style*="fontSize"]')

            # Bên trong thường là <strong> chứa nội dung chính
            strong_element = outer_span_v8.find_element(By.TAG_NAME, 'strong')

            text_v8 = strong_element.text.strip()

            if text_v8:
                print("🟢 Đã phát hiện bài đăng loại 8 (in đậm, không ảnh)")
                print(f"📜 Nội dung bài đăng:\n{text_v8}")
                return text_v8
            else:
                print("❌ Không tìm thấy nội dung trong bài đăng loại 8")
        except Exception as e:
            print("❌ Không tìm thấy bài đăng loại 8 (in đậm, không ảnh)")

        # 9️⃣ Bài đăng loại 9 - in đậm loại 2 (trong thẻ <h5>)
        try:
            # Bắt đầu từ thẻ <h5> với full class
            h5_element_v9 = post.find_element(By.CSS_SELECTOR,
                                              'h5.html-h5.xdj266r.x14z9mp.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1vvkbs.x1heor9g.x1qlqyl8.x1pd3egz.x1a2a7pz.xod5an3')

            print("🔍 Đã phát hiện thẻ <h5> bài đăng loại 9")

            # Tìm <span> chứa nội dung chính
            outer_span_v9 = h5_element_v9.find_element(By.CSS_SELECTOR,
                                                       'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1603h9y.x1u7k74.xo1l8bm.xzsf02u')

            # Bên trong là <strong> chứa nội dung
            strong_v9 = outer_span_v9.find_element(By.TAG_NAME, 'strong')

            text_v9 = strong_v9.text.strip()

            if text_v9:
                print("🟢 Đã phát hiện bài đăng loại 9 (in đậm, trong h5)")
                print(f"📜 Nội dung bài đăng:\n{text_v9}")
                return text_v9
            else:
                print("❌ Không tìm thấy nội dung trong bài đăng loại 9")
        except Exception as e:
            print("❌ Không tìm thấy bài đăng loại 9 (in đậm, trong h5)")


    except Exception:
        print("⚠️ Không xác định được loại bài đăng phù hợp")
        return None


def get_group_name(post):
    try:
        # Danh sách các class cần thử theo thứ tự
        group_class_selectors = [
            "a.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xkrqix3.x1sur9pj.xzsf02u.x1s688f",
            "a.x1i10hfl.xjbqb8w.x1ejq31n.x18oe1m7.x1sy0etr.xstzfhl.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xkrqix3.x1sur9pj.xzsf02u.x1s688f"
        ]

        for selector in group_class_selectors:
            group_links = post.find_elements(By.CSS_SELECTOR, selector)

            for group_link in group_links:
                try:
                    # TH1: Nếu trong <a> có thẻ <span>, ưu tiên lấy text của <span>
                    span = group_link.find_element(By.XPATH, ".//span")
                    name = span.text.strip()
                    if name:
                        return name
                except:
                    pass

                # TH2: Nếu không có <span>, lấy text trực tiếp từ <a>
                name = group_link.text.strip()
                if name:
                    return name

        print("Không tìm thấy tên nhóm.")
        return None

    except Exception as e:
        print("Lỗi khi lấy tên nhóm:", e)
        return None


def check_and_exit():
    global content_not_available_anymore
    # print("Đang thực hiện check_and_exit")

    # Danh sách các từ khóa cảnh báo không quan trọng
    unimportant_warning = ["remove", "available", "exist"]

    try:
        # Tìm phần tử cảnh báo
        alert_element = driver.find_element("css selector",
                                            '.x1n2onr6.x1ja2u2z.x1afcbsf.xdt5ytf.x1a2a7pz.x71s49j.x1qjc9v5.xazwl86.x1hl0hii.x1aq6byr.x2k6n7x.x78zum5.x1plvlek.xryxfnj.xcatxm7.x1n7qst7.xh8yej3')

        if alert_element.is_displayed():
            try:
                # Tìm thêm phần tử kiểm tra nội dung (cách 1)
                content_element = alert_element.find_element("css selector",
                                                      '.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xtoi2st.x3x7a5m.x1603h9y.x1u7k74.x1xlr1w8.xzsf02u.x2b8uid')
                content_text = content_element.text.strip()
                print(f"Tiêu đề cảnh báo là {content_text}")

            except NoSuchElementException:
                try:
                    # Nếu không tìm thấy bằng cách 1, thử cách 2 với class cụ thể của <span>
                    content_element = alert_element.find_element(
                        By.CSS_SELECTOR,
                        "span.x6zurak.x18bv5gf.x184q3qc.xqxll94.x1s928wv.xhkezso.x1gmr53x."
                        "x1cpjm7i.x1fgarty.x1943h6x.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x2b8uid."
                        "x1lliihq.xzsf02u.xlh3980.xvmahel.x1x9mg3.x1xlr1w8"
                    )
                    content_text = content_element.text.strip()
                    print(f"Tiêu đề cảnh báo là {content_text}")


                except NoSuchElementException:
                    # Không tìm thấy nội dung => xử lý như cảnh báo thật
                    print("Không tìm thấy nội dung bài đăng. Xử lý như cảnh báo SPAM.")
                    now = datetime.now()
                    print(f"Thời gian hiện tại là: {now.strftime('%H:%M:%S')}")
                    subject = f"Tài khoản {profile_location[f'profile{profile_count}'][2]} tạm thời bị khoá"
                    body = f"Thời gian: {now.strftime('%H:%M:%S')}\nĐã comment: {comment_count}"
                    SendingGmail.send_email(subject, body, receiver_email)
                    sys.exit(0)

            # Xử lý sau khi đã lấy được content_text
            if any(keyword.lower() in content_text.lower() for keyword in unimportant_warning):
                print("Phát hiện cảnh báo không quan trọng (chứa từ khóa trong danh sách). Tiếp tục chạy.")
                content_not_available_anymore = True
                pass  # Bài đăng không tồn tại, tiếp tục chạy
            else:
                # Nội dung khác => cảnh báo thật, gửi email và dừng chương trình
                print("Phát hiện cảnh báo SPAM! Dừng chương trình ngay lập tức.")
                now = datetime.now()
                print(f"Thời gian hiện tại là: {now.strftime('%H:%M:%S')}")
                subject = f"Tài khoản {profile_location[f'profile{profile_count}'][2]} tạm thời bị khoá"
                body = f"Thời gian: {now.strftime('%H:%M:%S')}\nĐã comment: {comment_count}"
                SendingGmail.send_email(subject, body, receiver_email)
                sys.exit(0)

    except NoSuchElementException:
        pass  # Không có cảnh báo, tiếp tục chạy


def search_menu_bar():
    try:
        # Thử chờ tối đa 5 giây để tìm menu bằng MENU_SELECTOR
        try:
            menu = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, MENU_SELECTOR))
            )
        except Exception:
            # Nếu không tìm thấy bằng MENU_SELECTOR thì thử cách thứ hai
            try:
                menu = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "xtijo5x.x1o0tod.xixxii4.x13vifvy.x1vjfegm"))
                )
            except Exception as e:
                print(f"❌ Không tìm thấy thanh menu bằng cả hai cách: {e}")
                return None

        if menu:
            try:
                # In nội dung bên trong menu
                # outer_html = menu.get_attribute("outerText")  # hoặc "outerHTML" nếu muốn xem cả thẻ HTML
                print("✅ Đã tìm thấy thanh menu trong search_menu_bar")
                # print(outer_html)
            except Exception as e:
                print(f"⚠️ Không thể lấy nội dung menu: {e}")
            return menu
        else:
            print("⚠️ Phần tử menu là None hoặc không hợp lệ.")
            return None

    except Exception as e:
        print(f"❌ Lỗi khi tìm thanh Menu: {e}")
        print("🔌 Đã ngắt kết nối driver.")
        driver.quit()
        sys.exit(0)



def preprocess_content_stage_1(post):
    try:
        selector = (
            ".xz74otr.x15mokao.x1ga7v0g.x16uus16.xbiv7yw.x1ey2m1c.xtijo5x.x5yr21d.x10l6tqk.x1o0tod.x13vifvy.xh8yej3"
        )

        matched_elements = post.find_elements(By.CSS_SELECTOR, selector)

        if len(matched_elements) > 1:
            print(
                "Bài đăng không hợp lệ do chứa nhiều hơn 1 ảnh, nghi ngờ là bài đăng mời thuê trọ, trả về cảnh báo cấp 2")
            return True
        else:
            return False

    except:
        pass

    return None  # Nội dung hợp lệ


def preprocess_content_stage_2(post_content, group_name):
    global preprocess_successful
    """
    Kiểm tra nội dung bài đăng trước khi gửi lên ChatGPT.
    Nếu nội dung chứa từ khóa không hợp lệ, trả về thông báo hoặc mã đặc biệt.
    """

    for keyword in post_content_invalid_keywords1:
        if keyword.lower() in post_content.lower():
            response_text = f"❌ Nội dung bài đăng không hợp lệ do chứa từ khóa: '{keyword}', trả về cảnh báo cấp 1"
            print(response_text)
            return "Y2"

    for keyword in post_content_valid_keywords:
        if keyword.lower() in post_content.lower():
            print("Phát hiện từ khoá được phép trong hàm preprocess_content")

            group_name_lower = group_name.lower()
            for kw in group_keywords_A1:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A1"
            for kw in group_keywords_A2:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A2"
            for kw in group_keywords_A3:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A3"
            for kw in group_keywords_A5:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A5"
            for kw in group_keywords_A6:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A6"
            for kw in group_keywords_A7:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A7"
            for kw in group_keywords_A8:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A8"
            for kw in group_keywords_A9:
                if kw in group_name_lower:
                    preprocess_successful = True
                    return "A9"
            break

    for keyword in post_content_invalid_keywords2:
        if keyword.lower() in post_content.lower():
            response_text = f"❌ Nội dung bài đăng không hợp lệ do chứa từ khóa: '{keyword}', trả về cảnh báo cấp 1"
            print(response_text)
            return "Y2"

    for keyword in post_content_extreme_invalid_keywords:
        if keyword.lower() in post_content.lower():
            response_text = f"❌ Bài đăng không hợp lệ do chứa từ khóa nằm trong extreme_invalid: '{keyword}', trả về cảnh báo cấp 2"
            print(response_text)
            return "Y1"

    return None  # Nội dung hợp lệ


def wait_for_response_content(driver, conversation_turn, timeout=30):
    """
    Chờ đợi cho đến khi nội dung của response_block chứa một trong các mã báo hiệu thành công.
    Nếu chưa có, tiếp tục lấy response_block mới mỗi 1s cho đến khi timeout.
    """
    try_time = 1
    response_block = None

    start_time = time.time()
    valid_signals = {"X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8",
                     "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "Z1"}

    while time.time() - start_time < timeout:
        try:
            # Lấy lại last_response trong mỗi lần lặp
            last_response = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"article[data-testid='conversation-turn-{conversation_turn}']"))
            )

            print("Đã lấy được last_response")

            # Lấy lại response_block
            if theme:
                response_block = WebDriverWait(last_response, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.markdown.prose.w-full.break-words.dark"))
                )

            elif not theme:
                response_block = WebDriverWait(last_response, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.markdown.prose.w-full.break-words.light"))
                )

            print("📩 Đã lấy được response_block...")
            # print(f"Nội dung của response_block lấy lần {try_time} (innerText):\n{response_block.get_attribute('innerText')}")
            try_time += 1

            # Kiểm tra nội dung của response_block
            response_text = "\n".join([elem.text for elem in response_block.find_elements(By.XPATH, ".//*")])

            # Kiểm tra mã báo hiệu thành công
            if any(signal in response_text for signal in valid_signals):
                # print(f"✅ Đã phát hiện tín hiệu thành công: {response_text}")
                return response_text

        except:
            print(f"⚠️ Lỗi khi lấy lại response_block")

        time.sleep(0.5)  # Chờ 1 giây rồi kiểm tra lại

    print("❌ Hết thời gian chờ, không tìm thấy tín hiệu thành công.")
    return None


def analyze_group_name(group_name, post):
    global group_name_valid_keywords

    if group_name is None:
        return False

    group_name = group_name.lower()

    for keyword in group_name_valid_keywords:
        if keyword in group_name:
            return True

    # Dùng Selenium để tìm phần tử đặc biệt trong post
    try:
        post.find_element(
            By.CSS_SELECTOR,
            'div.html-div.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x14vqqas.x6ikm8r.x10wlt62'
        )
        return True
    except:
        return False


def check_tabs_open(driver):
    print("Đang thực hiện việc kiểm tra số tab đang mở hiện tại")
    all_tabs = driver.window_handles

    # Lưu lại tab hiện tại để quay về sau khi in tên các tab
    current_tab = driver.current_window_handle

    valid_tabs = []

    for index, handle in enumerate(all_tabs):
        driver.switch_to.window(handle)
        title = driver.title
        print(f"Tab {index + 1} tiêu đề: {title}")

        # Bỏ qua tab có tiêu đề "Tab search" hoặc rỗng
        if title.strip().lower() != "tab search":
            valid_tabs.append(handle)

    # Quay về tab ban đầu
    driver.switch_to.window(current_tab)

    print("Kiểm tra driver trước khi kết thúc check_tabs_open")
    driver = check_driver_and_reconnect(driver)

    print(f"Số tab hợp lệ đang mở: {len(valid_tabs)}")
    return True if len(valid_tabs) == 2 else False



def filter_spam_and_click(post, menu, action_type):
    global reset_facebook_web_time, pos, reset_flag

    aligner.scroll_to_post_top_for_filter(post, menu, dpr, driver, tab_bar_height)
    time.sleep(0.4)

    menu_bottom = 0

    # Lấy vị trí của viewport
    viewport_top = driver.execute_script("return window.scrollY;")

    # Xác định tên nút và từ khóa in ra tương ứng
    if action_type == "positive":
        button_text = "Interested"
        log_action = "Interested"
        stay_to_watch_rate = random.random()
        if stay_to_watch_rate < 0.4:
            time.sleep(random.uniform(4, 6))
    elif action_type == "negative":
        button_text = "Not interested"
        log_action = "Not interested"
    elif action_type == "super negative":
        button_text = "Hide post"
        log_action = "Hide post"
    else:
        print("Tham số action_type không hợp lệ. Chỉ chấp nhận 'positive' hoặc 'negative' hoặc 'super negative'.")
        return

    try:
        # Lấy vị trí con chuột hiện tại
        current_mouse_pos = pyautogui.position()
        start_point1 = current_mouse_pos  # Sử dụng vị trí hiện tại của con chuột làm start_point

        # Tìm nút ba chấm chứa menu (dropdown)
        try:
            three_dots_button = post.find_element(By.CSS_SELECTOR, '[aria-label="Actions for this post"]')
            print("Đã tìm thấy nút ba chấm (Actions for this post)")
        except NoSuchElementException:
            print("Không tìm thấy nút ba chấm.")
            return

        # Lấy vị trí của nút ba chấm
        button_location = three_dots_button.location
        button_size = three_dots_button.size
        button_center_x = (button_location['x'] + button_size['width'] / 2) * dpr
        button_center_y = (button_location['y'] + (button_size['height'] / 2) - viewport_top) * dpr + tab_bar_height

        random_x = random.randint(int(-6 * dpr), int(6 * dpr))
        random_y = random.randint(int(-6 * dpr), int(6 * dpr))

        # Tính vị trí đích
        end_point1 = (button_center_x + random_x, button_center_y + random_y)

        # Lấy kích thước màn hình
        _, screen_height = pyautogui.size()

        menu_bottom = menu.location['y'] + menu.size['height'] - viewport_top
        if menu_bottom < 0:
            menu_bottom = 0

        # Giới hạn chiều cao hợp lệ (chỉ xét theo Y)
        safe_y_min = tab_bar_height + 10 * dpr + menu_bottom
        safe_y_max = screen_height - taskbar_height - 10 * dpr

        # Nếu Y vượt quá viewport thì bỏ qua
        if not (safe_y_min <= end_point1[1] <= safe_y_max):
            return None  # Không di chuyển nếu Y nằm ngoài vùng hợp lệ

        # Di chuyển chuột đến vị trí của nút ba chấm
        mover.test_move(start_point1, end_point1)
        print("Đã ấn nút 3 chấm action_for_this_post")

        # Click vào nút ba chấm để mở menu
        pyautogui.click()
        time.sleep(1)

        try:
            # Chờ cửa sổ "Actions for this post" xuất hiện với class mới
            try:
                actions_window = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'div[aria-label="Feed story"]'
                    ))
                )
            except:
                # Cách 2: Tìm theo full class
                actions_window = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'div.html-div.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.xezm23g.xwtykhg.x1lcr5pl.x1sa2p9j.x1py5zv9.xw5cjc7.x1vsv7so.xau1kf4.x18runqf.x1w7qqtc.xgfcmlh.x174in1k.x4ruge8.xel12sy.x8ro2h5.xd3bsdi.x8ii3r7.x9f619.x6ikm8r.x10wlt62.x1ga7v0g'
                    ))
                )
            print("Đã tìm thấy cửa sổ 'Actions for this post'")

            # Chờ tối đa 5 giây để nút mong muốn xuất hiện trong cửa sổ này
            target_button = WebDriverWait(actions_window, 2).until(
                EC.element_to_be_clickable((By.XPATH, f'.//span[text()="{button_text}"]'))
            )
            print(f"Đã tìm thấy nút '{log_action}' trong cửa sổ hành động.")

        except (TimeoutException, NoSuchElementException):
            print(f"Không tìm thấy cửa sổ hoặc nút '{log_action}'")
            pyautogui.press('esc')
            time.sleep(0.3)

            if action_type == "super negative":
                find_x_hide_post_and_click(post, dpr, tab_bar_height, menu)
                find_and_click_snooze_button(post)

            screen_width, screen_height = pyautogui.size()
            start_x, start_y = pyautogui.position()
            random_y2 = random.uniform(-20 * dpr, 0)
            target_y = start_y + random_y2
            print(f"target_y = {target_y}")
            print(f"menu_bottom = {menu_bottom}")
            random_y1 = random.uniform(15, 20)

            # Clamp theo chiều Y để không ra khỏi viewport (trên tab hoặc dưới taskbar)
            if target_y < tab_bar_height + menu_bottom + 30:
                print(f"tab_bar_height + menu_bottom = {tab_bar_height + menu_bottom}")
                target_y = tab_bar_height + (menu_bottom + random_y1) * dpr
                print(f"target_y mới là {target_y}")
            elif target_y > screen_height - taskbar_height:
                print(f"screen_height - taskbar_height = {screen_height - taskbar_height}")
                target_y = screen_height - taskbar_height - random_y1 * dpr
                print(f"target_y mới là {target_y}")

            mover.test_move((start_x, start_y), (start_x + 80 * dpr, target_y))

            pyautogui.click()
            return None

        # Lấy vị trí của nút
        button_location = target_button.location
        button_size = target_button.size

        screen_width, screen_height = pyautogui.size()

        random_x1 = random.randint(int(-80 * dpr), int(100 * dpr))
        random_y1 = random.randint(int(-2 * dpr), int(10 * dpr))

        button_center_x = (button_location['x'] + button_size['width'] / 2) * dpr
        button_center_y = (button_location['y'] + (button_size['height'] / 2) - viewport_top) * dpr + tab_bar_height

        # Tính toạ độ đích
        target_x = button_center_x + random_x1
        target_y = button_center_y + random_y1

        # Nếu vượt khỏi viewport theo chiều Y thì thôi không ấn nữa
        if target_y < tab_bar_height + menu_bottom * dpr or target_y > screen_height - taskbar_height:
            print(f"Nút '{log_action}' nằm ngoài tầm viewport của trang web")
            pyautogui.press('esc')
            time.sleep(0.3)

            if action_type == "super negative":
                find_x_hide_post_and_click(post, dpr, tab_bar_height, menu)
                find_and_click_snooze_button(post)

            screen_width, screen_height = pyautogui.size()
            start_x, start_y = pyautogui.position()
            random_y2 = random.uniform(-20 * dpr, 0)
            target_y = start_y + random_y2

            # Clamp theo chiều Y để không ra khỏi viewport (trên tab hoặc dưới taskbar)
            if target_y < tab_bar_height:
                target_y = tab_bar_height + 10 * dpr
            elif target_y > screen_height - taskbar_height:
                target_y = screen_height - taskbar_height - 10 * dpr

            mover.test_move((start_x, start_y), (start_x + 70 * dpr, target_y))

            pyautogui.click()
            return None

        start_point = pyautogui.position()
        end_point = (target_x, target_y)
        mover.test_move(start_point, end_point)

        # Click nút
        pyautogui.click()
        time.sleep(0.5)

        if log_action == "Hide post":
            check_and_press_esc(driver)

            x_raw = post.location['x']
            x = x_raw * dpr
            size = post.size
            post_width_raw = size['width']
            post_width = post_width_raw * dpr
            random_x = random.randint(int(35 * dpr), int(45 * dpr))
            random_y = random.randint(int(-10 * dpr), int(10 * dpr))
            width, height = pyautogui.size()

            start_x, start_y = pyautogui.position()
            target_x = x + post_width + random_x
            target_y = start_y + random_y

            # Giới hạn tọa độ để không chạm vào tab bar hoặc taskbar
            safe_y_min = tab_bar_height + 10 * dpr  # +10 để tránh dính mép
            safe_y_max = height - taskbar_height - 10 * dpr

            # Nếu vị trí đích nằm ngoài vùng an toàn thì điều chỉnh lại
            if target_y < safe_y_min:
                target_y = safe_y_min
            elif target_y > safe_y_max:
                target_y = safe_y_max

            mover.test_move((start_x, start_y), (target_x, target_y))

            find_and_click_snooze_button(post)

        print(f"Đã lọc bài đăng và ấn '{log_action}'.")

        if log_action != "Interested":
            x_raw = post.location['x']
            x = x_raw * dpr
            size = post.size
            post_width_raw = size['width']
            post_width = post_width_raw * dpr
            random_x = random.randint(int(35 * dpr), int(45 * dpr))
            random_y = random.randint(int(-10 * dpr), int(10 * dpr))
            width, height = pyautogui.size()

            start_x, start_y = pyautogui.position()
            target_x = x + post_width + random_x
            target_y = start_y + random_y

            # Giới hạn tọa độ để không chạm vào tab bar hoặc taskbar
            safe_y_min = tab_bar_height + 10 * dpr  # +10 để tránh dính mép
            safe_y_max = height - taskbar_height - 10 * dpr

            # Nếu vị trí đích nằm ngoài vùng an toàn thì điều chỉnh lại
            if target_y < safe_y_min:
                target_y = safe_y_min
            elif target_y > safe_y_max:
                target_y = safe_y_max

            mover.test_move((start_x, start_y), (target_x, target_y))

    except Exception as e:
        print(f"Bài đăng này không có nút '{log_action}' hoặc có lỗi xảy ra: {e}")
        pyautogui.press('esc')
        time.sleep(0.3)

        screen_width, screen_height = pyautogui.size()
        start_x, start_y = pyautogui.position()
        random_y2 = random.uniform(-20 * dpr, 0)
        target_y = start_y + random_y2

        # Clamp theo chiều Y để không ra khỏi viewport (trên tab hoặc dưới taskbar)
        if target_y < tab_bar_height + menu_bottom * dpr:
            target_y = tab_bar_height + (menu_bottom + 10) * dpr
        elif target_y > screen_height - taskbar_height:
            target_y = screen_height - taskbar_height - 10 * dpr

        mover.test_move((start_x, start_y), (start_x + 70 * dpr, target_y))

        pyautogui.click()
        return None


def find_x_hide_post_and_click(post, dpr, tab_bar_height, menu):
    print("Đang thực hiện hàm find_x_hide_post_and_click")
    try:
        target_class = "x1i10hfl xjqpnuy xc5r6h4 xqeqjp1 x1phubyo x13fuv20 x18b5jzi x1q0q8m5 x1t7ytsu x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x14z9mp xat24cr x1lziwak x2lwn1j xeuugli x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x6s0dn4 x1iwo8zk x1033uif x179ill4 x1b60jn0 x972fbf x10w94by x1qhh985 x14e42zd x9f619 x78zum5 xl56j7k xexx8yu xyri2b x18d9i69 x1c1uobl x1n2onr6 xc9qbxq x14qfxbe xjbqb8w"
        button = post.find_element(By.CSS_SELECTOR, f'a[class="{target_class}"]')
        print("Đã tìm thấy nút X - Hide post trong bài đăng")

        location = button.location_once_scrolled_into_view
        size = button.size

        # Tính vị trí trung tâm của nút
        center_x = int(location['x'] + size['width'] / 2 + random.randint(-4, 4))
        center_y = int(location['y'] + size['height'] / 2 + random.randint(-4, 4))

        # Lấy vị trí chuột hiện tại
        viewport_top = driver.execute_script("return window.scrollY;")
        start_point = pyautogui.position()
        end_point = (center_x * dpr, (center_y - viewport_top) * dpr + tab_bar_height)

        # ===== THÊM CƠ CHẾ AN TOÀN =====
        menu_bottom = menu.location['y'] + menu.size['height'] - viewport_top
        screen_width, screen_height = pyautogui.size()
        if menu_bottom < 0:
            menu_bottom = 0

        # Giới hạn toạ độ Y hợp lệ
        safe_y_min = tab_bar_height + 10 * dpr + menu_bottom
        safe_y_max = screen_height - taskbar_height - 10 * dpr

        if not (safe_y_min <= end_point[1] <= safe_y_max):
            return None  # Không di chuyển nếu Y vượt vùng an toàn

        # Di chuyển và click
        mover.test_move(start_point, end_point)
        pyautogui.click()
        print("Đã ấn nút X - Hide post trong bài đăng")

    except Exception:
        print(f"Không tìm thấy nút Hide Post trong hàm find_x_hide_post_and_click")


def check_and_press_esc(driver):
    try:
        # Tìm phần tử theo toàn bộ dãy class bằng CSS selector
        element = driver.find_element(
            By.CSS_SELECTOR,
            'div.x1n2onr6.x1ja2u2z.x1afcbsf.x78zum5.xdt5ytf.x1a2a7pz.x6ikm8r.x10wlt62.x71s49j.x1jx94hy.x1qpq9i9.xdney7k.xu5ydu1.xt3gfkd.x104qc98.x1g2kw80.x16n5opg.xl7ujzl.xhkep3z.x1n7qst7.xh8yej3'
        )
        print("Phát hiện ấn truợt nút report")
        time.sleep(0.5)
        pyautogui.press('esc')
    except NoSuchElementException:
        # Không tìm thấy, không làm gì cả
        pass


def find_and_click_snooze_button(post):
    global dpr, tab_bar_height, group_name_valid_keywords
    count = 0
    print("Đang thực hiện hàm find_and_click_snooze_button")

    try:
        containers = post.find_elements(By.CSS_SELECTOR,
                                        'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.xeuugli.x1iyjqo2'
                                        )
        print("Đã tìm thấy danh sách nút bấm trong cửa sổ Action for this post")

        valid_buttons = []

        for container in containers:
            count += 1
            print(f"Đã phát hiện nút bấm #{count}")

            # ✅ Thử selector đầu tiên
            spans = container.find_elements(
                By.CSS_SELECTOR,
                'span.x6zurak.x18bv5gf.x184q3qc.xqxll94.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1yc453h.x1lliihq.xzsf02u.xlh3980.xvmahel.x1x9mg3.xk50ysn, '  # class cũ
                'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x6prxxf.xvq8zen.xk50ysn.xzsf02u.x1yc453h'
                # class mới
            )

            if spans:
                print("Đã tìm thấy spans trong hàm find_and_click_snooze_button")

                for span in spans:
                    text = span.text.strip().lower()
                    print(f"Tiêu đề nút bấm là: {text}")

                    if "snooze" in text:
                        if any(keyword in text for keyword in group_name_valid_keywords):
                            print(f"Phát hiện nút snooze chứa tên nhóm: {text}")
                            continue

                        print("Đã phát hiện nút snooze người đăng bài không hợp lệ")
                        print(f"Tiêu đề nút: {text}")
                        valid_buttons.append(container)

            else:
                print("Không tìm thấy spans trong hàm find_and_click_snooze_button")

        if len(valid_buttons) == 1:
            print("Đang thực hiện việc ấn nút snooze")
            container = valid_buttons[0]

            start_point = pyautogui.position()

            viewport_top = driver.execute_script("return window.scrollY;")
            location = container.location
            base_x = location['x']
            base_y = (location['y'] - viewport_top) * dpr + tab_bar_height

            offset_x = random.uniform(5 * dpr, 100 * dpr)
            offset_y = random.uniform(5 * dpr, 20 * dpr)
            end_point = (base_x + offset_x, base_y + offset_y)

            mover.test_move(start_point, end_point)
            pyautogui.click(end_point)
            print("Đã ấn nút Snooze")

            return True

        return None

    except Exception as e:
        print(f"Lỗi khi xử lý nút snooze: {e}")
        return None


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


def check_driver_and_reconnect(driver):
    try:
        # Test driver bằng script đơn giản
        driver.execute_script("return navigator.userAgent")
        print("✅ Driver vẫn đang kết nối bình thường.")
        return driver
    except (WebDriverException, urllib3.exceptions.HTTPError, http.client.CannotSendRequest,
            http.client.ResponseNotReady, ConnectionError, Exception) as e:

        print(f"[CẢNH BÁO] Mất kết nối với ChromeDriver: {e}")
        print("→ Đang thử kết nối lại qua cổng debugger 9222...")

        # Đóng driver cũ nếu còn
        try:
            driver.quit()
        except:
            pass

        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(15)
            print("[THÀNH CÔNG] Đã kết nối lại với Chrome qua cổng 9222.")

            # Cập nhật driver mới vào aligner (không cần tạo lại đối tượng)
            aligner.update_driver(driver)

            return driver
        except Exception as e:
            print(f"[LỖI] Không thể kết nối lại với Chrome: {e}")
            now = datetime.now()
            subject = f"Chương trình đã được dừng do mất kết nối driver"
            body = f"Thời gian: {now.strftime('%H:%M:%S')}"

            SendingGmail.send_email(subject, body, receiver_email)
            sys.exit(0)


def scanning_post():
    global found_post, menu, pos, reset_facebook_web_time, reset_flag, target, number_of_processed_post, content_not_available_anymore, driver, i
    # print("Kiểm tra driver sau khi search_menu_bar")
    # driver = check_driver_and_reconnect(driver)

    menu = search_menu_bar()

    # print("Kiểm tra driver sau khi search_menu_bar")
    # driver = check_driver_and_reconnect(driver)

    post = None

    same_pos_count = 0
    last_pos = -1

    # Vòng lặp quét bài đăng
    while True:
        i += 1
        content_not_available_anymore = False

        if pos > 50:
            reset_flag = True
            pyautogui.hotkey('ctrl', 'r')
            time.sleep(2)
            pos = 1
            continue

        if comment_count >= target:
            print("Kiểm tra driver trước khi thực hiện việc đổi tài khoản")
            driver = check_driver_and_reconnect(driver)
            print("ID driver trước khi change_account:", id(driver))

            change_account()

            print("Kiểm tra driver sau khi thực hiện việc đổi tài khoản")
            driver = check_driver_and_reconnect(driver)
            print("ID driver sau khi change_account:", id(driver))

            print("Đã đổi tài khoản thành công")

        if reset_flag:
            print("Kiểm tra driver trước khi thực hiện việc lấy lại menu từ reset_flag")
            driver = check_driver_and_reconnect(driver)

            menu = search_menu_bar()
            print("Đã thực hiện lấy lại menu trong reset_flag")

            print("Kiểm tra driver sau khi thực hiện việc lấy lại menu từ reset_flag")
            driver = check_driver_and_reconnect(driver)
            print("Đã hoàn thành kiểm tra trong reset_flag")

            pos = 1
            reset_flag = False
            continue

        print(f"-----Xử lý bài đăng {number_of_processed_post + 1}-----Số lần reset Facebook hiện tại: {reset_facebook_web_time} lần")
        print(f"Chỉ số bài đăng: {pos}")
        print(f"Đã comment được {comment_count} comment")

        # ✅ Kiểm tra lặp lại cùng một vị trí
        if pos == last_pos:
            same_pos_count += 1
        else:
            same_pos_count = 0
            last_pos = pos

        if reset_facebook_web_time > 3:
            print("Việc reset lại Facebook được thực hiện quá nhiều lần, kết thúc chương trình")
            now = datetime.now()
            subject = f"Chương trình đã được dừng do reset_facebook_web_time được gọi quá nhiều lần"
            body = f"Thời gian: {now.strftime('%H:%M:%S')}"

            SendingGmail.send_email(subject, body, receiver_email)
            sys.exit(0)

        # ✅ Nếu bị lặp lại quá nhiều lần thì xử lý đặc biệt
        if same_pos_count > 4:
            print(f"⚠️ Đã xử lý bài đăng {pos} quá 4 lần mà không thành công, thực hiện việc reset lại Facebook")
            pyautogui.hotkey('ctrl', 'r')  # Ví dụ: reload lại trang
            pos = 1
            same_pos_count = 0
            reset_facebook_web_time += 1
            reset_flag = True
            print("Đã bật reset_flag trong same_pos_count > 10")
            time.sleep(8)
            continue  # bỏ qua vòng lặp hiện tại

        try:
            print(f"Bắt đầu quét bài đăng {pos}")

            try:
                # 🔹 Đợi bài đăng xuất hiện
                post = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, POST_SELECTOR_TEMPLATE.format(pos=pos)))
                )
            except Exception as e:
                print(f"[LỖI] Không thể tìm thấy bài đăng tại vị trí {pos}")
                print("Thực hiện việc mở tab Facebook mới")
                reset_flag = True
                reset_facebook_web_time += 1
                open_new_facebook_tab(driver)
                continue

            found_post = True  # Đã tìm thấy bài đăng, không cần bắt lỗi nữa
            pos += 1
            number_of_processed_post += 1
            print("Đã tìm thấy bài đăng")

            # Cuộn xuống một chút để chuẩn bị
            scroll.slow_scroll_down_simulation()
            print("Đã thực hiện xong slow_scroll_down_simulation()")

            if pos > 2:
                # Căn chỉnh góc trên của bài đăng với menu
                aligner.rough_align_post_top_with_menu(post, menu, dpr, driver, tab_bar_height)

            print(f"\nBài đăng {pos - 1} đã được căn chỉnh nửa vời.")

            handle_post(post, menu, pos)
            print("Đã thực hiện xong hàm handle_post")

            if reset_flag:
                print(f"reset_flag đã được thực hiện, bài đăng đang quét đã được đổi về 1")
                pos = 1
                continue

            # Kiểm tra lại nội dung bài đăng với xác suất
            # aligner.scroll_up_to_see_post_content(post, menu, dpr)

            print("\n\n\n")  # Đánh dấu kết thúc của một bài đăng

        except TimeoutException:
            if not found_post:  # Chỉ báo lỗi nếu không tìm thấy bài đăng trong thời gian quy định
                print(f"❌ Bài đăng {pos} không tồn tại, chưa tải hoặc Facebook lag, reset lại")
                pyautogui.hotkey('ctrl', 'r')
                pos = 1
                reset_facebook_web_time += 1
                time.sleep(8)  # Chờ Facebook load lại

        except StaleElementReferenceException:
            reset_flag = True
            continue


def change_account():
    global profile_count, driver, comment_count, first_message_sent, question_send_to_chatgpt_count, number_of_profile, pos, menu, reset_flag, target, theme, reopen_chatgpt_time, answer_from_chatgpt_try_time, tab_bar_height, number_of_processed_post, number_of_post_commented, reset_facebook_web_time
    print("Đang thực hiện việc đổi tài khoản")
    # Bắt đầu chạy khi comment_count đạt số lượng nhất định, đổi profile và đợi một khoảng thời gian
    TabHandle.close_old_tabs(driver)  # Đóng các tab cũ và để tab trắng

    now = datetime.now()

    valid_post_rate = number_of_post_commented / number_of_processed_post
    subject = f"{profile_location[f"profile{profile_count}"][2]} - {comment_count} - {now.strftime('%H:%M:%S')}"
    body = f"Tài khoản: {profile_location[f"profile{profile_count}"][2]}\nSố comment đã comment: {comment_count}\nThời gian thực hiện: {now.strftime('%H:%M:%S')}\nĐã quét qua số bài đăng: {number_of_processed_post}\nTỉ lệ bài đăng hợp lệ: {valid_post_rate:.2f}"

    comment_count = 0  # Đặt lại số bình luận
    question_send_to_chatgpt_count = 0  # Đặt lại số câu hỏi đã gửi đến ChatGPT
    reopen_chatgpt_time = 0
    reset_facebook_web_time = 0
    answer_from_chatgpt_try_time = 0
    number_of_processed_post = 0
    number_of_post_commented = 0
    pos = 1
    first_message_sent = False
    menu = None
    reset_flag = True
    print("Đã bật reset_flag trong change_account()")

    SendingGmail.send_email(subject, body, receiver_email)

    # Tăng profile_count, nếu profile_count đến số cuối thì quay lại 1
    profile_count += 1

    if profile_count == 4:
        profile_count += 1

    if profile_count > number_of_profile:
        long_time_sleep = random.randint(10800, 12600)
        print(f"Thời gian hiện tại là: {now.strftime('%H:%M:%S')}")
        print(
            f"Thực hiện quãng nghỉ dài sau khi đã quét xong với {number_of_profile} acc - {long_time_sleep / 60} phút")
        time_counter(long_time_sleep)
        profile_count = 1
    else:
        short_time_sleep = random.randint(1200, 1500)
        print(f"Thời gian hiện tại là: {now.strftime('%H:%M:%S')}")
        time_counter(short_time_sleep)

    TimeManage.wait_for_valid_time()  # Kiểm tra thời gian trước khi quét bài đăng
    target = profile_location[f"profile{profile_count}"][4]

    # Tạo driver với profile tiếp theo
    driver, tab_bar_height, _, theme, _ = Start2.start_browsers(profile_count, screen_scale_x, screen_scale_y)

    # Cập nhật driver mới vào aligner (không cần tạo lại đối tượng)
    aligner.update_driver(driver)
    print("ID driver sau khi update trong Align:", id(driver))

    if not check_tabs_open(driver):
        print("Việc mở tab ChatGPT hoặc Facebook không thành công, đang khởi động lại")
        TabHandle.close_old_tabs(driver)
        time.sleep(2)
        TimeManage.wait_for_valid_time()  # Kiểm tra thời gian trước khi quét bài đăng
        driver, tab_bar_height, _, theme, _ = Start2.start_browsers(profile_count, screen_scale_x, screen_scale_y)
        time.sleep(2)

        aligner.update_driver(driver)
        time.sleep(1)

    elif check_tabs_open(driver):
        print("Đã mở cả 2 tab ChatGPT và Facebook thành công")

    print("Kiểm tra driver trước khi kết thúc change_account")
    driver = check_driver_and_reconnect(driver)
    print("ID driver trước khi kết thúc change_account:", id(driver))
    return reset_flag


def open_new_chatgpt_tab(driver):
    global answer_from_chatgpt_try_time, question_send_to_chatgpt_count
    answer_from_chatgpt_try_time = 0
    question_send_to_chatgpt_count = 0

    try:
        tabs = driver.window_handles
        print("Đã lấy được danh sách tabs")
    except WebDriverException as e:
        print("[LỖI] Không thể lấy danh sách tab từ trình duyệt.")
        print(f"Chi tiết lỗi Selenium: {e}")
        traceback.print_exc()
        # Có thể xử lý lại driver tại đây nếu cần
        sys.exit(0)
    except Exception as e:
        print("[LỖI KHÁC] Không xác định được lỗi khi truy cập window_handles.")
        print(f"Chi tiết: {e}")
        traceback.print_exc()
        sys.exit(0)

    # Tìm và đóng tab ChatGPT
    for tab in tabs:
        driver.switch_to.window(tab)
        if "chatgpt.com" in driver.current_url:
            driver.close()
            print("Đã đóng tab ChatGPT bị lag.")
            break

    time.sleep(1)  # Chờ một chút để đảm bảo tab đã đóng

    TabHandle.switch_tab_to(driver, "facebook")

    # Mở lại tab ChatGPT mới
    driver.execute_script("window.open('https://chat.openai.com', '_blank');")
    print("Đã mở tab ChatGPT mới.")
    time.sleep(3)

    # Chuyển sang tab ChatGPT mới mở
    TabHandle.switch_tab_to(driver, "chatgpt")

def open_new_facebook_tab(driver):
    print("Đang thực hiện hàm open_new_facebook_tab")

    try:
        tabs = driver.window_handles
        print("Đã lấy được danh sách tabs")
    except WebDriverException as e:
        print("[LỖI] Không thể lấy danh sách tab từ trình duyệt.")
        print(f"Chi tiết lỗi Selenium: {e}")
        traceback.print_exc()
        # Có thể xử lý lại driver tại đây nếu cần
        sys.exit(0)
    except Exception as e:
        print("[LỖI KHÁC] Không xác định được lỗi khi truy cập window_handles.")
        print(f"Chi tiết: {e}")
        traceback.print_exc()
        sys.exit(0)

    # Tìm và đóng tab Facebook
    for tab in tabs:
        driver.switch_to.window(tab)
        if "facebook.com" in driver.current_url:
            driver.close()
            print("Đã đóng tab Facebook bị misclick")
            break

    time.sleep(1)  # Chờ một chút để đảm bảo tab đã đóng

    TabHandle.switch_tab_to(driver, "chatgpt")

    # Mở lại tab Facebook mới
    driver.execute_script("window.open('https://www.facebook.com/', '_blank');")
    print("Đã mở tab Facebook mới.")
    time.sleep(3)

    # Chuyển sang tab Facebook mới mở
    TabHandle.switch_tab_to(driver, "facebook")


def is_driver_alive(driver):
    try:
        # Kiểm tra trạng thái session
        _ = driver.title  # Hoặc driver.current_url
        return True
    except:
        return False

attempt = 0
while attempt < 3:
    if not check_tabs_open(driver):
        print(f"Lần thử {attempt + 1}: Việc mở tab ChatGPT hoặc Facebook không thành công, đang khởi động lại")
        TabHandle.close_old_tabs(driver)
        time.sleep(2)
        TimeManage.wait_for_valid_time()  # Kiểm tra thời gian trước khi quét bài đăng

        driver, tab_bar_height, _, theme, _ = Start2.start_browsers(profile_count, screen_scale_x, screen_scale_y)
        time.sleep(2)

        aligner.update_driver(driver)
        time.sleep(1)

        attempt += 1
    else:
        print("Đã mở cả 2 tab ChatGPT và Facebook thành công")
        print("Kiểm tra driver trước khi bắt đầu vào hàm scanning_post")
        driver = check_driver_and_reconnect(driver)
        break
else:
    print("Thử 3 lần nhưng vẫn không mở được 2 tab cần thiết. Thoát chương trình.")
    now = datetime.now()
    subject = f"Chương trình đã được dừng do không mở được đúng 2 tab cần thiết"
    body = f"Thời gian: {now.strftime('%H:%M:%S')}"

    SendingGmail.send_email(subject, body, receiver_email)
    sys.exit(0)

scanning_post()
