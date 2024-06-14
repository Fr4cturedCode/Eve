import time
import pyautogui
from a1_functions import *
import pygetwindow as gw
from numpy import random
from pynput import keyboard
import threading

toons = ['DangLang']
# toons = ['Fr4ctured Mind']
# toons = ['Zoe Washborn']
dual_screen = False

Dscan = True
# Dscan = False

# sound = True
sound = False

screens = find_screens(toons)
main_toon, main_screen = toons[0], screens[0]
if main_screen == 'laptop':
    alt_screen = 'monitor'
if main_screen == 'monitor':
    alt_screen = 'laptop'

def on_press(key):
    global stop
    # global start
    if key == keyboard.Key.ctrl_r:
        print('\nStopping', end='')
        stop = True
        return

def stop_check(stop):
    if stop == True:
        print('\rStopped by user')
        quit()

with keyboard.Listener(on_press=on_press) as listener:
    if __name__ == '__main__':
        stop = False
        start_time = time.time()

        print('\n-----------------------------------------')
        print('             LP / OP deployed')
        print('-----------------------------------------')
        time.sleep(0.5)
        while gw.getActiveWindow() is not None and gw.getActiveWindow().title != 'EVE - ' + main_toon:
            print(f"\rClick on {main_toon}'s client.", end='')
            time.sleep(0.5)
        print('\rWatching...')

        ####### Main Loop ########
        while 1 != 0:
            stop_check(stop)

            ######    Check grid for Players and NPCs   ######
            overview_status = watch_overview(main_screen, mode='Observe')
            if overview_status == 'Overview blocked':
                print('\rOverview not detected', end='')
            if overview_status == 'Player on grid':
                if sound is True:
                    threading.Thread(target=alarm_sound(), daemon=True).start()
                print(f'\n    {overview_status} after {round((time.time() - start_time) / 60, 1)} minutes\n')

            ######    D-Scanning    ######
            if 'dscan_interval' not in locals() or time.time() >= last_dscan_time + dscan_interval:
                stop_check(stop)
                if gw.getActiveWindow() is not None and gw.getActiveWindow().title == 'EVE - ' + main_toon:  # scans only on main toon
                    pyautogui.keyDown('`')
                    time.sleep(.1 + random.gamma(3, .03))
                    pyautogui.keyUp('`')
                    time.sleep(.5)
                    last_dscan_time = time.time()

                    ######    Check grid for Players and NPCs   ######
                    overview_status = watch_overview(main_screen, mode='Observe')
                    if overview_status == 'Overview blocked':
                        print('\rOverview not detected', end='')
                    if overview_status == 'Player on grid':
                        if sound is True:
                            threading.Thread(target=alarm_sound(), daemon=True).start()
                        print(f'\n    Player on grid after {round((time.time() - start_time) / 60, 1)} minutes\n')
                    time.sleep(.5)

                    ######   Read D-Scan results    ######
                    dscan_results = watch_dscan(main_screen, mode='Observe')
                    time.sleep(.5)
                    if dscan_results == 'new object':
                        if sound is True:
                            threading.Thread(target=alarm_sound(), daemon=True).start()
                        print(
                            f'\n     Unknown object on Dscan after \n               {round((time.time() - start_time) / 60, 1)} minutes\n')
                    dscan_interval = random.gamma(1.5, 1.5) + .5

            ######   Check for new sigs   ######
            if new_sigs(main_screen, mode='Observe') is True:
                if sound is True:
                    threading.Thread(target=alarm_sound(), daemon=True).start()
                print(f'\n       NEW SIG after {round((time.time() - start_time) / 60, 1)} minutes\n')
                time.sleep(.5)

            if dual_screen is True:
                if new_sigs(alt_screen, mode='Observe') is True:
                    if sound is True:
                        threading.Thread(target=alarm_sound(), daemon=True).start()
                    print(f'\n       NEW SIG after {round((time.time() - start_time) / 60, 1)} minutes\n')
                    time.sleep(5)
