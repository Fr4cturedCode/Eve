import pyautogui
from pynput import mouse, keyboard
from pynput.mouse import Controller
from PIL import ImageGrab
import time
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
# from a1_functions import *


def bboxtool(filename = 'None'):
    global pressed
    pressed = False
    mouse = Controller()

    def on_press(key):
        global start, pressed
        if not pressed and key == keyboard.Key.alt_l:
            start = mouse.position
            pressed = True

        if key == keyboard.Key.esc:
            return False
        if not key:
            return False

    def on_release(key):
        global stop
        if key == keyboard.Key.alt_l:
            stop = mouse.position
            return False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    mod = 1
    if start[0] > 2560 or stop[0] > 2560:
        mod = 0.8333333                      # adapts for different monitor size
    x0 = round(mod * min(start[0], stop[0]))
    y0 = round(mod * min(start[1], stop[1]))
    x1 = round(mod * max(start[0], stop[0]))
    y1 = round(mod * max(start[1], stop[1]))

    # print(x0, y0, "-->", x1, y1, f'\nCenter: x = {round(x0 + (x1-x0)/2)}, y = {round(y0+ (y1-y0)/2)}\n')
    # print(x0 - 2560, y0, "-->", x1-2560, y1, f' \nCenter: x = {round(x0+ (x1-x0)/2 -2560)}, y = {round(y0 +(y1-y0)/2)}')
    # print(f'\n w = {x1-x0}   h = {y1-y0}')
    print(' x0   y0   x1   y1')
    print(f'{x0}, {y0}, {x1}, {y1}')


    # filename = input("Enter Filename: ") +".png"
    # filename = "test_template.png"
    # ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True).save('Templates/' + filename)
    # return filename
    return
bboxtool()

def determine_key_names():
    global start
    global stop
    # global let_go
    # let_go = True

    def on_press(key):
        global start
        # global let_go

        try:
            # if let_go is True:
            #     start = time.time()
            print('alphanumeric key {0} pressed'.format(key.char))
                # let_go = False
        except AttributeError:
            pass
            # print('special key {0} pressed'.format(key))

    def on_release(key):
        # global let_go
        print('{0} released'.format(key))
        # let_go = True
        # try:
            # print(time.time()-start)
        # except:
        #     pass
        if key == keyboard.Key.esc:
            return False  # Stop listener

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
# determine_key_names()

def mousecapture():
    def on_click(x, y, button, pressed):
        global click,release
        if pressed:
            click = time.time()
            try:
                print(click-release, 'between clicks')
            except:
                pass
        if not pressed:
            release = time.time()
            print(release-click, 'between click and release')
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
# mousecapture()

def histogram():
    # ##### to set an upper limit
    # a = []
    # for i in range(0, 5000):
    #     value = .05 + random.gamma(1.5, .07)
    #     while value > 0.4:
    #         value = .1 + random.gamma(1.5, .07)
    #     a.append(value)

    # a = 5 + random.gamma(8, .08, 1000)     # 1.5s avg, max 4s
    # time.sleep(10 + random.gamma(5, .1))
    # a = 10 + random.gamma(5, .1, 1000)
    #dscan mashing speed

    min = 1
    shape, scale = 1.5, 1.5
    a = min + random.gamma(shape, scale, 1000)

    plt.axvline(x=np.mean(a), color='r')
    plt.hist(a, bins=50)
    plt.show()
# histogram()

def evemonskills():
    skills_list = open('pyfaconfessorlist.txt', 'r').readlines()
    for row in skills_list:
        if row[-2] != '0':
            print(f'{row}', end='')
# evemonskills()

def screenshots(time):
    i = 1
    while i < time:
        ImageGrab.grab(bbox=(0, 0, 2560, 1600), all_screens=True).save(f'Templates/Downtime/downtime{i}.png')
        time.sleep(1)
        i += 1
    quit()