from a2_market_functions import *
import pyperclip


if __name__ == '__main__':

    what = input("buy or sell? 's' / 'b'\n")
    if what == 'b':
        action = 'buy'
    if what == 's':
        action = 'sell'
    print(f'--- Ready to {action} ---')

    try:
        old_file = max(glob.iglob(r'C:\Users\Matt\Documents\EVE\logs\Marketlogs\*.txt'), key=os.path.getctime)
    except:
        old_file = None

    while 1 != 0:
        try:
            newest_file = max(glob.iglob(r'C:\Users\Matt\Documents\EVE\logs\Marketlogs\*.txt'), key=os.path.getctime)
        except:
            newest_file = None

        if newest_file != old_file:
            new_price = item_analyser(action=action, display=True)
            pyperclip.copy(f'{new_price:.2f}')

        old_file = newest_file
        time.sleep(.5)
