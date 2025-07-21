# Các hàm liên quan đến xử lý tab (đóng mở tab, chuyển đổi tab)

import time
from Mousemove import MouseMover
import pyautogui
import sys

# Khởi tạo đối tượng từ class MouseMover
mover = MouseMover()


def get_current_tab(driver):
    """Kiểm tra URL hiện tại để xác định tab đang mở."""
    current_url = driver.current_url.lower()
    if "facebook" in current_url:
        return 1
    elif "chat.openai" in current_url or "chatgpt" in current_url:
        return 2
    return 0


def switch_tab_reverse(driver):
    """Chuyển tab giữa Facebook và ChatGPT bằng Selenium"""
    initial_tab = get_current_tab(driver)
    print(f"Giá trị của initial_tab là {initial_tab}, URL: {driver.current_url}")
    print(f"Tab hiện tại là {'Facebook' if initial_tab == 1 else 'ChatGPT'}")

    if initial_tab == 0:
        print("Không xác định được tab hiện tại!")
        return

    # Lấy danh sách các tab
    handles = driver.window_handles
    current_index = handles.index(driver.current_window_handle)

    # Chuyển sang tab tiếp theo trong danh sách
    next_index = 0 if initial_tab == 1 else 1
    driver.switch_to.window(handles[next_index])

    time.sleep(1)  # Chờ trình duyệt cập nhật URL

    new_tab = get_current_tab(driver)
    print(f"Giá trị của new_tab là {new_tab}, URL: {driver.current_url}")
    print(f"Tab sau khi đã chuyển là {'Facebook' if new_tab == 1 else 'ChatGPT'}")

    if new_tab != initial_tab:
        print("Chuyển tab thành công!")
    else:
        print("Chuyển tab thất bại!")


def switch_tab(driver):
    """Chuyển tab giữa Facebook và ChatGPT bằng Selenium"""
    initial_tab = get_current_tab(driver)
    print(f"Giá trị của initial_tab là {initial_tab}, URL: {driver.current_url}")
    print(f"Tab hiện tại là {'Facebook' if initial_tab == 1 else 'ChatGPT'}")

    if initial_tab == 0:
        print("Không xác định được tab hiện tại!")
        return

    # Lấy danh sách các tab
    handles = driver.window_handles
    current_index = handles.index(driver.current_window_handle)

    # Chuyển sang tab tiếp theo trong danh sách
    next_index = 1 if initial_tab == 1 else 0
    driver.switch_to.window(handles[next_index])

    time.sleep(1)  # Chờ trình duyệt cập nhật URL

    new_tab = get_current_tab(driver)
    print(f"Giá trị của new_tab là {new_tab}, URL: {driver.current_url}")
    print(f"Tab sau khi đã chuyển là {'Facebook' if new_tab == 1 else 'ChatGPT'}")

    if new_tab != initial_tab:
        print("Chuyển tab thành công!")
    else:
        print("Chuyển tab thất bại!, thử lại bằng hàm switch_tab_reverse")
        switch_tab_reverse(driver)


def switch_tab_to(driver, goal):
    goal = goal.strip().lower()
    handles = driver.window_handles
    print(f"Đang tìm tab có chứa '{goal}' trong URL...")

    for index, handle in enumerate(handles):
        driver.switch_to.window(handle)
        time.sleep(1)  # Cho trình duyệt thời gian cập nhật URL

        current_url = driver.current_url.lower()
        print(f"Tab {index + 1} URL: {current_url}")

        if goal in current_url:
            print(f"✅ Đã chuyển đến tab chứa '{goal}' thành công!")
            return

    print(f"❌ Không tìm thấy tab nào có chứa '{goal}' trong URL.")



def click_close_window():
    start_x, start_y = pyautogui.position()
    width, height = pyautogui.size()
    mover.test_move((start_x, start_y), (width - 10, 10))
    pyautogui.click()
    print("Đã đóng cửa sổ bằng close")


def close_old_tabs(driver):
    """Mở một tab mới (trống) và đóng các tab cũ, bỏ qua tab có tiêu đề 'Tab search'. Thử lại tối đa 3 lần nếu lỗi."""

    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            old_tabs = driver.window_handles
            print("Đang thực hiện đóng các tab cũ và để tab trắng trước khi đổi acc")

            # Mở tab mới (trống)
            pyautogui.hotkey('ctrl', 't')
            print("Đã mở tab trắng")
            time.sleep(1)

            # Đóng các tab cũ, trừ tab có tiêu đề 'Tab search'
            for tab in old_tabs:
                driver.switch_to.window(tab)
                title = driver.title.strip().lower()

                if title != "tab search":
                    print(f"Đóng tab tiêu đề: {driver.title}")
                    driver.close()
                else:
                    print(f"Bỏ qua tab có tiêu đề 'Tab search'")

            print("Đã đóng các tab cũ")

            # Chuyển sang tab mới nhất (còn lại sau khi đóng)
            remaining_tabs = driver.window_handles
            if remaining_tabs:
                driver.switch_to.window(remaining_tabs[0])
                print("Đã chuyển về tab trắng")

            driver.quit()
            click_close_window()  # Giả định bạn đã định nghĩa hàm này ở nơi khác
            driver.quit()

            break  # Thành công thì thoát khỏi vòng lặp

        except Exception as e:
            retry_count += 1
            print(f"Lỗi lần {retry_count}: {e}")
            if retry_count < max_retries:
                print("Thử lại...")
                time.sleep(2)
            else:
                print("Thử lại thất bại 3 lần. Thoát chương trình.")
                sys.exit(0)
