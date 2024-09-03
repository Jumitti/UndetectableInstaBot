import cv2
import pyautogui
import numpy as np
import time
import random
import easyocr
import keyboard
import os
from datetime import datetime

scale_like = 0
logo_like = None
best_match_like = 0
scale_comment = 0
logo_comment = None
best_match_comment = 0
y_last_like = 0
y_last_comment = 0


def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    return screenshot


def save_detected_image(type, display_result, max_loc, resized_logo, scale, max_val, threshold):
    debug_folder = 'debug'
    if not os.path.exists(debug_folder):
        os.makedirs(debug_folder)

    bottom_right = (max_loc[0] + resized_logo.shape[1], max_loc[1] + resized_logo.shape[0])
    cv2.rectangle(display_result, max_loc, bottom_right, (0, 255, 0), 2)

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{type}-Threshold {threshold}-Scale {scale}-MaxVal {max_val}-Time {current_time}.png'

    file_path = os.path.join(debug_folder, filename)
    cv2.imwrite(file_path, display_result)
    print(f"Debug: {file_path}")


def detect_scale(type, logos, scales, threshold, debug, update_progress_callback=None):
    """
    :param logos:
    :param scales:
    :param threshold:
    :return:
    """

    screenshot = take_screenshot()
    best_match = None
    best_logo = None
    best_scale = None
    best_result = None
    i = 1
    j = 1

    for logo in logos:
        for scale in scales:
            resized_logo = cv2.resize(logo, (0, 0), fx=scale, fy=scale)

            if resized_logo.shape[0] > screenshot.shape[0] or resized_logo.shape[1] > screenshot.shape[1]:
                continue

            result = cv2.matchTemplate(screenshot, resized_logo, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            print(f"Detection {type}-Logo {i}-Scale {scale}-MaxVal {max_val}")

            if max_val >= threshold:
                if best_match is None or max_val > best_match:
                    best_match = max_val
                    best_logo = logo
                    best_scale = scale
                    best_result = (max_loc, resized_logo.shape[1], resized_logo.shape[0])

            if debug == 2:
                display_result = screenshot.copy()
                top_left = max_loc
                bottom_right = (top_left[0] + resized_logo.shape[1], top_left[1] + resized_logo.shape[0])
                save_detected_image(f"Detection {type} {i}", display_result, max_loc, resized_logo, scale, max_val, threshold)

            if update_progress_callback:
                update_progress_callback(j / (len(logos) * len(scales)), f"Scale detection for {type}...")
            j += 1
        i += 1

    if best_match:
        return best_logo, best_scale, best_match
    else:
        return None


def main_like(threshold=0.75, debug=0, update_progress_callback=None):
    global scale_like, logo_like, y_last_like, best_match_like

    logos = [cv2.imread('undetectableinstabot/logo/logo_light.png'), cv2.imread('undetectableinstabot/logo/logo_dark.png')]
    scales = np.linspace(0.5, 1.5, 20)

    if scale_like == 0 and logo_like is None and best_match_like == 0:
        scale_like_output = detect_scale("Like", logos, scales, threshold, debug, update_progress_callback if update_progress_callback is not None else None)
        if scale_like_output:
            logo_like, scale_like, best_match_like = scale_like_output
        else:
            print("Like logo not found, try again in the next loop. Remember to change the threshold and debug if necessary")

    if scale_like != 0 and logo_like is not None:
        screenshot = take_screenshot()
        best_result = None

        resized_logo = cv2.resize(logo_like, (0, 0), fx=scale_like, fy=scale_like)
        result = cv2.matchTemplate(screenshot, resized_logo, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"Like-Scale {scale_like}-MaxVal {max_val}")
        if max_val >= threshold:
            best_result = (max_loc, resized_logo.shape[1], resized_logo.shape[0])

            if 0 < debug <= 2:
                display_result = screenshot.copy()
                top_left = max_loc
                bottom_right = (top_left[0] + resized_logo.shape[1], top_left[1] + resized_logo.shape[0])
                save_detected_image("Like", display_result, max_loc, resized_logo, scale_like, max_val, threshold)

        if best_result:
            max_loc, width, height = best_result
            logo_center_x = max_loc[0] + width // 2
            logo_center_y = max_loc[1] + height // 2
            offset_x = int(width * 0.3)
            offset_y = 0
            click_x = logo_center_x - offset_x
            click_y = logo_center_y + offset_y
            click_x = max(0, min(click_x, screenshot.shape[1] - 1))
            click_y = max(0, min(click_y, screenshot.shape[0] - 1))

            if click_y > y_last_like:
                pyautogui.moveTo(click_x, click_y)
                time.sleep(0.25)
                pyautogui.click()
                pyautogui.moveTo(click_x - 100, click_y)
                print(f"Like detected at (X:{click_x}, Y:{click_y}).")
                y_last_like = click_y
        else:
            y_last_like = 0
            print("Logo not found. Scroll down.")

    time.sleep(0.25)
    pyautogui.scroll(-150)
    time.sleep(0.25)

    return scale_like if scale_like != 0 else None, best_match_like if best_match_like != 0 else None


def main_comment(comment, threshold=0.49, debug=0, update_progress_callback=None):
    global scale_comment, logo_comment, y_last_comment, best_match_comment

    logos = [cv2.imread('undetectableinstabot/logo/comment_light.png'), cv2.imread('undetectableinstabot/logo/comment_dark.png')]
    scales = np.linspace(0.25, 1.75, 30)

    if scale_comment == 0 and logo_comment is None:
        scale_comment_output = detect_scale("Comment", logos, scales, threshold, debug, update_progress_callback if update_progress_callback is not None else None)
        if scale_comment_output:
            logo_comment, scale_comment, best_match_comment = scale_comment_output
        else:
            print("Comment logo not found, try again in the next loop. Remember to change the threshold and debug if necessary")

    if scale_comment != 0 and logo_comment is not None:
        screenshot = take_screenshot()
        best_result = None

        resized_logo = cv2.resize(logo_comment, (0, 0), fx=scale_comment, fy=scale_comment)
        result = cv2.matchTemplate(screenshot, resized_logo, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"Comment-Scale {scale_comment}-Max Val {max_val}")
        if max_val >= threshold:
            best_result = (max_loc, resized_logo.shape[1], resized_logo.shape[0])

            if 0 < debug <= 2:
                display_result = screenshot.copy()
                top_left = max_loc
                bottom_right = (top_left[0] + resized_logo.shape[1], top_left[1] + resized_logo.shape[0])
                save_detected_image("Comment", display_result, max_loc, resized_logo, scale_like, max_val, threshold)

        if best_result:
            max_loc, width, height = best_result
            logo_center_x = max_loc[0] + width // 2
            logo_center_y = max_loc[1] + height // 2
            offset_x = int(width * 0.3)
            offset_y = int(height * 0.3)
            click_x = logo_center_x - offset_x
            click_y = logo_center_y - offset_y
            click_x = max(0, min(click_x, screenshot.shape[1] - 1))
            click_y = max(0, min(click_y, screenshot.shape[0] - 1))

            if click_y > y_last_comment:
                pyautogui.moveTo(click_x, click_y)
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(0.5)
                keyboard.write(comment)
                time.sleep(0.5)
                keyboard.press_and_release('enter')
                time.sleep(0.5)
                pyautogui.moveTo(click_x - 150, click_y)
                print(f"Comment detected at (X:{click_x}, Y:{click_y}).")
                y_last_comment = click_y
        else:
            y_last_comment = 0
            print("Comment not found. Scroll down.")

    time.sleep(1)
    pyautogui.scroll(-150)
    time.sleep(1)

    return scale_comment if scale_comment != 0 else None, best_match_comment if best_match_comment != 0 else None


def reset(pause=False):
    global scale_like, logo_like, logo_comment, scale_comment, y_last_like, y_last_comment

    if pause is False:
        scale_like = 0
        logo_like = None
        scale_comment = 0
        logo_comment = None
    y_last_like = 0
    y_last_comment = 0
