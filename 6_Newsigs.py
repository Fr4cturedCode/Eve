from a1_functions import *
import threading
from pynput import keyboard

screen = 'laptop'

print('\n-----------------------------------------')
print('          Watching for new sigs')
print('-----------------------------------------')

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
    stop = False
    while 1 != 0:
        stop_check(stop)
        if new_sigs(screen) is True:
            threading.Thread(target=alarm_sound(), daemon=True).start()
            print(f'\n       NEW SIG after {round((time.time() - start_time) / 60, 1)} minutes\n')
            time.sleep(.5)