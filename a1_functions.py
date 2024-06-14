import pyautogui
from PIL import ImageGrab
import numpy as np
from numpy import random
import cv2
import time
import pygetwindow as gw
import pywinauto
import os
import vlc
import ctypes
import scipy
from scipy import interpolate
from pynput import keyboard
import pytesseract
import re
import mss
import threading

start_time = time.time()


def alarm_sound(sound='alarm'):
    p = vlc.MediaPlayer(f'sounds/{sound}.mp3')
    p.play()
    time.sleep(2)
# threading.Thread(target=alarm_sound, args=(['sonar'])).start()


def randomize_click(x, y, width, height):
        # x/y are center of region, width/height is total size
    region_x = np.arange(round(x - width / 2), round(x + width / 2), 1)
    region_y = np.arange(round(y - height / 2), round(y + height / 2), 1)
    # print(min(region_x), max(region_x), max(region_x) - min(region_x))
    x = random.choice(region_x)
    y = random.choice(region_y)
    return x, y
# randomize_click(100,100,52,52)


def randomize_click2(x0, y0, x1, y1):
    region_x = np.arange(x0, x1, 1)
    region_y = np.arange(y0, y1, 1)
    x = random.choice(region_x)
    y = random.choice(region_y)
    return x, y
# x,y = randomize_click2(4, 61, 50, 102)
# pyautogui.moveTo(x, y)


def move_to(x2, y2):

    # time.sleep(np.random.gamma(3, .2, 1))
    x1, y1 = pyautogui.position()  # Starting position

    dist = int(((x2-x1)**2 + (y2-y1)**2)**.5)
    cp = 3 + int(dist/800)  # Number of control points. Must be at least 2.
    # print(cp)
    # cp = 3

    # Distribute control points between start and destination evenly.
    x = np.linspace(x1, x2, num=cp, dtype='int')
    y = np.linspace(y1, y2, num=cp, dtype='int')

    # Randomise inner points a bit (+-RND at most).
    RND = 40
    xr = np.random.randint(-RND, RND, size=cp)
    yr = np.random.randint(-RND, RND, size=cp)
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr

    # Approximate using Bezier spline.
    degree = 3 if cp > 3 else cp - 1  # Degree of b-spline. 3 is recommended.
                                      # Must be less than number of control points.

    tck, u = scipy.interpolate.splprep([x, y], k=degree)
    u = np.linspace(0, 1, num=100)  # num = max screen dimension

    points = scipy.interpolate.splev(u, tck)
    array = list(zip(*(i.astype(int) for i in points)))

    new_array = []
    for index, point in enumerate(array):
        if array[index] != array[index-1]:
            new_array.append(array[index])

    for point in new_array[::2]:
        ctypes.windll.user32.SetCursorPos(int(point[0]), int(point[1]))
        time.sleep(0.001)
    # time.sleep(np.random.gamma(3, .2, 1))
# time.sleep(1)
# move_to(3500, 200)


def video_capture(pathandname, screen, scale=0.5, duration=10):
    if screen == 'laptop':
        top, left, width, height = 0, 0, 2559, 1599
    if screen == 'monitor':
        top, left, width, height = 0, 0, 2559, 1599

    frame_width = round(width * scale)
    frame_height = round(height * scale)
    fps = 20.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vidwriter = cv2.VideoWriter(f'{pathandname}.avi', fourcc, fps, (frame_width, frame_height))

    start_time = time.time()
    with mss.mss() as sct:
        # Part of the screen to capture
        monitor = {"top": top, "left": left, "width": width, "height": height}

        while time.time() - start_time < duration:
            last_time = time.time()

            img = np.array(sct.grab(monitor))
            img = cv2.resize(img, (frame_width, frame_height))
            frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            cv2.putText(frame, "FPS: %f" % (1.0 / (time.time() - last_time)),
                        (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            vidwriter.write(frame)
    vidwriter.release()
    cv2.destroyAllWindows()
# video_capture('Alerts/Newsig', 'laptop', duration=2)


def ocr(bbox, scale=6, lng='eng', file=None, quantity=False, simple=False, mode=None):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if file is None:
        ImageGrab.grab(bbox=bbox, all_screens=True).save('Tesseract/ocr_window.png')

    im_gray = cv2.imread('Tesseract/ocr_window.png', cv2.IMREAD_GRAYSCALE)
    if scale != 1:
        im_gray = cv2.resize(im_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    cv2.imwrite('Tesseract/ocr_im_gray.jpg', im_gray)
    binary = cv2.threshold(im_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    invert = cv2.bitwise_not(binary)
    cv2.imwrite('Tesseract/ocr_processed.jpg', invert)

    array = pytesseract.image_to_boxes(invert, lang=lng, config='--psm 7 --oem 3')
    # print(array)
    split_array = re.split('\n', array)
    new_array = []
    for i, row in enumerate(split_array):
        if i < len(split_array) - 1:
            new_array.append(re.split(' ', row))
    string = []
    for row in new_array:
        # print(row)
        if len(string) > 0:
            if int(row[1]) - int(oldrightbound) > 4*scale:
                string.append(' ')
        string.append(row[0])
        oldrightbound = row[3]
    string = ''.join(string)

    if mode == 'distance':
        # ------ duplicate for numbers
        num_array = pytesseract.image_to_boxes(invert, lang='Eve', config='--psm 7 --oem 3')
        split_array2 = re.split('\n', num_array)
        new_array2 = []
        for i, row in enumerate(split_array2):
            if i < len(split_array2) - 1:
                new_array2.append(re.split(' ', row))
        string2 = []
        for row in new_array2:
            # print(row)
            if len(string2) > 0:
                if int(row[1]) - int(oldrightbound) > 4 * scale:
                    string2.append(' ')
            string2.append(row[0])
            oldrightbound = row[3]
        string2 = ''.join(string2)
        # print(string2)

    if lng == 'num':
        string = string.replace(' ', '').replace(',', '').replace('.', '', (string.count('.') - 1))

    if mode == 'distance':
        # print(string)
        string = string.replace('@', '0').replace(' Il', ' II').replace('m_', 'm').replace('kn','km')
        if string.find(' AU') != -1:
            # # if string.find('.') == -1:
            # string = string[:string.find(' AU')-2]
            # print(string)
            return 100000000
        elif string.find('km') != -1:
            distance = string2[:string2.find(' ')] + '000'
        elif string.find('m') != -1:
            string2 = string2.replace(',', '')
            distance = string2[:string2.find(' ')]

        distance = (int(distance))
        return distance

    return string
# old = 0
# while 1 != 0:
#     string = ocr(bbox = (2021, 234, 2262, 255), lng='eng', mode='distance')  ## top of overview window
#     # string = ocr(bbox = (2112, 233, 2255, 262), lng='eng')
#     new = string
#     if new != old:
#         print(new)
#     old = new
#     time.sleep(.1)

# response = find_on_overview('asteroid', 'laptop', click=True)
# x, y = response[0], response[1]
# print(x, y)
# bbox=(x+2, y-10, 2262, y+10)

# bbox=(2033, 304, 2263, 325)
# dist = ocr(bbox=bbox, scale=6, lng='eng', mode='distance', file='yes')  ## top of overview window
# print(dist)


def find_ui_element(screen, element, x0=None, y0=None, x1=None, y1=None, button=None, threshold=.8, silent=False):
    if screen == 'monitor':
        template_path = 'Templates/UI Elements/Monitor/' + element + '.png'
        mod = 0.8333
    if screen == 'laptop':
        template_path = 'Templates/UI Elements/Laptop/' + element + '.png'
        mod = 1
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')
    method = cv2.TM_CCOEFF_NORMED

    object = cv2.imread(template_path)
    result = cv2.matchTemplate(object, search_region, method)
    loc = np.where(result >= threshold)

    h, w = object.shape[:2]
    for pt in zip(*loc[::-1]):
        cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    if loc[0].shape[0] == 0:
        if silent is False:
            print(f'\robject: "{element}" not found on screen')
        return 'not found'
    if loc[0].shape[0] != 0:
        h, w = object.shape[:2]
        y = (loc[0][0] + y0 + h / 2.1)/mod
        x = (loc[1][0] + x0 + w / 2.1)/mod
        xrand, yrand = randomize_click(x, y, w, h)

        if button == 'left' or button == 'right':
            pyautogui.moveTo(xrand, yrand)
            time.sleep(.1 + random.gamma(3, .1))
            pyautogui.click(button=button)
            time.sleep(.3 + random.gamma(4, .1))
        if button == 'double':
            pyautogui.moveTo(xrand, yrand)
            interval = np.random.normal(0.12, 0.006, 1)[0]
            pyautogui.click(clicks=2, interval=float(interval))
        return x, y
# print(find_ui_element('laptop', 'stopped', 681, 1372, 1057, 1599, silent=True,threshold=.95))
# print(find_ui_element('laptop', 'drones_on_target', 1641, 150, 1937, 246, silent=True))
# find_ui_element('laptop','close', 1378, 327, 1975, 905)
# def find_UI_element(screen, element, x0=None, y0=None, x1=None, y1=None, threshold=.8):
#     if screen == 'monitor':
#         template_path = 'Templates/UI Elements/Monitor/' + element + '.png'
#         mod = 0.8333
#     if screen == 'laptop':
#         template_path = 'Templates/UI Elements/Laptop/' + element + '.png'
#         mod = 1
#     ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
#     search_region = cv2.imread('Templates/1_Search_Region.png')
#     method = cv2.TM_CCOEFF_NORMED
#
#     object = cv2.imread(template_path)
#     result = cv2.matchTemplate(object, search_region, method)
#     loc = np.where(result >= threshold)
#
#     # h, w = template.shape[:2]
#     # for pt in zip(*loc[::-1]):
#     #     cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
#     # cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)
#
#     if loc[0].shape[0] == 0:
#         return False
#     if loc[0].shape[0] != 0:
#         h, w = object.shape[:2]
#         y, x = loc[0][0] + y0 + h / 2.1, loc[1][0] + x0 + w / 2.1
#
#         return True
# # print(find_UI_element('laptop','cluster shutdown', 809, 0, 1751, 803))


def find_in_context_menu(x,y, what, screen):
    if screen == 'laptop':
        path = 'Templates/Right Click/Laptop/'
        mod = 1
    if screen == 'monitor':
        path = 'Templates/Right Click/Monitor/'
        mod = 0.8333

    x = x*mod
    y = y*mod

    x0 = x
    x1 = x + 400
    y0 = y - 400
    y1 = y + 500

    if 2100 < x0 < 2560:
        x0 = 2100
        x1 = 2560
        if y0 > 1000:
            y0 = 1000
            y1 = 1600

    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8

    template = cv2.imread(path + what + '.png')
    result = cv2.matchTemplate(template, search_region, method)
    loc = np.where(result >= threshold)
    h, w = template.shape[:2]

    if 'warp' in what and loc[0].shape[0] == 0:
        template = cv2.imread(path + 'approach_location.png')
        result = cv2.matchTemplate(template, search_region, method)
        loc = np.where(result >= threshold)
        if loc[0].shape[0] != 0:
            return 'already there'

    for pt in zip(*loc[::-1]):
        cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    if loc[0].shape[0] != 0:
        y = round((y0 + loc[0][0] + h/2)/mod)
        x = round((x0 + loc[1][0] + w/2)/mod)
        return x, y
    else:
        print('"'+what+'"' + ' not found in context menu')
        return 'not found'
# x = find_in_context_menu(3473, 76,'warp_self')
# print(x[0])


def reset_mouse(screen):
    time.sleep(1)
    if screen == 'monitor':
        x, y = 4500, 500
    if screen == 'laptop':
        x, y = 1300, 400
    x, y = randomize_click(x, y, 200, 300)
    pyautogui.moveTo(x, y)
    pyautogui.click()
# reset_mouse('monitor')


def find_screens(toons):
    screens = []
    for i in range(0, len(toons)):
        toon_window = gw.getWindowsWithTitle('EVE - '+toons[i])[0]
        if toon_window.left > 2000:
            screens.append('monitor')
        if toon_window.left < 2000:
            screens.append('laptop')
    return screens
# print(find_screens(['DangLang']))


def set_active_toon(toon, screen=None):
    # print(toon,screen)
    x, y = pyautogui.position()
    active_window = gw.getActiveWindow().title
    if active_window != 'EVE - ' + toon:
        app = pywinauto.application.Application().connect(title='EVE - ' + toon, found_index=1, timeout=.1)
        app.top_window().set_focus()
        # time.sleep(.1 + random.gamma(3, .1))
        pyautogui.moveTo(x, y)

        # if screen is not None:
        #     if screen == 'laptop':
        #         x, y = 1250, 400
        #     elif screen == 'monitor':
        #         x, y = 4500, 400
        #     pyautogui.moveTo(x, y)
# set_active_toon('Fr4ctured Mind', 'laptop')
# set_active_toon('DangLang', 'monitor')


def double_click_in_space(screen):
    if screen == 'monitor':
        mod = 0.8333
        x, y = 3900, 500
        width = 1100
        height = 700
    if screen == 'laptop':
        mod = 1
        x, y = 1300, 500
        width = 1100
        height = 800
    x, y = randomize_click(x, y, width, height)

    pyautogui.moveTo(x/mod, y/mod)
    time.sleep(0.2)
    interval = np.random.normal(0.12, 0.006, 1)[0]
    pyautogui.click(clicks=2, interval=float(interval))
    interval = np.random.normal(0.12, 0.006, 1)[0]
    time.sleep(interval)
    interval = np.random.normal(0.12, 0.006, 1)[0]
    pyautogui.click(clicks=2, interval=float(interval))
# double_click_in_space('laptop')


def stop_ship():
    pyautogui.keyDown('ctrl')
    time.sleep(.1 + random.gamma(3, .05))
    pyautogui.keyDown('space')
    time.sleep(.1 + random.gamma(3, .03))
    pyautogui.keyUp('space')
    time.sleep(.1 + random.gamma(3, .03))
    pyautogui.keyUp('ctrl')
    time.sleep(.5 + random.gamma(4, .1))


def is_warping(screen):
    if screen == 'laptop':
        x0 = 650
        x1 = x0 + 500
        y0 = 1200
        y1 = y0 + 80
        pathmod = 'laptop_'
    if screen == 'monitor':
        base = 2560           # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 450
        x1 = base + 800
        y0 = 1160
        y1 = 1200
        pathmod = ''
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8
    template = cv2.imread('Templates/Warping/'+pathmod+'warp_drive_active.png')
    result = cv2.matchTemplate(template, search_region, method)
    loc = np.where(result >= threshold)

    if loc[0].shape[0] == 0:
        template2 = cv2.imread('Templates/Warping/'+pathmod+'establishing_warp_vector.png')
        result = cv2.matchTemplate(template2, search_region, method)
        loc = np.where(result >= threshold)
        if loc[0].shape[0] == 0:
            return False
    return True
# while 1 != 0:
#     time.sleep(.5)
#     print(is_warping('laptop'))


def find_next_gate(screen):
    if screen == 'laptop':
        mod = 1
        x0 = 1990
        x1 = x0 + 50
        y0 = 200
        y1 = 1000
    if screen == 'monitor':
        mod = .83333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 2100
        x1 = x0 + 275
        y0 = 150
        y1 = 800
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    hsv = cv2.cvtColor(search_region, cv2.COLOR_BGR2HSV)
    lower_val = np.array([20, 200, 80])
    upper_val = np.array([40, 255, 255])
    yellow = cv2.inRange(hsv, lower_val, upper_val)
    cv2.imwrite('Templates/3_color_threshold.png', yellow)

    yellow = yellow/255
    y, x = np.where(yellow > 0)
    if len(y) == 0:
        return 'no gate found'

    x_center = (round(np.mean(x)) + x0)/mod
    y_center = (round(np.mean(y)) + y0)/mod

    x, y = randomize_click(x_center + 40, y_center, 20, 5)
    pyautogui.moveTo(x, y)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(1)

    return x_center, y_center
# print(find_next_gate('laptop'))


def save_current_system(screen):
    if screen == 'monitor':
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0, x1, y0, y1 = base + 280, base + 500, 0, 400
    if screen == 'laptop':
        mod = 1
        x0 = 115
        x1 = 250
        y0 = 140
        y1 = 170

    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png', cv2.IMREAD_GRAYSCALE)
    cv2.imwrite('Templates/Autopilot/old_system.png', search_region)

    ret, thresh1 = cv2.threshold(search_region, 170, 255, cv2.THRESH_TOZERO)   #eliminates darks
    cv2.imwrite('Templates/Autopilot/thresh1.png', thresh1)

    ret, thresh2 = cv2.threshold(search_region, 220, 255, cv2.THRESH_TOZERO)
    cv2.imwrite('Templates/Autopilot/thresh2.png', thresh2)
    return
# save_current_system('laptop')


def check_new_system(screen):
    if screen == 'monitor':
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0, x1, y0, y1 = base + 280, base + 500, 0, 400
    if screen == 'laptop':
        mod = 1
        x0 = 100
        x1 = 430
        y0 = 135
        y1 = 175
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8

    ret, thresh1 = cv2.threshold(search_region, 180, 255, cv2.THRESH_TOZERO)

    template = cv2.imread('Templates/Autopilot/thresh1.png', cv2.IMREAD_GRAYSCALE)
    result = cv2.matchTemplate(template, thresh1, method)
    loc = np.where(result >= threshold)

    h, w = template.shape[:2]
    for pt in zip(*loc[::-1]):
        cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 2)
    cv2.imwrite('Templates/Autopilot/current_system.png', thresh1)

    if loc[0].shape[0] == 0:
        return 'new system'
    else:
        return 'same system'
# print(check_new_system('laptop'))


def identify_system(screen):
    if screen == 'laptop':
        # x0, y0, x1, y1 = 63, 136, 429, 204
        x0, y0, x1, y1 = 114, 135, 430, 171
    # x, y = find_ui_element(screen, 'system_name', x0, y0, x1, y1, threshold=.9)
    # string = ocr(bbox=(x+10, y-10, x+100, y+20), lng='eng')
    string = ocr(bbox=(x0, y0, x1, y1), lng='eng')
    print(string)
# identify_system('laptop')


def identify_destination(screen, stage=None):
    if screen == 'monitor':
        path = 'Templates/UI Elements/Monitor/'
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0, x1, y0, y1 = base + 280, base + 500, 0, 400
    if screen == 'laptop':
        path = 'Templates/UI Elements/Laptop/'
        mod = 1
        x0 = 50
        x1 = 430
        y0 = 200
        y1 = y0 + 200
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8

    for file in os.listdir(path + 'destinations'):
        # ret, thresh1 = cv2.threshold(search_region, 150, 255, cv2.THRESH_TOZERO)
        desto = cv2.imread(path + 'destinations/' +file, cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(desto, search_region, method)
        loc = np.where(result >= threshold)
        # print(file, np.max(result))
        if loc[0].shape[0] != 0:
            if 'destination' in file:
                return 'No Destination'
            if 'amarr' in file:
                return 'Amarr'
            if 'jita' in file:
                return 'Jita'
            # print(destination, file, np.max(result))
# while 1 != 0:
# print(identify_destination('laptop'))
#     time.sleep(0.5)


def new_sigs(screen, mode=None):
    if screen == 'monitor':
        path = 'Templates/UI Elements/Monitor/'
        base = 2560           # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 450
        x1 = base + 800
        y0 = 0
        y1 = 600
    if screen == 'laptop':
        x0, y0, x1, y1 = 720, 0, 1129, 316
        path = 'Templates/UI Elements/Laptop/'
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .9

    probe_window = cv2.imread(path + 'probe_window.png')
    result = cv2.matchTemplate(probe_window, search_region, method)
    win_loc0 = np.where(result >= threshold)
    if win_loc0[0].shape[0] == 0:
        return False

    template = cv2.imread(path + 'NoNewSigs.png')
    result = cv2.matchTemplate(template, search_region, method)
    loc = np.where(result >= threshold)

    template2 = cv2.imread(path + 'currently_ignoring.png')   ## this is active if all sites+sigs are ignored
    result2 = cv2.matchTemplate(template2, search_region, method)
    loc2 = np.where(result2 >= threshold)

    if loc[0].shape[0] == 0 and loc2[0].shape[0] == 0:
        threading.Thread(target=alarm_sound, args=(['sonar'])).start()
        threading.Thread(target=video_capture, args=('Alerts/Newsig', screen, .5, 30)).start()
        return True
    else:

        return False
# print(new_sigs('laptop'))


def watch_dscan(screen, save='False', number=0, mode=None):
    if mode == 'Observe':
        save_path = 'Alerts/Observe/'
    else:
        save_path = 'Alerts/'
    if screen == 'monitor':
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 50
        x1 = x0 + 300
        y0 = 400
        y1 = 1200
        entry_h = 13
        path = 'Templates/UI Elements/Monitor/'
        whitelist_path = 'Templates/Whitelist/Monitor/'
    if screen == 'laptop':
        x0, y0, x1, y1 = 93, 288, 480, 1268
        entry_h = 15
        path = 'Templates/UI Elements/Laptop/'
        whitelist_path = 'Templates/Whitelist/Laptop/'
    # h = y1 - y0
    # w = x1 - x0
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    threshold = .99
    method = cv2.TM_CCOEFF_NORMED

    ## verify dscan open/unobstructred and crop into correct size ##
    window = cv2.imread(path + 'dscan_window.png')
    result = cv2.matchTemplate(window, search_region, method)
    window_loc = np.where(result >= .95)

    button = cv2.imread(path + 'dscan_button.png')
    result = cv2.matchTemplate(button, search_region, method)
    button_loc = np.where(result >= .95)

    if window_loc[0].shape[0] == 0 or button_loc[0].shape[0] == 0:
        print('\rDscan closed or obstructed', end='')
        return

    ### crop dscan list from larger image ###
    list_region = search_region[window_loc[0][0]+30:button_loc[0][0]-10, window_loc[1][0]:150]
    cv2.imwrite('Alerts/Dscan/list_region.png', list_region)
    grey = cv2.cvtColor(list_region, cv2.COLOR_BGR2GRAY)
    grey = grey[:, 0:22]
    ret, thresh1 = cv2.threshold(grey, 100, 250, cv2.THRESH_BINARY)

    #### count previous saved alerts, prepping for new one ####
    alert_directory = save_path
    alerts = [0]
    for file in os.listdir(alert_directory):
        if 'Alert' in file:
            alerts.append(int(file[file.find(' '):file.find('-')]))
    recent_alert_number = f'{max(alerts)}'
    new_alert_number = f'Alert {max(alerts) + 1}'
    if save == True:
        cv2.imwrite(alert_directory + recent_alert_number + ' -followup ' + number + '.png', search_region)
        return

    ####   blob detection   ####
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = False
    params.filterByInertia = False
    params.filterByConvexity = False
    params.filterByCircularity = False
    params.filterByColor = False
    detector = cv2.SimpleBlobDetector_create(params)  # Set up the detector with default parameters.
    keypoints = detector.detect(thresh1)  # Detect blobs.
    dscan_list = []
    for keyPoint in keypoints:
        x = round(keyPoint.pt[0])
        y = round(keyPoint.pt[1])
        s = round(keyPoint.size)
        dscan_list.append(y)
    dscan_list = sorted(dscan_list)
    im_with_keypoints = cv2.drawKeypoints(thresh1, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite('Alerts/Dscan/entries.png', im_with_keypoints)

    ##### iterating over entries on dscan
    for ship in range(0, len(dscan_list)):
        newobject = True
        y = dscan_list[ship]   # y coord from blob detection
        dscan_entry_region = list_region[y - entry_h:y + entry_h, :]  # creating box around y coord

        ###### comparing each listing on the dscan against whitelisted objects
        # white_list_directory = 'Templates/Whitelist/'
        for file in os.listdir(whitelist_path):
            white_list_object = os.fsdecode(file)
            whitelist_template = cv2.imread(whitelist_path + white_list_object)
            result = cv2.matchTemplate(whitelist_template, dscan_entry_region, method)
            loc = np.where(result >= threshold)

            ##### if dscan entry is a whitelisted object
            if loc[0].shape[0] != 0:
                newobject = False
                break  # object white-listed, continues on to next dscan entry

        # ----- if dscan entry is an unknown object -----
        if newobject is True:
            # threading.Thread(target=video_capture, args=('Alerts/'+ new_alert_number + '-Dscan-'+ screen, screen, .5, 30)).start()
            cv2.imwrite(alert_directory + new_alert_number + '-Dscan-'+ screen+ '.png', search_region)
            cv2.imwrite('Alerts/Dscan/new_object_box.png', dscan_entry_region)
            return 'new object'  # found possible enemy

    return False
# print(watch_dscan('laptop'))
# print(watch_dscan('monitor'))


def target_locked(screen):
    if screen == 'laptop':
        path = 'Templates/UI Elements/Laptop/'
        mod = 1
        bbox = (1728, 0, 1968, 139)
    if screen == 'monitor':
        path = 'Templates/UI Elements/Monitor/'
        mod = 0.833
        bbox = (4640, 0, 2500, 120)
    ImageGrab.grab(bbox=bbox, all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .7

    target = cv2.imread(path + 'target_locked.png', cv2.IMREAD_GRAYSCALE)
    result = cv2.matchTemplate(target, search_region, method)
    loc = np.where(result >= threshold)
    # print(np.max(result))
    if loc[0].shape[0] == 0:
        return 'no target'
    if loc[0].shape[0] != 0:
        return 'target'
# print(target_locked('monitor'))
# print(target_locked('laptop'))


def selected_item(screen, action=None):
    if screen == 'laptop':
        path = 'Templates/UI Elements/Laptop/'
        mod = 1
        x0 = 1950
        x1 = x0 + 500
        y0 = 0
        y1 = 160
    if screen == 'monitor':
        path = 'Templates/UI Elements/Monitor/'
        mod = 0.833
        base = 2540  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 2050
        x1 = x0 + 400
        y0 = 0
        y1 = 120
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8

    no_object = cv2.imread(path + 'no_object_selected.png', cv2.IMREAD_GRAYSCALE)
    result = cv2.matchTemplate(no_object, search_region, method)
    loc = np.where(result >= threshold)
    # print(np.max(result))
    if loc[0].shape[0] != 0:
        return 'no object selected'

    # ---- check gate for important or dangerous systems ----
    for file in os.listdir(path + 'dangerous gates/'):
        # ahbazon_gate = cv2.imread(path + 'dangerous gates/' +'ahbazon_gate.png', cv2.IMREAD_GRAYSCALE)
        # result = cv2.matchTemplate(ahbazon_gate, search_region, method)

        gate = cv2.imread(path + 'dangerous gates/' + file, cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(gate, search_region, method)
        loc = np.where(result >= threshold)
        if loc[0].shape[0] != 0 and action is None:
            # print(file[:-4])
            return f'dangerous gate {file[:-4]}'

    if action == 'approach':
        align = cv2.imread(path + 'approach.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(align, search_region, method)
        loc = np.where(result >= threshold)
        h, w = align.shape[:2]
        y = round((y0 + loc[0][0] + h / 2) / mod)
        x = round((x0 + loc[1][0] + w / 2) / mod)
        x, y = randomize_click(x, y, w * .8, h * .8)
        pyautogui.moveTo(x, y)
        pyautogui.click()
        if screen == 'monitor':
            x, y = randomize_click(4500, 500, 200, 300)
        if screen == 'laptop':
            x, y = randomize_click(1300, 400, 200, 300)
        pyautogui.moveTo(x, y)
        return

    if action == 'align':
        align = cv2.imread(path + 'align.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(align, search_region, method)
        loc = np.where(result >= threshold)
        h, w = align.shape[:2]
        y = round((y0 + loc[0][0] + h / 2) / mod)
        x = round((x0 + loc[1][0] + w / 2) / mod)
        x, y = randomize_click(x, y, w * .8, h * .8)
        pyautogui.moveTo(x, y)
        pyautogui.click()
        if screen == 'monitor':
            x, y = randomize_click(4500, 500, 200, 300)
        if screen == 'laptop':
            x, y = randomize_click(1300, 400, 200, 300)
        pyautogui.moveTo(x, y)

        dock = cv2.imread(path + 'dock.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(dock, search_region, method)
        loc = np.where(result >= threshold)
        if loc[0].shape[0] != 0:
            return 'at destination'

    if action == 'warp':
        warp_to = cv2.imread(path + 'warp_to.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(warp_to, search_region, method)
        loc = np.where(result >= threshold)
        h, w = warp_to.shape[:2]

        y = round((y0 + loc[0][0] + h / 2) / mod)
        x = round((x0 + loc[1][0] + w / 2) / mod)
        x, y = randomize_click(x, y, w * .8, h * .8)
        pyautogui.moveTo(x, y)
        pyautogui.click()
        return

    if action == 'warp/dock':  #warps or docks depending on whats available
        dock = cv2.imread(path + 'dock.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(dock, search_region, method)
        dock_loc = np.where(result >= threshold)
        if dock_loc[0].shape[0] != 0:
            h, w = dock.shape[:2]
            y = round((y0 + dock_loc[0][0] + h / 2) / mod)
            x = round((x0 + dock_loc[1][0] + w / 2) / mod)
            x, y = randomize_click(x, y, w * .8, h * .8)
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click()
            time.sleep(1)

            if screen == 'monitor':
                x, y = randomize_click(4500, 500, 200, 300)
            if screen == 'laptop':
                x, y = randomize_click(1300, 400, 200, 300)
            pyautogui.moveTo(x, y)
            return 'at destination'

        jump = cv2.imread(path + 'jump_gate.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(jump, search_region, method)
        jump_loc = np.where(result >= threshold)
        if jump_loc[0].shape[0] != 0:
            h, w = jump.shape[:2]
            y = round((y0 + jump_loc[0][0] + h / 2) / mod)
            x = round((x0 + jump_loc[1][0] + w / 2) / mod)
            x, y = randomize_click(x, y, w * .8, h * .8)
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click()
            time.sleep(0.5)
            if screen == 'monitor':
                x, y = randomize_click(4500, 500, 200, 300)
            if screen == 'laptop':
                x, y = randomize_click(1300, 400, 200, 300)
            pyautogui.moveTo(x, y)
            return 'in route'

    if action == 'orbit':  #warps or docks depending on whats available
        orbit = cv2.imread(path + 'orbit.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(orbit, search_region, method)
        jump_loc = np.where(result >= threshold)
        if jump_loc[0].shape[0] != 0:
            h, w = orbit.shape[:2]
            y = round((y0 + jump_loc[0][0] + h / 2) / mod)
            x = round((x0 + jump_loc[1][0] + w / 2) / mod)
            x, y = randomize_click(x, y, w * .8, h * .8)
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pyautogui.click()
            time.sleep(0.5)
            if screen == 'monitor':
                x, y = randomize_click(4500, 500, 200, 300)
            if screen == 'laptop':
                x, y = randomize_click(1300, 400, 200, 300)
            pyautogui.moveTo(x, y)
            return

    if action is None:
        dock = cv2.imread(path + 'dock.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(dock, search_region, method)
        loc = np.where(result >= threshold)
        if loc[0].shape[0] != 0:
            return 'at destination'
    return 'in route'

    # align = cv2.imread('Templates/UI Elements/align.png', cv2.IMREAD_GRAYSCALE)
    # approach = cv2.imread('Templates/UI Elements/approach.png', cv2.IMREAD_GRAYSCALE)
    # warp_to = cv2.imread('Templates/UI Elements/warp_to.png', cv2.IMREAD_GRAYSCALE)

# progress = selected_item('laptop')
# if 'dangerous' in progress:
    # print(progress[15:])
# print(selected_item('laptop', action='orbit'))


def watch_overview(screen, mode=None):
    if mode == 'Observe':
        save_path = 'Alerts/Observe/'
    else:
        save_path = 'Alerts/'
    if screen == 'monitor':
        path = 'Templates/UI Elements/Monitor/'
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 2140
        x1 = x0 + 275
        y0 = 150
        y1 = y0 + 500
    if screen == 'laptop':
        path = 'Templates/UI Elements/Laptop/'
        x0 = 1980
        x1 = x0 + 450
        y0 = 210
        y1 = y0 + 550
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/overview_Search_Region.png')
    search_region = cv2.imread('Templates/overview_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .95

    #### verify overview is not blocked by other windows #####
    overview_visible = cv2.imread(path + 'overview_open.png')
    result = cv2.matchTemplate(overview_visible, search_region, method)
    loc = np.where(result >= threshold)
    if loc[0].shape[0] == 0:
        return 'Overview blocked'

    ##### determine bottom boundary of overview list #####
    edge = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
    ret, edgethresh = cv2.threshold(edge, 40, 255, cv2.THRESH_TOZERO)  # eliminates darks
    # cv2.imwrite('Templates/Overview/overview_threshold.png', edgethresh)
    zero_row = 0
    for ystop, row in enumerate(edgethresh):
        # print(sum(row))
        if sum(row) == 0:
            zero_row += 1
        else:
            zero_row = 0
        if zero_row > 15:
            break
    # ystop is last index where last 15 rows were equal to zero
    search_region = search_region[:ystop, :]

    ##### counts out all the alert screenshots in order to name the new one ####
    alert_directory = save_path
    alerts = [0]
    for file in os.listdir(alert_directory):
        if 'Alert' in file:
            alerts.append(int(file[file.find(' '):file.find('-')]))
    filename = f'Alert {max(alerts) + 1}'

    if mode != 'Ignore':
        #### detects red color used for NPCs
        hsv = cv2.cvtColor(search_region, cv2.COLOR_BGR2HSV)
        lower_val = np.array([0, 42, 120])
        upper_val = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_val, upper_val)
        # cv2.imwrite('Templates/3_color_threshold.png', mask)
        red_pixels = cv2.countNonZero(mask)
        if red_pixels > 15:
            cv2.imwrite(alert_directory + filename + ' -Overview.png', search_region)
            return 'NPCs on grid'

    #### detects grey color for other players
    grey = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(grey, 90, 255, cv2.THRESH_TOZERO)   #eliminates darks
    ret, thresh1 = cv2.threshold(thresh1, 110, 0, cv2.THRESH_TOZERO_INV) #eliminates whites
    pixels = cv2.countNonZero(thresh1)
    cv2.imwrite('Templates/Overview/overview_threshold.png', thresh1)
    if pixels > 1500:
        cv2.imwrite(alert_directory+filename+' -Overview.png', search_region)
        # cv2.imwrite('Templates/Overview/overview_threshold.png', thresh1)
        return 'Player on grid'

    return None
# print(watch_overview('laptop'))
# while 1 != 0:
#     print(watch_overview())
#     time.sleep(.5)


def find_on_overview(icon, screen, click=False):
    if screen == 'laptop':
        mod = 1
        x0, y0, x1, y1 = 1982, 206, 2487, 1025
        path = 'Templates/Overview/Laptop/'
    if screen == 'monitor':
        mod = 0.8333
        x0, y0, x1, y1 = 4679, 150, 5024, 882
        path = 'Templates/Overview/Monitor/'
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    # print(icon, screen)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .9

    template = cv2.imread(path + icon+'.png')
    result = cv2.matchTemplate(template, search_region, method)
    loc = np.where(result >= threshold)
    # print(loc)
    # print(loc[1][0])

    h, w = template.shape[:2]

    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    # cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    if loc[0].shape[0] == 0:
        return 'not found'
    y = round((y0 + loc[0][0] + h/2)/mod)
    x = round((x0 + loc[1][0] + w/2 + 40)/mod)
    if click is True:
        xrand, yrand = randomize_click(x, y, 100, h * .8)
        pyautogui.moveTo(xrand, yrand)
        time.sleep(.1 + random.gamma(2, .1))
        pyautogui.click()
        time.sleep(.2 + random.gamma(3, .1))
    return x, y
# find_on_overview('asteroid_omber', 'laptop', click=True)
# x,y = find_on_overview('asteroid', 'laptop')
# x, y = find_on_overview('sun', 'laptop')
# pyautogui.moveTo(x, y)

# def lockup_object(x, y, screen):
#     pyautogui.moveTo(x, y)
#     time.sleep(0.2)
#
#     pyautogui.keyDown('ctrl')
#     time.sleep(.7)
#     pyautogui.click()
#     time.sleep(0.2)
#     pyautogui.click()
#     time.sleep(0.5)
#     pyautogui.keyUp('ctrl')
#     time.sleep(0.5)


def on_grid_with(icon, screen):

    location = find_on_overview(icon, screen)
    if location == 'not found':
        return 'wrong overview tab'

    x, y = location[0], location[1]

    if screen == 'laptop':
        mod = 1
        path = 'Templates/Overview/Laptop/'
    if screen == 'monitor':
        mod = 0.8333
        path = 'Templates/Overview/Monitor/'

    ImageGrab.grab(bbox=(x, y-15, x + 130, y+15), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .9

    template = cv2.imread(path + 'AU.png')
    result = cv2.matchTemplate(template, search_region, method)
    loc = np.where(result >= threshold)
    h, w = template.shape[:2]

    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    # cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    if loc[0].shape[0] == 0:
        return 'on grid'
    else:
        return 'off grid'
# print(on_grid_with('fortizar', 'laptop'))


def change_tab(tab, screen):
    if screen == 'laptop':
        mod = 1
        x0 = 1950
        x1 = x0 + 500
        y0 = 150
        y1 = y0 + 100
        path = 'Templates/Overview/Laptop/'
    if screen == 'monitor':
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 2100
        x1 = x0 + 400
        y0 = 100
        y1 = y0 + 80
        path = 'Templates/Overview/Monitor/'
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .9

    template = cv2.imread(path + tab+'.png')
    result = cv2.matchTemplate(template, search_region, method)
    loc = np.where(result >= threshold)
    h, w = template.shape[:2]

    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    # cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    if loc[0].shape[0] == 0:
        print('cant find overview tab')
        return 'cannot find'
    y = round((y0 + loc[0][0] + h/2)/mod)
    x = round((x0 + loc[1][0] + w/2)/mod)

    grey = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
    grey = grey[loc[0][0]+h:loc[0][0]+h+20, loc[1][0]:loc[1][0]+w]
    ret, thresh1 = cv2.threshold(grey, 70, 255, cv2.THRESH_TOZERO)  # eliminates darks
    pixels = cv2.countNonZero(thresh1)
    if pixels > 15:
        # print('tab selected')
        return

    x, y = randomize_click(x, y, w, h)
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(.1 + random.gamma(3, .15))

    if screen == 'monitor':
        x, y = 4700, 200
    if screen == 'laptop':
        x, y = 1800, 200
    x, y = randomize_click(x, y, 200, 100)
    pyautogui.moveTo(x, y)
    return
# change_tab('pve_tab', 'monitor')


def dock_up(screen):
    # x, y = find_on_overview('fortizar_icon', screen)
    x, y = find_bookmark('fortizar', screen)

    pyautogui.moveTo(x, y)
    pyautogui.click(button='right')
    time.sleep(.3 + random.gamma(3, .1))
    x, y = find_in_context_menu(x, y, 'dock', screen)
    xloc, yloc = randomize_click(x, y, 30, 8)
    pyautogui.moveTo(xloc, yloc)
    pyautogui.click()
# dock_up('laptop')


# def dock_up(toon, screen):
#     active_window = gw.getActiveWindow().title
#     if active_window != 'EVE - ' + toon:
#         gw.getWindowsWithTitle('EVE - ' + toon)[0].activate()
#         time.sleep(.5)
#     x, y = find_on_overview('fortizar_icon', screen)
#
#     pyautogui.moveTo(x, y)
#     pyautogui.click(button='right')
#     time.sleep(0.5)
#     x, y = find_in_context_menu(x, y, 'dock', screen)
#     xloc, yloc = randomize_click(x, y, 30, 8)
#     pyautogui.moveTo(xloc, yloc)
#     # pyautogui.click()
# # dock_up('Zoe Washborn', 'laptop')

def active_modules(screen):

    screenshots = 3
    modules_per_row = 4
    sensitivity = 200

    if screen == 'laptop':
        module_gap = 63
        row_gap = 56
        radius = 29
        path = 'Templates/UI Elements/Laptop/'
        bbox = (891, 1377, 1321, 1569)
    if screen == 'monitor':
        module_gap = 45
        row_gap = 40
        radius = 28
        path = 'Templates/UI Elements/Monitor/'
        bbox = (3200, 1285, 3488, 1417)

    ImageGrab.grab(bbox=bbox, all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .95


    modules = cv2.imread(path + 'ship_controller.png')
    result = cv2.matchTemplate(modules, search_region, method)
    module_loc = np.where(result >= threshold)
    modx = module_loc[1][0] + 100
    # mody = module_loc[0][0]
    top_row = 41

    greater_module_array = np.zeros([screenshots, 3, modules_per_row])
    for t, screenshot in enumerate(greater_module_array):
        ImageGrab.grab(bbox=bbox, all_screens=True).save('Templates/1_Search_Region.png')
        search_region = cv2.imread('Templates/1_Search_Region.png')

        hsv = cv2.cvtColor(search_region, cv2.COLOR_BGR2HSV)
        lower_val = np.array([37, 42, 0])
        upper_val = np.array([84, 255, 255])
        mask = cv2.inRange(hsv, lower_val, upper_val)

        module_array = np.zeros([3, modules_per_row])
        for j, row in enumerate(module_array):
            ypos = top_row + row_gap*j
            for i, slot in enumerate(row):
                xpos = int(i * module_gap)
                if j == 1:
                    xpos = xpos + 30
                top = ypos - radius
                bottom = ypos + radius
                left = modx + xpos - radius
                right = modx + xpos + radius
                slot_mask = mask[top: bottom, left: right]

                hh, ww = slot_mask.shape[:2]
                xc = hh // 2
                yc = ww // 2
                background = np.full_like(slot_mask, 255)
                blackcenter = cv2.circle(background, (xc, yc), radius+1, (0, 0, 0), -1)
                mask1 = cv2.circle(blackcenter, (xc, yc), radius-8, (255, 255, 255), -1)
                cv2.imwrite('Templates/Modules/modules_mask.png', mask1)
                slot_mask = cv2.subtract(slot_mask, mask1)

                if t == 0:
                    cv2.imwrite(f'Templates/Modules/Active/1_module_mask {j,i}.png', slot_mask)
                    h, w = radius, radius
                    cv2.circle(search_region, (modx + xpos, ypos), radius+1, (0, 0, 255), 1)
                    cv2.circle(search_region, (modx + xpos, ypos), radius-8, (0, 0, 255), 1)
                    cv2.imwrite('Templates/Modules/modules_region.png', search_region)
                    # cv2.imwrite(f'Templates/Modules/Active/mask_region.png', mask)
                hasGreen = round(np.sum(slot_mask)/255)
                greater_module_array[t, j, i] = hasGreen
        time.sleep(0.1)
    # print(greater_module_array)

    green_array = np.zeros([3, modules_per_row])
    for j, row in enumerate(module_array):
        for i, slot in enumerate(row):
            snapshots = []
            for t, screenshot in enumerate(greater_module_array):
                snapshots.append(greater_module_array[t, j, i])
            difference = max(snapshots) - min(snapshots)

            # if difference > 0:
            #     print(difference)

            if difference > sensitivity:
                green_array[j, i] = True
            else:
                green_array[j, i] = False
    return green_array
# print(active_modules('laptop'))


def toggle_module(module):
    if module == 'cloak':
        pyautogui.keyDown('alt')
        time.sleep(.1 + random.gamma(3, .05))
        pyautogui.keyDown('f1')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('f1')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('alt')
    if module == 'MWD':
        pyautogui.keyDown('alt')
        time.sleep(.1 + random.gamma(3, .05))
        pyautogui.keyDown('f2')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('f2')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('alt')
    if module == 'MWD + cloak':
        pyautogui.keyDown('alt')
        time.sleep(.1 + random.gamma(3, .05))
        pyautogui.keyDown('f1')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyDown('f2')
        time.sleep(.1 + random.gamma(2, .01))
        pyautogui.keyUp('f1')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('f2')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('alt')
        time.sleep(.1 + random.gamma(2, .01))
    if module == 'low1':
        pyautogui.keyDown('1')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('1')
        time.sleep(.1 + random.gamma(3, .03))
    if module == 'low2':
        pyautogui.keyDown('2')
        time.sleep(.1 + random.gamma(2, .01))
        pyautogui.keyUp('2')
        time.sleep(.1 + random.gamma(3, .03))
    if module == 'high3':
        pyautogui.keyDown('f3')
        time.sleep(.1 + random.gamma(2, .01))
        pyautogui.keyUp('f3')
        time.sleep(.1 + random.gamma(3, .03))
# toggle_module('cloak')


def set_fleet_formation(formation,screen):
    if screen == 'laptop':
        mod = 1
        region = (1573, 1142, 2534, 1532)
        path = 'Templates/UI Elements/Laptop/'
    if screen == 'monitor':
        mod = 0.8333
        region = (4399, 1030, 5094, 1393)
    ImageGrab.grab(bbox=region, all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8

    fleet_window = cv2.imread(path + 'fleet_window.png')
    result = cv2.matchTemplate(fleet_window, search_region, method)
    loc = np.where(result >= threshold)
    # x_fleet_window = loc[1][0]
    # y_fleet_window = loc[0][0]

    if formation == 'point':

        point_formation = cv2.imread(path + 'formation_point_active.png')
        result = cv2.matchTemplate(search_region, point_formation, method)
        point_loc = np.where(result >= threshold)
        h, w = point_formation.shape[:2]

        if point_loc[0].shape[0] == 0:
            print('\rOPEN FORMATION WINDOW')
            return

        x = point_loc[1][0]
        y = point_loc[0][0]

        for pt in zip(*point_loc[::-1]):
            cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    if formation == 'sphere':
        sphere_formation = cv2.imread(path + 'formation_sphere_active.png')
        result = cv2.matchTemplate(search_region, sphere_formation, method)
        sphere_loc = np.where(result >= threshold)
        h, w = sphere_formation.shape[:2]

        if sphere_loc[0].shape[0] == 0:
            print('\rOPEN FORMATION WINDOW')
            return

        x = sphere_loc[1][0]
        y = sphere_loc[0][0]

        for pt in zip(*sphere_loc[::-1]):
            cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    active_region = search_region[y:y + h, x:x+w]
    hsv = cv2.cvtColor(active_region, cv2.COLOR_BGR2HSV)
    lower_val = np.array([20, 200, 80])
    upper_val = np.array([40, 255, 255])
    yellow = cv2.inRange(hsv, lower_val, upper_val)

    hasYellow = round(np.sum(yellow)/255)
    # cv2.imwrite('Templates/3_color_threshold.png', yellow)

    if hasYellow < 20:
        x_move = x + region[0] + w/2
        y_move = y + region[1] + h/2
        pyautogui.moveTo(x_move, y_move)
        time.sleep(.1 + random.gamma(3, .05))
        pyautogui.click()
    return
# set_fleet_formation('point', 'monitor')


def find_bookmark(where, screen):
    if screen == 'monitor':
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0, x1, y0, y1 = base + 280, base + 500, 0, 400
        path = 'Templates/Bookmarks/Monitor/'
    if screen == 'laptop':
        mod = 1
        x0, x1, y0, y1 = 350, 800, 0, 800
        path = 'Templates/Bookmarks/Laptop/'
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .95

    if 'dock' in where:
        template = cv2.imread(path + where + '.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(template, search_region, method)
        loc = np.where(result >= threshold)
        h, w = template.shape[:2]
        if loc[0].shape[0] == 0:
            return 'no bookmark found'
    else:
        template = cv2.imread(path + where +'.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(template, search_region, method)
        loc = np.where(result >= threshold)
        h, w = template.shape[:2]
        if loc[0].shape[0] == 0:
            return 'no bookmark found'

    for pt in zip(*loc[::-1]):
        cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (255, 0, 255), 2)
    cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    y = round((y0 + loc[0][0] + h/2)/mod)
    x = round((x0 + loc[1][0] + w/2)/mod)

    if where == 'top_bm':
        x += 60
        w = 60
    x, y = randomize_click(x, y, w, h*0.8)
    return x, y
# x, y = find_bookmark('ORE 3', 'laptop')
# print(find_bookmark('fort', 'laptop'))
# pyautogui.moveTo(x, y)


def warp_to_bookmark(who, where, screen):
    location = find_bookmark(where, screen)
    if location == 'no bookmark found':
        print(f' {where} bookmark not found')
        return 'not found'
    x, y = location[0], location[1]

    pyautogui.moveTo(x, y)
    time.sleep(0.3)
    pyautogui.click(button='right')
    time.sleep(.5 + random.gamma(4, .1))

    if who == 'Self':
        what = 'warp_self'
    elif who == 'Squad':
        what = 'warp_squad'
    result = find_in_context_menu(x, y, what, screen)
    if type(result) is str:
        # print(result)
        reset_mouse(screen)
        return result
    else:
        x, y = randomize_click(result[0], result[1], 50, 8)
        pyautogui.moveTo(x, y)
        pyautogui.click()
        return 'initiating warp'
# print(warp_to_bookmark('self', 'instadock', 'monitor'))


def determine_current_crystal(screen):
    if screen == 'laptop':
        bbox1 = 1971, 0, 2331, 106
        bbox2 = 924, 1339, 1211, 1516
    if screen == 'monitor':
        bbox1 = 4498, 0, 5119, 132
        bbox2 = 3228, 1255, 3465, 1397
    threshold = .95

    # --- check for variegated first
    response = find_ui_element(screen, 'variegated', bbox2[0], bbox2[1], bbox2[2], bbox2[3],
                               threshold=threshold, silent=True)
    if response != 'not found':
        current_crystal = 'variegated'
    else:
        # ---- check for coherent
        response = find_ui_element(screen, 'coherent', bbox2[0], bbox2[1], bbox2[2], bbox2[3],
                                   threshold=threshold, silent=True)
        if response != 'not found':
            current_crystal = 'coherent'
        else:
            # ----- check for unloaded
            response = find_ui_element(screen, 'stripminer2', bbox2[0], bbox2[1], bbox2[2], bbox2[3],
                                   threshold=threshold, silent=True)
            if response != 'not found':
                current_crystal = 'none'
            else:
                print('no mining modules detected')
    return current_crystal
# print(determine_current_crystal('laptop'))


def load_mining_crystal(screen, crystal=None):
    if screen == 'laptop':
        bbox1 = 1971, 0, 2331, 106
        # bbox1 = 2256, 236, 2324, 258  # top listing in type column of overview
        bbox2 = 924, 1339, 1211, 1516
    if screen == 'monitor':
        bbox1 = 4498, 0, 5119, 132
        bbox2 = 3228, 1255, 3465, 1397
    threshold = .95

    # asteroid_types = ['omber', 'kernite', 'gneiss']
    # for asteroid in asteroid_types:
    #     response = find_ui_element(screen, 'asteroid_'+asteroid, bbox1[0], bbox1[1], bbox1[2], bbox1[3],
    #                                 threshold=threshold, silent=True)
    #     if response != 'not found':
    #         selected_asteroid = asteroid
    #         if selected_asteroid == 'omber' or selected_asteroid == 'kernite':
    #             crystal = 'coherent'
    #         if selected_asteroid == 'gneiss':
    #             crystal = 'variegated'
    # print(response)
    # x, y = randomize_click(response[0], response[1], 50, 8)
    # pyautogui.moveTo(x, y)
    # quit()

    time.sleep(0.05)
    response = find_ui_element(screen, 'stripminer2', bbox2[0], bbox2[1], bbox2[2], bbox2[3], button='right', threshold=threshold, silent=True)
    if response == 'not found':
        if crystal == 'coherent':
            time.sleep(0.05)
            response = find_ui_element(screen, 'variegated', bbox2[0], bbox2[1], bbox2[2], bbox2[3], button='right', threshold=threshold, silent=True)
        elif crystal == 'variegated':
            time.sleep(0.05)
            response = find_ui_element(screen, 'coherent', bbox2[0], bbox2[1], bbox2[2], bbox2[3], button='right', threshold=threshold, silent=True)
    if response == 'not found':
        return 'correct crystals installed'

    time.sleep(0.05)
    result = find_in_context_menu(response[0], response[1], crystal, screen)
    if result == 'not found in context menu':
        quit()
    x, y = randomize_click(result[0], result[1], 50, 8)
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(.3 + random.gamma(4, .1))
# print(load_mining_crystal('laptop', 'coherent'))
# print(load_mining_crystal('laptop', 'variegated'))


def select_mineral(screen, current_crystal=None, maxrange=14000):
    if screen == 'laptop':
        bbox1 = 2254, 236, 2408, 1147  # overview 'type' column
        bbox2 = 924, 1339, 1211, 1516  # crystals
    if screen == 'monitor':
        bbox1 = 4498, 0, 5119, 132
        bbox2 = 3228, 1255, 3465, 1397
    threshold = .95

    if current_crystal is None:
        current_crystal = determine_current_crystal(screen)
    new_crystal = []
    asteroid_types = ['omber', 'kernite', 'gneiss']

    # ----- find top asteroids of each type -----
    omber_loc = []
    kernite_loc = []
    gneiss_loc = []
    top_asteroid = []
    for a, asteroid in enumerate(asteroid_types):
        response = find_ui_element(screen, 'asteroid_'+asteroid, bbox1[0], bbox1[1], bbox1[2], bbox1[3],
                                    threshold=threshold, silent=True)
        # print(response)
        if response != 'not found':
            x = round(response[0])
            y = round(response[1])
            if asteroid == 'omber':
                omber_loc.append(y)
            if asteroid == 'kernite':
                kernite_loc.append(y)
            if asteroid == 'gneiss':
                gneiss_loc.append(y)

    # ---- if no rocks found on grid -----
    if not omber_loc and not kernite_loc and not gneiss_loc:
        return 100001

    #  ------ create array of top location for each asteroid type -----
    if omber_loc:
        top_asteroid.append(min(omber_loc))
    else:
        top_asteroid.append(888888)
    if kernite_loc:
        top_asteroid.append(min(kernite_loc))
    else:
        top_asteroid.append(888888)
    if gneiss_loc:
        top_asteroid.append(min(gneiss_loc))
    else:
        top_asteroid.append(888888)

    # --- determine which rocks are at which positions on the overview -----
    if current_crystal == 'none':
        top_rock = min(top_asteroid)
        top_type = asteroid_types[top_asteroid.index(top_rock)]
        if top_type == 'omber' or top_type == 'kernite':
            new_crystal = 'coherent'
        if top_type == 'gneiss':
            new_crystal = 'variegated'
    if current_crystal == 'coherent':
        top_rock = min(top_asteroid[0], top_asteroid[1])
        top_type = asteroid_types[top_asteroid.index(top_rock)]
        if top_rock == 888888:
            new_crystal = 'variegated'
            top_rock = top_asteroid[2]
            top_type = 'gneiss'
    if current_crystal == 'variegated':
        top_rock = top_asteroid[2]
        top_type = 'gneiss'
        if top_rock == 888888:
            new_crystal = 'coherent'
            top_rock = min(top_asteroid[0], top_asteroid[1])
            top_type = asteroid_types[top_asteroid.index(top_rock)]
    # print(top_asteroid)
    # print(top_rock, top_type)


    # ----- find distance to top asteroid that matches the current crystal ----
    y = top_rock
    distance = ocr(bbox=(x - 250, y - 10, 2262, y + 10), lng='eng', mode='distance')  # top of overview window

    # ----- if in range, begin harvest
    if distance <= maxrange:
        if new_crystal:
            print(f'\r Loading {new_crystal} crystals', end='')
            load_mining_crystal(screen, new_crystal)
            time.sleep(.2 + random.gamma(2, .1))
            load_mining_crystal(screen, new_crystal)
            time.sleep(.2 + random.gamma(2, .1))
        else:
            load_mining_crystal(screen, current_crystal)
        xrand, yrand = randomize_click(x, y, 50, 8)
        pyautogui.moveTo(xrand, yrand)
        time.sleep(.1 + random.gamma(2, .1))
        pyautogui.click()
        return distance

    # ----- if closest matching asteroid too far, try other crystal type
    elif distance > maxrange:
        if top_type == 'omber' or top_type == 'kernite':
            new_crystal = 'variegated'
            top_type = 'gneiss'
            top_rock = top_asteroid[2]
        elif top_type == 'gneiss':
            new_crystal = 'coherent'
            top_type = asteroid_types[top_asteroid.index(top_rock)]
            top_rock = min(top_asteroid[0], top_asteroid[1])

        y = top_rock
        distance = ocr(bbox=(x - 250, y - 10, 2262, y + 10), lng='eng', mode='distance')  # top of overview window

        if distance <= maxrange:
            if new_crystal:
                print(f'\r Loading {new_crystal} crystals', end='')
                load_mining_crystal(screen, new_crystal)
                time.sleep(.2 + random.gamma(2, .1))
                load_mining_crystal(screen, new_crystal)
                time.sleep(.2 + random.gamma(2, .1))
            xrand, yrand = randomize_click(x, y, 50, 8)
            pyautogui.moveTo(xrand, yrand)
            time.sleep(.1 + random.gamma(2, .1))
            pyautogui.click()
            return distance
        else:
            return 100001
# print(select_mineral('laptop', current_crystal='none', maxrange=14000))
# print(select_mineral('laptop', current_crystal='coherent', maxrange=14000))
# print(select_mineral('laptop', current_crystal='variegated', maxrange=14000))


def open_mining_hold(screen):
    if screen == 'monitor':
        template_path = 'Templates/UI Elements/Monitor/'
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 400
        x1 = x0 + 600
        y0 = 1000
        y1 = 1440
    if screen == 'laptop':
        template_path = 'Templates/UI Elements/Laptop/'
        mod = 1
        x0 = 700
        x1 = x0 + 600
        y0 = 1000
        y1 = 1600
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8

    controller = cv2.imread(template_path + 'ship_controller.png')
    result = cv2.matchTemplate(controller, search_region, method)
    loc = np.where(result >= .9)
    h, w = controller.shape[:2]
    y, x = loc[0][0] + y0-30, loc[1][0] + x0-30

    x, y = randomize_click(x, y, 20, 20)
    pyautogui.moveTo(x/mod, y/mod)
    time.sleep(0.5)
    pyautogui.click(button='right')
    time.sleep(.3 + random.gamma(4, .1))

    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    mining_hold = cv2.imread(template_path + 'open_mining_hold.png')
    result = cv2.matchTemplate(mining_hold, search_region, method)
    loc = np.where(result >= threshold)
    h, w = mining_hold.shape[:2]
    y, x = loc[0][0] +h/2 + y0, loc[1][0] + w/2 + x0


    # pyautogui.keyDown('shift')
    # time.sleep(.11)
    x, y = randomize_click(x, y, w, h)
    pyautogui.moveTo(x / mod, y / mod)
    time.sleep(0.4)
    pyautogui.click()
    time.sleep(.3 + random.gamma(4, .08))
    # pyautogui.keyUp('shift')
    # time.sleep(0.5)

    reset_mouse(screen)
# open_mining_hold('laptop')


def mining_hold(screen, query=None):
    if screen == 'monitor':
        template_path = 'Templates/UI Elements/Monitor/'
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 1400
        x1 = x0 + 800
        y0 = 800
        y1 = 1440
    if screen == 'laptop':
        template_path = 'Templates/UI Elements/Laptop/'
        mod = 1
        x0 = 1400
        x1 = x0 + 800
        y0 = 1100
        y1 = 1600
        where = 'laptop_'
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    method = cv2.TM_CCOEFF_NORMED
    threshold = .8

    mining_hold = cv2.imread(template_path + 'mining_hold.png')
    result = cv2.matchTemplate(mining_hold, search_region, method)
    loc = np.where(result >= threshold)
    h, w = mining_hold.shape[:2]
    if loc[0].shape[0] == 0:
        return 'Cargohold Closed'
    new_y, new_x = loc[0][0] + y0, loc[1][0] + x0

    ImageGrab.grab(bbox=(new_x, new_y, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png')

    empty_hold = cv2.imread(template_path + 'empty_cargohold.png')
    result = cv2.matchTemplate(empty_hold, search_region, method)
    empty_loc = np.where(result >= threshold)
    if empty_loc[0].shape[0] != 0:
        return 0

    search_template = cv2.imread(template_path + 'inventory_search.png')
    result = cv2.matchTemplate(search_template, search_region, method)
    loc = np.where(result >= threshold)
    h, w = search_template.shape[:2]

    order_template = cv2.imread(template_path + 'inventory_order.png')
    result = cv2.matchTemplate(order_template, search_region, method)
    loc2 = np.where(result >= threshold)
    h2, w2 = order_template.shape[:2]

    if screen == 'monitor':
        left, right, up, down = 12, -16, - 10, 20
    if screen == 'laptop':
        left, right, up, down = 18, -22, - 10, 20

    left_limit = loc2[1][0] + w2 + left
    right_limit = loc[1][0] + right
    upper_limit = loc[0][0] + up
    lower_limit = loc[0][0] + down

    cv2.line(search_region, (left_limit, 0), (left_limit, y1-y0), (255, 255, 255), thickness=1)
    cv2.line(search_region, (right_limit, 0), (right_limit, y1-y0), (255, 255, 255), thickness=1)
    cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

    search_region = search_region[upper_limit:lower_limit, left_limit:right_limit]
    hsv = cv2.cvtColor(search_region, cv2.COLOR_BGR2HSV)
    lower_val = np.array([20, 200, 80])
    upper_val = np.array([40, 255, 255])
    yellow = cv2.inRange(hsv, lower_val, upper_val)
    cv2.imwrite('Templates/3_color_threshold.png', yellow)

    yellow = yellow / 255
    y, x = np.where(yellow > 0)
    if x.size > 0:
        m3_amount = max(x)
        hold_size = right_limit - left_limit
        percent_full = round(m3_amount / hold_size * 100, 1)
        if query == 'percent full':
            return percent_full
    elif x.size == 0:
        return 0

    if query == 'position':
        x_center = new_x + loc2[1][0] + 30
        y_center = new_y + loc2[0][0] + 60
        return x_center/mod, y_center/mod
# hold_status = mining_hold('laptop', 'percent full')
# print(hold_status)
# if hold_status > 95:
#     print('hi')
# x, y = mining_hold('monitor', 'position')
# print(x, y)
# pyautogui.moveTo(x, y)


def transfer_box(screen, query=None):

    if screen == 'monitor':
        template_path = 'Templates/UI Elements/Monitor/'
        mod = 0.8333
        base = 2560  # monitor1 = [2560, 1600]  ///  monitor2 = [2560, 1440]
        x0 = base + 1500
        x1 = base + 2200
        y0 = 400
        y1 = 1200
    if screen == 'laptop':
        template_path = 'Templates/UI Elements/Laptop/'
        mod = 1
        x0 = 1500
        x1 = 2100
        y0 = 600
        y1 = 1400
    ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/1_Search_Region.png')
    search_region = cv2.imread('Templates/1_Search_Region.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .9

    if query == 'window location':
        transfer_window = cv2.imread(template_path + 'cargo_deposit_window.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(transfer_window, search_region, method)
        transfer_loc = np.where(result >= threshold)

        if transfer_loc[0].shape[0] == 0 and query != 'button location':
            return 'Deposit Closed'

        h, w = transfer_window.shape[:2]
        x_window = transfer_loc[1][0]
        y_window = transfer_loc[0][0]

        cancel_button = cv2.imread(template_path + 'cancel_button.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(cancel_button, search_region, method)
        cancel_loc = np.where(result >= threshold)
        hcancel, wcancel = cancel_button.shape[:2]

        x_cancel_button = cancel_loc[1][0]
        y_cancel_button = cancel_loc[0][0]

        # for pt in zip(*button_loc[::-1]):
        #     cv2.rectangle(search_region, pt, (pt[0] + wb, pt[1] + hb), (255, 0, 255), 2)
        # for pt in zip(*transfer_loc[::-1]):
        #     cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (255, 0, 255), 2)
        # cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

        x = x0 + x_window + 140*mod
        y = y0 + y_window + (y_cancel_button - y_window)/2

    if query == 'button location':
        transfer_button = cv2.imread(template_path + 'transfer_button.png', cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(transfer_button, search_region, method)
        button_loc = np.where(result >= threshold)
        hb, wb = transfer_button.shape[:2]

        x_button = button_loc[1][0]
        y_button = button_loc[0][0]

        x = x0 + x_button + wb/2
        y = y0 + y_button + hb/2
    return x/mod, y/mod
# x, y = transfer_box('laptop', 'window location')
# x, y = transfer_box('laptop', 'button location')
# print(x, y)
# pyautogui.moveTo(x, y)


def transfer_ore(screen, dropoff_location='fortizar'):

    if transfer_box(screen, 'window location') == 'Deposit Closed':
        x, y = find_bookmark(dropoff_location, screen)
        pyautogui.moveTo(x, y)
        time.sleep(.1 + random.gamma(3, .1))
        pyautogui.click(button='right')
        time.sleep(.7 + random.gamma(3, .2))

        x, y = find_in_context_menu(x, y, 'open_cargo_deposit', screen)
        x, y = randomize_click(x, y, 30, 8)
        pyautogui.moveTo(x, y)
        pyautogui.click()
        time.sleep(.1 + random.gamma(3, .1))

    status = mining_hold(screen, 'position')
    if status == 'Cargohold Closed':
        open_mining_hold(screen)
        status = mining_hold(screen, 'position')

    if status == 'Cargohold Empty' or status == 0:
        return

    x, y = randomize_click(status[0], status[1], 30, 30)
    pyautogui.moveTo(x, y)
    pyautogui.click()
    time.sleep(.1 + random.gamma(3, .1))

    pyautogui.keyDown('ctrl')
    time.sleep(.1 + random.gamma(3, .1))
    pyautogui.keyDown('a')
    time.sleep(.1 + random.gamma(3, .1))
    pyautogui.keyUp('a')
    time.sleep(.1 + random.gamma(3, .07))
    pyautogui.keyUp('ctrl')
    time.sleep(.1 + random.gamma(3, .1))

    x, y = transfer_box(screen, 'window location')
    x_transfer, y_transfer = randomize_click(x, y, 150, 150)
    pyautogui.mouseDown()
    time.sleep(.1 + random.gamma(3, .07))
    move_to(x_transfer, y_transfer)
    time.sleep(.1 + random.gamma(3, .07))
    pyautogui.mouseUp()
    time.sleep(.1 + random.gamma(3, .1))

    x, y = transfer_box(screen, 'button location')
    x_button, y_button = randomize_click(x, y, 60, 15)
    pyautogui.moveTo(x_button, y_button)
    pyautogui.click()
    time.sleep(.1 + random.gamma(3, .1))
# transfer_ore('laptop')

#
# screen = 'laptop'
# fort_grid = on_grid_with('fortizar', screen)
# print(fort_grid)
#
# if fort_grid == 'wrong overview tab':
#     change_tab('general_tab', screen)
#     time.sleep(0.3)
#
#     fort_grid = on_grid_with('fortizar', screen)
#     print(fort_grid)


def launch_drones(screen):
    if find_ui_element(screen, 'zero drones in space', 620, 825, 940, 1203, threshold=.99, silent=True) != 'not found':
        pyautogui.keyDown('shift')
        time.sleep(.1 + random.gamma(3, .05))
        pyautogui.keyDown('f')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('f')
        time.sleep(.1 + random.gamma(3, .03))
        pyautogui.keyUp('shift')
        time.sleep(.3 + random.gamma(3, .03))
        return 'launching'
    else:
        return 'already launched'
# print(launch_drones('laptop'))


def recall_drones(screen, onlylook=False):
    if find_ui_element(screen, 'zero drones in space', 620, 825, 940, 1203, threshold=.97, silent=True) == 'not found':
        if onlylook is False:
            pyautogui.keyDown('shift')
            time.sleep(.1 + random.gamma(3, .05))
            pyautogui.keyDown('r')
            time.sleep(.3 + random.gamma(3, .03))
            pyautogui.keyUp('r')
            time.sleep(.1 + random.gamma(3, .03))
            pyautogui.keyUp('shift')
            time.sleep(.3 + random.gamma(3, .03))
            return 'recalling'
    else:
        return 'already recalled'
# time.sleep(1)
# print(recall_drones('laptop', onlylook=True))


def activate_filament(screen):
    if screen == 'laptop':
        x, y = find_ui_element(screen, 'filament', 1931, 1040, 2559, 1596, button='right')
    if screen == 'monitor':
        x, y = find_ui_element(screen, 'filament', 1931, 1040, 2559, 1596, button='right')
    time.sleep(.3 + random.gamma(4, .1))

    x, y = find_in_context_menu(x, y, 'use_filament', screen)
    pyautogui.moveTo(x, y)
    time.sleep(.3 + random.gamma(4, .1))
    pyautogui.click()

    time.sleep(2 + random.gamma(4, .1))
    if screen == 'laptop':
        find_ui_element(screen, 'activate_for_fleet', 772, 262, 1967, 1402, button='left')
    if screen == 'monitor':
        find_ui_element(screen, 'activate_for_fleet', 772, 262, 1967, 1402, button='left')
    time.sleep(.3 + random.gamma(4, .1))
# activate_filament('laptop')


def detect_present_modules(screen):
    if screen == 'laptop':
        path = 'Templates/Modules/Laptop/'
        bbox = (891, 1377, 1321, 1569)
    if screen == 'monitor':
        path = 'Templates/Modules/Monitor/'
        bbox = (3200, 1285, 3488, 1417)

    ImageGrab.grab(bbox=bbox, all_screens=True).save('Templates/Modules/search_region.png')
    search_region = cv2.imread('Templates/Modules/search_region.png', cv2.IMREAD_GRAYSCALE)

    method = cv2.TM_CCOEFF_NORMED
    threshold = .95

    present_modules = []
    for module in os.listdir(path):
        name = module[:-4]
        mod = cv2.imread(path+module, cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(mod, search_region, method)
        loc = np.where(result >= threshold)

        duplicates = 0
        if loc[0].shape[0] != 0:
            if loc[0].shape[0] > 1:
                locations = [[loc[0][0], loc[1][0]]]

                true_loc = []
                for i, row in enumerate(loc[0]):
                    distances = []
                    for c, comp in enumerate(locations):
                        ydist = loc[0][i] - comp[0]
                        xdist = loc[1][i] - comp[1]
                        r = round(np.sqrt(ydist**2 + xdist**2))
                        distances.append(r)
                    if min(distances) > 5:
                        locations.append([loc[0][i], loc[1][i]])
                duplicates = len(locations)

                # h, w = mod.shape[:2]
                # for pt in zip(*loc[::-1]):
                #     cv2.rectangle(search_region, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                # cv2.imwrite('Templates/2_Matching_Attempt.png', search_region)

            if name == 'variegated' or name == 'coherent' or name == 'stripminer':
                name = 'miner'
            present_modules.append(name)
            if duplicates > 0:
                for i in range(0, duplicates-1):
                    present_modules.append(name)

    return present_modules
# print(detect_present_modules('laptop'))


def detect_current_ship(screen, present_modules=None):

    if present_modules is None:
        present_modules = detect_present_modules(screen)

    ship_list = dict([
        ('Prospects', ['cloak', 'gas_cloud_harvester', 'gas_cloud_harvester', 'MWD', 'ship_scanner', 'warp_core_stabilizer']),
        ('Covetors', ['afterburner', 'gas_cloud_harvester', 'gas_cloud_harvester', 'warp_core_stabilizer', 'webifier']),
        ('Retrievers', ['afterburner', 'ship_scanner', 'miner', 'miner']),
        ('Pacifier', ['cloak', 'combat_probes', 'MWD', 'nullifier']),
        ('Mastodon', ['cloak', 'invuln', 'invuln', 'kinetic_shield_hardener', 'MWD', 'nullifier', 'warp_core_stabilizer'])
    ])
    for key in ship_list:
        if set(ship_list[key]) == set(present_modules):
            return key
    return 'Unrecognized'
# print(detect_current_ship('laptop'))


def switch_pod(screen, pod):
    if screen == 'laptop':
        x0, y0, x1, y1 = 1156, 569, 2530, 1498

    character_window = find_ui_element(screen, 'character_window', 85, 138, 1477, 582)
    if character_window == 'not found':
        x, y = randomize_click2(4, 61, 50, 102)
        pyautogui.moveTo(x, y)
        print('Opening character sheet')
        time.sleep(.1 + random.gamma(2, .1))
        pyautogui.click()
        time.sleep(.5 + random.gamma(3, .2))
        character_window = find_ui_element(screen, 'character_window', 85, 138, 1477, 582)

    if character_window != 'not found':
        clone_tab = find_ui_element(screen, 'clone_tab_open', 383, 222, 1466, 1059)
        if clone_tab == 'not found':
            jump_clones_tab = find_ui_element(screen, 'jump_clones_tab', 86, 139, 1485, 1225, button='left')
            time.sleep(.5 + random.gamma(3, .2))
            clone_tab = find_ui_element(screen, 'clone_tab_open', 383, 222, 1466, 1059)

        if clone_tab != 'not found':
            pod_loc = find_ui_element(screen, pod, 86, 139, 1485, 1225)
            time.sleep(.5 + random.gamma(3, .2))
            if pod_loc != 'not found':
                print(f'Jumping into {pod} pod')
                jump = find_ui_element(screen, 'clone_jump', pod_loc[0]-10, pod_loc[1]-10, pod_loc[0] + 400, pod_loc[1] + 40, button='left')
            else:
                print(f'Already in {pod} pod')

        time.sleep(5 + random.gamma(3, .2))
        close_window = find_ui_element(screen, 'close_window', character_window[0]+500, character_window[1]-15,
                                       character_window[0]+1000, character_window[1]+30, button='left')

# switch_pod('laptop', 'Virtues')


def switch_ship(screen, ship):
    # screen = find_screens([character])[0]
    # set_active_toon('DangLang')
    if screen == 'laptop':
        x0, y0, x1, y1 = 1156, 569, 2530, 1498
    inventory_window = find_ui_element(screen, 'inventory_window', x0, y0, x1, y1)

    if inventory_window == 'not found':
        print('Opening Inventory')
        open_inventory = find_ui_element(screen, 'open_inventory', 0, 464, 101, 1122, button='left')
        time.sleep(1 + random.gamma(4, .1))
        inventory_window = find_ui_element(screen, 'inventory_window', x0, y0, x1, y1)

    if inventory_window != 'not found':
        pacifier = find_ui_element(screen, ship, x0, y0, x1, y1, button='double')
        if pacifier != 'not found':
            print('Selecting Pacifier')
            time.sleep(.2 + random.gamma(3, .1))
            interval = np.random.normal(0.12, 0.006, 1)[0]
            pyautogui.click(clicks=2, interval=float(interval))
        else:
            print('Switching inventory to Ship Hangar tab')
            ship_hangar = find_ui_element(screen, 'ship_hangar', x0, y0, x1, y1, button='left')
            time.sleep(.5 + random.gamma(4, .1))
            if ship_hangar != 'not found':
                pacifier = find_ui_element(screen, ship, x0, y0, x1, y1, button='double')
                if pacifier != 'not found':
                    print('Selecting Pacifier')
                    # time.sleep(.2 + random.gamma(3, .1))
                    # interval = np.random.normal(0.12, 0.006, 1)[0]
                    # pyautogui.click(clicks=2, interval=float(interval))
    else:
        print('Inventory not found')
# switch_ship('laptop', 'pacifier')





if __name__ == '__main__':
    print('\n\n', round(time.time()-start_time, 5), 'sec')