from a1_functions import *
from datetime import datetime
from datetime import timedelta


# toons = ['Cave Dweller']
toons = ['Zoe Washborn']
# toons = ['Astina Leanni']
# toons = ['Fr4ctured Mind']

screens = find_screens(toons)
screen = screens[0]

cloak = True
# cloak = False

# testmode = True
testmode = False

### determine downtime ###
today = datetime.now()
downtime = datetime(today.year, today.month, today.day, 4, 0, 0)

if testmode is True:
    print('\nTEST MODE, WILL NOT ENTER ABYSSAL\n')
    downtime = datetime.now() + timedelta(minutes=1.6)   ###### TEST BLOCK, DELETE LATER

difference = (downtime - datetime.now())
seconds = difference.total_seconds()
if seconds < 0:
    downtime += timedelta(days=1)
    difference = (downtime - datetime.now())
    seconds = difference.total_seconds()
while seconds > 100:  # sleeps until downtime based on the clock
    difference = (downtime - datetime.now())
    print(f'\rTime until server restart: {difference}', end='')
    seconds = difference.total_seconds()
    time.sleep(1)

###  begin entry ###
print(f'\rAbyssal Process Active:\n')
set_active_toon(toons[0])
time.sleep(.5 + random.gamma(4, .1))
stop_ship()
time.sleep(1 + random.gamma(4, .1))

# if testmode is False:
#     while 1 != 0: # waits until cluster shutdown message is shown
#         if find_UI_element(screen, 'cluster shutdown', 809, 0, 1751, 803) is True:
#             # set_active_toon('Aetarin Thiesant')
#             # time.sleep(.2)
#             # ImageGrab.grab(bbox=(3228, 0, 4542, 808), all_screens=True).save(f'Templates/Downtime/downtimeMonitor.png')
#             time.sleep(.2)
#             break
#         set_active_toon(toons[0])
#         time.sleep(1)
#     time.sleep(50)

### uncloack ###
if cloak is True:
    print('\rUncloaking', end='')
    toggle_module('cloak')
    time.sleep(2 + random.gamma(4, .1))

### activate filament ###
if find_on_overview('abyssal trace', screen) == 'not found':
    print('\rActivating Filament', end='')
    activate_filament(screen)
    time.sleep(5 + random.gamma(4, .1))

### select abyssal, approach, press jump ###
print('\rBeginning Entry Process', end='')
trace = find_on_overview('abyssal trace', screen, click=True)
if trace == 'not found':
    print('Abyssal Trace not seen on overview. Quitting')
    quit()
time.sleep(1 + random.gamma(4, .1))

# selected_item(screen, action='approach')
# time.sleep(5 + random.gamma(4, .1))

selected_item(screen, action='warp/dock')
time.sleep(2 + random.gamma(4, .1))

if testmode is True:
    quit()

### enter abyssal ###
print('\rEntering Abyssal', end='')
if screen == 'laptop':
    click_UI_element(screen, 'activate', 772, 262, 1967, 1402)
if screen == 'monitor':
    click_UI_element(screen, 'activate', 772, 262, 1967, 1402)
time.sleep(1 + random.gamma(3, .03))

### wait out invuln  ###
print('\rWaiting out invuln', end='')
time.sleep(55 + random.gamma(4, .1))

### orbit conduit ###
find_on_overview('abyssal trace', screen, click=True)
time.sleep(1 + random.gamma(4, .1))
print('\rOrbiting Conduit', end='')
selected_item(screen, action='orbit')
time.sleep(1 + random.gamma(3, .03))

### activate modules ###
print('\rActivating Mods', end='')
# toggle_module('low1')
# time.sleep(.1 + random.gamma(3, .03))
# toggle_module('low2')
# time.sleep(1 + random.gamma(3, .03))
toggle_module('MWD')
time.sleep(1 + random.gamma(3, .03))






