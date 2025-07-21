import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pynput.keyboard import Key, Controller
from pynput.mouse import Controller as MouseController
import pyautogui
from Mousemove import MouseMover
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import ReadTimeoutError
import pyperclip
import TabHandle
import pygetwindow as gw
from selenium.common.exceptions import WebDriverException

# Cài pywin32 nếu không cài đươc 3 thư viện này
import win32api
import win32gui
import win32con

mover = MouseMover()
keyboard = Controller()
mouse = MouseController()


def get_taskbar_height():
    monitor = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTONEAREST)
    monitor_info = win32api.GetMonitorInfo(monitor)
    work_area = monitor_info['Work']

    screen_height = win32api.GetSystemMetrics(1)
    work_height = work_area[3] - work_area[1]

    return screen_height - work_height


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

    except Exception as e:
        print(f"Lỗi khi đưa Chrome ra trước màn hình: {str(e)}")


def check_driver_and_reconnect(driver):
    try:
        # Thử chạy 1 lệnh đơn giản để kiểm tra driver còn hoạt động
        _ = driver.title  # Gọi lệnh bất kì để xem driver còn sống không
        print("✅ Driver vẫn đang kết nối bình thường.")
        return driver  # Trả về driver hiện tại nếu vẫn hoạt động

    except WebDriverException as e:
        print("❌ Driver đã bị ngắt kết nối:", str(e))
        print("🔄 Đang tiến hành kết nối lại...")

        try:
            # Kết nối lại với Chrome qua debugger address
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(15)
            print("✅ Đã kết nối lại thành công.")
            return driver

        except Exception as reconnect_error:
            print("❌ Kết nối lại thất bại:", str(reconnect_error))
            return None


def start_browsers(profile_count, screen_scale_x, screen_scale_y):
    while True:
        try:
            # Tính profile name theo profile_count
            if profile_count == 1:
                profile_name = "Default"
            else:
                profile_name = f"Profile {profile_count}"

            # Lấy kích thước màn hình
            width, height = pyautogui.size()

            pyautogui.press('win')  # Mở Start Menu
            time.sleep(1)

            # Chuẩn bị lệnh khởi động Chrome với profile tương ứng
            command = f'chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\ChromeDebugProfiles" --profile-directory="{profile_name}"'
            pyperclip.copy(command)
            time.sleep(0.5)

            # Dán lệnh vào ô tìm kiếm rồi nhấn Enter
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            print(f"Đã mở Chrome với profile: {profile_name}")
            time.sleep(3)

            start_x, start_y = pyautogui.position()
            mover.test_move((start_x, start_y), (1100 * screen_scale_x, 273 * screen_scale_y))
            pyautogui.click()
            time.sleep(1)

            start_x, start_y = pyautogui.position()
            mover.test_move((start_x, start_y), (1030 * screen_scale_x, 273 * screen_scale_y))
            pyautogui.click()

            try:
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
                driver = webdriver.Chrome(options=chrome_options)
                driver.set_page_load_timeout(15)
                print("Đã kết nối với selenium, khởi tạo driver thành công.")

                print("Chuẩn bị kiểm tra window_size")
                # Kiểm tra và maximize nếu chưa phải fullscreen
                try:
                    handles = driver.window_handles
                    print(f"🧩 Số tab hiện có: {len(handles)}")

                    for idx, handle in enumerate(handles):
                        try:
                            driver.switch_to.window(handle)
                            current_url = driver.current_url
                            title = driver.title
                            print(f"\n📄 Tab {idx + 1}:")
                            print(f"🆔 Handle ID: {handle}")
                            print(f"🔗 URL: {current_url}")
                            print(f"📝 Title: {title}")
                        except Exception as tab_err:
                            print(f"\n❌ Lỗi khi truy cập tab {idx + 1} (handle: {handle}): {tab_err}")

                    # Sau khi duyệt xong, thử lấy window_size ở tab đầu tiên (nếu cần)
                    TabHandle.switch_tab_to(driver, "new-tab")
                    window_size = driver.get_window_size()
                    print(f"\n📐 Kích thước cửa sổ trình duyệt: {window_size}")

                except Exception as e:
                    print("❌ Lỗi khi lấy kích thước browser hoặc thao tác với các tab:", e)

                try:
                    screen_size = pyautogui.size()
                    print(f"Kích thước màn hình: {screen_size}")
                except Exception as e:
                    print("Lỗi khi lấy kích thước màn hình bằng pyautogui.size():", e)
                print("Đã lấy được trạng thái window_size")

                if window_size["width"] < screen_size.width or window_size["height"] < screen_size.height:
                    print("Cửa sổ chưa maximize. Đang thực hiện maximize...")
                    driver.maximize_window()
                    time.sleep(1)
                else:
                    print("Cửa sổ đã ở chế độ maximize.")

                driver.get("https://www.facebook.com/")
                print("Đã mở Facebook")
                driver.implicitly_wait(2)

                time.sleep(2)
                driver.execute_script("window.open('https://chat.openai.com', '_blank');")
                print("Đã mở ChatGPT")

                time.sleep(3)
                # Chuyển về Facebook
                TabHandle.switch_tab_to(driver, "facebook")

                # 👉 Lấy devicePixelRatio (DPR)

                dpr = driver.execute_script("return window.devicePixelRatio")

                print(f"Device Pixel Ratio (DPR): {dpr}")

                # Lấy chiều cao viewport
                viewport_height_raw = driver.execute_script("return window.innerHeight")
                viewport_height = viewport_height_raw * dpr
                print(f"Chiều cao viewport: {viewport_height} px")

                # Lấy chiều cao taskbar
                taskbar_height = get_taskbar_height()
                print(f"Chiều cao taskbar: {taskbar_height} px")

                tab_bar_height = height - viewport_height - taskbar_height
                print(f"Chiều cao thanh tab và thanh địa chỉ là {tab_bar_height} px")

                time.sleep(2)

                # Xác định theme browser là light hay dark
                is_dark_mode = driver.execute_script(
                    "return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;"
                )

                if is_dark_mode:
                    print("theme của trình duyệt hiện tại là dark")
                else:
                    print("theme của trình duyệt hiện tại là light")

                time.sleep(2)
                bring_debugging_chrome_to_front()
                time.sleep(2)

                print("Kiểm tra driver trước khi kết thúc start_browsers")
                driver = check_driver_and_reconnect(driver)

                return driver, tab_bar_height, dpr, is_dark_mode, taskbar_height

            except (TimeoutException, ReadTimeoutError) as e:
                print(f"Lỗi khi kết nối với Chrome: {str(e)}. Thử lại sau 3 giây...")
                time.sleep(3)
                TabHandle.click_close_window()
                time.sleep(3)
                continue

        except Exception as e:
            print(f"Lỗi không xác định trong vòng lặp: {str(e)}. Thử lại sau 3 giây...")
            time.sleep(3)
            continue
