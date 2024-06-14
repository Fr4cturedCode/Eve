import time
import pyautogui
from a1_functions import *
import pygetwindow as gw
from numpy import random
from pynput import keyboard
import threading
import csv
import os
from datetime import datetime

npc_reaction = 'Evade'
# npc_reaction = 'Ignore'

dropoff_location = 'InstaDock'
dock = True
automate_Dscan = True  # True automates d-scanning, False if in a closed wormhole

toons = ['Fr4ctured Mind', 'Zoe Washborn', 'GigaSpaceChad', 'DangLang']
# toons = ['Zoe Washborn']
scanner = 'DangLang'

bookmarks_file = 'bookmarks.csv'
os.system('notepad.exe ' + bookmarks_file)


def on_press(key):
    global stop
    global pause
    # global start
    if key == keyboard.Key.ctrl_r:
        print('\nStopping', end='')
        stop = True
        return
    if key == keyboard.Key.alt_gr:
        if pause is False:
            print('\r Pausing...', end='')
            pause = True
            return
        if pause is True:
            print('\r Unpaused', end='')
            pause = False
            return


def stop_check(stop):
    if stop is True:
        print('\rStopped by user')
        quit()
    while pause is True:
        print('\r Paused', end='')
        time.sleep(.2)


def lock_up_resources(harvest_range, drones='Deploy'):
    # print('\rSelecting resource', end='')
    ranges = []
    for i in range(0, len(toons)):
        stop_check(stop)
        set_active_toon(toons[i], screens[i])

        time.sleep(.1 + random.gamma(5, .04))
        change_tab('pve_tab', screens[i])
        time.sleep(.1 + random.gamma(5, .04))

        if target_locked(screens[i]) == 'no target':
            # ---- if modules are currently active, turn them off
            stop_check(stop)
            print(f'\r {toons[i]} Selecting target', end='')
            active_mods = active_modules(screens[i])
            if active_mods[0][0] == 1:
                pyautogui.keyDown('f1')
                time.sleep(.2 + random.gamma(2, .01))
            if active_mods[0][1] == 1:
                pyautogui.keyDown('f2')
                time.sleep(.2 + random.gamma(2, .02))
            if active_mods[0][0] == 1:
                pyautogui.keyUp('f1')
                time.sleep(.2 + random.gamma(2, .01))
            if active_mods[0][1] == 1:
                pyautogui.keyUp('f2')
                time.sleep(.2 + random.gamma(2, .02))

            # ---- find resource on overview, then click ----
            stop_check(stop)
            if action == 'Huffing':
                res_loc = find_on_overview(resource, screens[i], click=True)
                x, y = res_loc[0], res_loc[1]
                if res_loc == 'not found':
                    return 100001
            if action == 'Mining':
                distance = select_mineral(screens[i], maxrange=harvest_range)
                ranges.append(distance)
                if distance > harvest_range:
                    return distance

            # ------ locks up selected overview item ------
            stop_check(stop)
            pyautogui.keyDown('ctrl')
            time.sleep(.3 + random.gamma(5, .02))
            pyautogui.keyUp('ctrl')
            time.sleep(.5 + random.gamma(5, .02))

            # ---- launch drones ----
            if action == 'Mining' and drones == 'Deploy':
                stop_check(stop)
                drone_status = launch_drones(screens[i])
                if drone_status == 'launching':
                    print(f'\r {toons[i]}  launching drones', end='')
                    time.sleep(2 + random.gamma(5, .02))

            # ----- activate modules-------
            stop_check(stop)
            print(f'\r {toons[i]} Activating modules', end='')
            pyautogui.keyDown('f1')
            time.sleep(.2 + random.gamma(2, .01))
            pyautogui.keyDown('f2')
            time.sleep(.3 + random.gamma(5, .02))
            pyautogui.keyUp('f1')
            time.sleep(.2 + random.gamma(2, .01))
            pyautogui.keyUp('f2')
            time.sleep(.5 + random.gamma(5, .02))

            # ------- activate drones ----------
            if action == 'Mining' and drones == 'Deploy':
                print(f'\r {toons[i]} Sending drones', end='')
                stop_check(stop)
                pyautogui.keyDown('f')
                time.sleep(.2 + random.gamma(3, .02))
                pyautogui.keyUp('f')
                time.sleep(.3 + random.gamma(5, .02))

        else:
            # -------- activate modules if target already selected ----
            active_mods = active_modules(screens[i])
            stop_check(stop)
            if active_mods[0][0] == 0:
                print(f'\r {toons[i]} Toggling f1', end='')
                pyautogui.keyDown('f1')
                time.sleep(.2 + random.gamma(2, .01))
            if active_mods[0][1] == 0:
                print(f'\r {toons[i]} Toggling f2', end='')
                pyautogui.keyDown('f2')
                time.sleep(.2 + random.gamma(2, .03))
            if active_mods[0][0] == 0:
                pyautogui.keyUp('f1')
                time.sleep(.2 + random.gamma(2, .02))
            if active_mods[0][1] == 0:
                pyautogui.keyUp('f2')
                time.sleep(.2 + random.gamma(5, .02))

            # ---------- drones ----------
            if action == 'Mining' and drones == 'Deploy':
                stop_check(stop)
                if find_ui_element((screens[i]), 'drones_on_target', 1641, 150, 1937, 246, silent=True) == 'not found':
                    drone_status = launch_drones(screens[i])
                    if drone_status == 'launching':
                        print(f'\r {toons[i]} Launching drones', end='')
                        time.sleep(2 + random.gamma(5, .02))
                    print(f'\r {toons[i]} Sending drones', end='')
                    pyautogui.keyDown('f')
                    time.sleep(.2 + random.gamma(3, .02))
                    pyautogui.keyUp('f')
                    time.sleep(.3 + random.gamma(5, .02))

    time.sleep(.5 + random.gamma(5, .02))
    set_active_toon(main_toon, main_screen)
    if len(ranges) > 0:
        return max(ranges)
    else:
        return 0


with keyboard.Listener(on_press=on_press) as listener:

    start_time = time.time()
    stop = False
    # global pause
    pause = False
    cycle = 1
    old_m3 = 0
    full = False
    current_location = 'unknown'
    drones = 'Deploy'
    recalled = False
    continue_scanning = False

    # -----------------------------------------------------------------------------
    # -------------------------------- initial setup  -----------------------------
    # -----------------------------------------------------------------------------

    # ---- determine downtime ----
    now = datetime.now()
    settle = datetime(now.year, now.month, now.day, 3, 40, 0)
    logoff = datetime(now.year, now.month, now.day, 3, 50, 0)
    downtime = datetime(now.year, now.month, now.day, 4, 0, 0)

    # ---- generate bookmarks from file ------
    with open(bookmarks_file, 'r') as file:
        reader = csv.reader(file)
        count = sum(1 for row in reader)
    if count > 0:
        with open('bookmarks.csv', 'r') as file:
            reader = csv.reader(file)
            resource_bookmarks = next(csv.reader(file))
            return_to_site = True
    else:
        resource_bookmarks = []
        return_to_site = False

    # ---- finds characters associated screens -----
    screens = find_screens(toons)
    main_toon, main_screen = toons[0], screens[0]
    if len(toons) == 1:
        who = 'Self'
    else:
        who = 'Squad'

    # --------- wait until correct client is selected -----------
    while gw.getActiveWindow() is not None and gw.getActiveWindow().title != 'EVE - ' + main_toon:
        print(f"\rClick on {main_toon}'s client.", end='')
        time.sleep(0.5)

    # ---------- determine ship, assign values ----------
    ships = detect_current_ship(main_screen)
    if ships == 'Prospects':
        hold_size = 12500
        fill_time = 78
        safe_spot = 'Safe'
        action = 'Huffing'
        resource = 'gas cloud'
        harvest_range = 1500
    elif ships == 'Covetors':
        hold_size = 9000
        fill_time = 37
        safe_spot = 'InstaDock'
        action = 'Huffing'
        resource = 'gas cloud'
        harvest_range = 1500
    elif ships == 'Retrievers':
        hold_size = 33000
        fill_time = 19.7
        safe_spot = 'InstaDock'
        action = 'Mining'
        resource = 'asteroid'
        harvest_range = 13000
    else:
        print('\r \n No harvesting capable ship detected.')
        quit()

    # ------ check current location of fleet -------
    fort_check = find_bookmark('InstaDock', main_screen)
    if fort_check != 'no bookmark found':
        system = 'Home System'
        deposit = True
    else:
        system = 'Downchain'
        deposit = False
        safe_check = find_bookmark('Safe', main_screen)
        if safe_check == 'no bookmark found':
            print('Safe bookmark not found')
            quit()

    # --------------- display------------------
    print('\r \n-----------------------------------------')
    print(f' {action} with {ships}  // {npc_reaction} NPCs')
    print(f' Location: {system}  // D-Scaning: {automate_Dscan}')
    print(f' Emergency warping "{who}" to: {safe_spot}')
    if not resource_bookmarks:
        print('    No bookmark list')
    else:
        print(f'    Resource bookmarks :\n    {resource_bookmarks}')
    print('-----------------------------------------')
    print('\r Watching...')

    # --- determine if on grid with fort ----
    if on_grid_with('fortizar', main_screen) == 'on grid':
        current_location = 'fort grid'

    # ---- lock up resources if possible -----
    if current_location != 'fort grid':
        if gw.getActiveWindow() is not None and gw.getActiveWindow().title == 'EVE - ' + main_toon:
            if target_locked(main_screen) == 'no target':
                distance = lock_up_resources(harvest_range, drones=drones)
                if distance == 100001: # no asteroids on overview
                    change_tab('general_tab', main_screen)
                    if on_grid_with('fortizar', main_screen) == 'on grid':
                        current_location = 'fort grid'
                    # print('\r \n No rocks on grid. Failed to initiate')
                    # quit()
                if distance > harvest_range:
                    full = True
                last_mining_check = time.time()
                mining_check_interval = 30 + random.gamma(20, 1)

        # set warp formation #
        if who == 'Squad' and ships == 'Prospects':
            time.sleep(.5 + random.gamma(3, .03))
            if safe_spot == 'Safe':
                set_fleet_formation('sphere', main_screen)
            if safe_spot == 'InstaDock':
                set_fleet_formation('point', main_screen)
            time.sleep(0.5)
        reset_mouse(main_screen)

    # -----------------------------------------------------------------------
    # ------------------------------ Main Loop  -----------------------------
    # -----------------------------------------------------------------------

    iterations = 0
    while 1 != 0:
        stop_check(stop)

        if settle < datetime.now() < downtime:
            return_to_site = False
            if logoff < datetime.now() < downtime:
                full = False

        # -------- Check grid for Players and NPCs  --------
        overview_status = watch_overview(main_screen, npc_reaction)
        if overview_status == 'Overview blocked':
            print('\rOverview not detected', end='')
        if overview_status == 'NPCs on grid':
            print(f'\n    NPCs on grid after {round((time.time() - start_time) / 60, 1)} minutes\n')
            break
        if overview_status == 'Player on grid':
            continue_scanning = True
            threading.Thread(target=alarm_sound, args=['klaxon']).start()
            threading.Thread(target=video_capture, args=('Alerts/Player on grid', main_screen, .5, 30)).start()
            print(f'\n    Player on grid after {round((time.time() - start_time) / 60, 1)} minutes\n')
            break

        # --------  D-Scanning --------
        if 'dscan_interval' not in locals() or automate_Dscan is True and time.time() >= last_dscan_time+dscan_interval:
            stop_check(stop)
            if gw.getActiveWindow() is not None and gw.getActiveWindow().title == 'EVE - ' + main_toon:
                pyautogui.keyDown('`')
                time.sleep(.1 + random.gamma(3, .03))
                pyautogui.keyUp('`')
                time.sleep(.5)
                last_dscan_time = time.time()

                # -------- Check grid for Players and NPCs --------
                overview_status = watch_overview(main_screen, npc_reaction)
                if overview_status == 'Overview blocked':
                    print('\rOverview not detected', end='')
                if overview_status == 'NPCs on grid':
                    print(f'\n    NPCs on grid after {round((time.time() - start_time) / 60, 1)} minutes\n')
                    break
                if overview_status == 'Player on grid':
                    continue_scanning = True
                    threading.Thread(target=alarm_sound, args=['klaxon']).start()
                    threading.Thread(target=video_capture, args=('Alerts/Player on grid', main_screen, .5, 30)).start()
                    print(f'\n    Player on grid after {round((time.time() - start_time) / 60, 1)} minutes\n')
                    break
                time.sleep(.5)

                # --------  Read D-Scan results  --------
                dscan_results = watch_dscan(main_screen)
                time.sleep(.5)
                if dscan_results == 'new object':
                    threading.Thread(target=alarm_sound, args=['alarm']).start()
                    threading.Thread(target=video_capture, args=('Alerts/Dscan_object', main_screen, .5, 30)).start()
                    continue_scanning = True
                    print(f'\n     Unknown object on Dscan after \n               '
                          f'{round((time.time()-start_time)/60,1)} minutes\n')
                    break
                dscan_interval = random.gamma(1.5, 1.5) + .5

        # --------  Check for new sigs  ----------
        if new_sigs(main_screen) is True:
            threading.Thread(target=alarm_sound, args=['sonar']).start()
            threading.Thread(target=video_capture, args=('Alerts/New_sig', main_screen, .5, 30)).start()
            continue_scanning = True
            print(f'\n       NEW SIG after {round((time.time()-start_time)/60,1)} minutes\n')
            time.sleep(5)
            break

        # ----------------------------------------------------------------------------------------
        # -------------------------- Monitor mining ----------------------------------------------
        # ----------------------------------------------------------------------------------------

        stop_check(stop)
        if gw.getActiveWindow() is not None and gw.getActiveWindow().title == 'EVE - ' + main_toon:

            # -----  activate miners/scoops/drones ----
            if iterations > 0 and current_location != 'fort grid':

                # ------ Mining Checks --------
                if action == 'Mining':
                    # if sufficient time has passed, or nothing currently selected
                    if 'last_mining_check' not in locals() or time.time() >= last_mining_check + mining_check_interval \
                            or selected_item(main_screen) == 'no object selected':
                        distance = lock_up_resources(harvest_range, drones=drones)
                        if distance > harvest_range:
                            full = True
                        last_mining_check = time.time()
                        mining_check_interval = 30 + random.gamma(20, 1)

                # ----- Huffing Checks ------
                if action == 'Huffing':
                    if selected_item(main_screen) == 'no object selected':
                        time.sleep(random.gamma(5, .5))
                        print('\nResource has been consumed')
                        full = True
                        return_to_site = False

                # ------ activate survery scanning on interval -------
                if 'last_survey' not in locals() or time.time() >= last_survey + survey_interval:
                    toggle_module('high3')
                    time.sleep(5 + random.gamma(1.5, 1.5))
                    if gw.getActiveWindow() is not None and gw.getActiveWindow().title == 'EVE - ' + main_toon:
                        reset_mouse(main_screen)
                    last_survey = time.time()
                    survey_interval = 120 + random.gamma(50, 1)

            # ---- detect hold percentage ------
            hold_status = mining_hold(main_screen, 'percent full')

            # -- opens cargohold if closed --
            if hold_status == 'Cargohold Closed':
                print(f'\rHold closed or obscured', end='')
                if gw.getActiveWindow() is not None and gw.getActiveWindow().title == 'EVE - ' + main_toon:
                    open_mining_hold(screens[0])
                    time.sleep(1)
                    hold_status = mining_hold(main_screen, 'percent full')  # check again

            # --- determine cargohold volume ---
            if hold_status != 'Cargohold Closed':      # if cargohold open
                new_m3 = round(hold_size * hold_status/100)
                time_remaining = round(fill_time * (1-hold_status/100))
                if new_m3 != old_m3:
                    print(f'\r Cargo {hold_status}% full  ({new_m3} m^3)   -{time_remaining} min', end='')
                stop_check(stop)
                old_m3 = new_m3

                # ---- deposit on first iteration (only if general tab selected)
                # if iterations == 0 and hold_status > 5 and current_location == 'fort grid':
                if iterations == 0 and current_location == 'fort grid':
                    full = True
                    deposit = True
                    if hold_status > 5:
                        return_to_site = False  # only deposits. wont leave fort grid

                # ------ control drone deployment ------
                if hold_status <= 90:
                    drones = 'Deploy'
                elif hold_status > 90:
                    drones = 'Recall'                           # ----- recall drones -----
                    if action == 'Mining' and current_location != 'fort grid' and recalled is False:
                        print('\r Cargo nearly full. Recalling Drones', end='')
                        for i in range(0, len(toons)):
                            stop_check(stop)
                            set_active_toon(toons[i], screens[i])
                            recall_drones(screens[i])
                            time.sleep(.1 + random.gamma(3, .1))
                        set_active_toon(main_toon, main_screen)
                        recalled = True

                # ------ return to base signal -----
                if hold_status > 98:
                    print('\n Cargo full', end='')
                    full = True

            # ====================================================================================
            # ======================== RETURN HOME AND DEPOSIT RESOURCES =========================
            # ====================================================================================

            if full is True:

                # --- check status of old bookmark ---
                if current_location != 'fort grid' and distance >= harvest_range:
                    print(f'\r {resource_bookmarks[0]} bookmark depleted\n')
                    with open('bookmarks.csv', 'w', newline='\n') as file:
                        csv.writer(file).writerow(resource_bookmarks[1:])
                    resource_bookmarks = resource_bookmarks[1:]

                # ---- prevents return if bookmarks not available ----
                if not resource_bookmarks:
                    return_to_site = False  # change when CSV bookmark list created

                # ----- recall drones -----
                if action == 'Mining' and current_location != 'fort grid':
                    for i in range(0, len(toons)):
                        stop_check(stop)
                        set_active_toon(toons[i], screens[i])
                        recall_drones(screens[i])
                        time.sleep(.1 + random.gamma(3, .1))
                    set_active_toon(main_toon, main_screen)
                    while recall_drones(main_screen, onlylook=True) != 'already recalled':
                        time.sleep(.5)
                    time.sleep(4 + random.gamma(3, .1))

                # ------ deposit resources into structure --------
                if deposit is False:
                    break
                if deposit is True:

                    if current_location != 'fort grid':
                        if who == 'Squad' and ships == 'Prospects':
                            set_fleet_formation('point', main_screen)

                        stop_check(stop)
                        response = warp_to_bookmark(who, dropoff_location, main_screen)
                        if response == 'not found':
                            time.sleep(1 + random.gamma(3, .1))
                            reset_mouse(main_screen)
                            time.sleep(1 + random.gamma(3, .1))
                            response = warp_to_bookmark(who, dropoff_location, main_screen)
                            if response == 'not found':
                                print(f" Can't initiate warp to {dropoff_location}. Quitting")
                                quit()

                        while is_warping(screens[0]) is False:  # waiting until warp is recognized
                            time.sleep(.5)

                        # --- once warp initiated, turn off any active miners/huffers
                        for i in range(1, len(toons)):
                            stop_check(stop)
                            set_active_toon(toons[i], screens[i])
                            active_mods = active_modules(screens[i])
                            if active_mods[0][0] == 1:
                                pyautogui.keyDown('f1')
                                time.sleep(.1 + random.gamma(2, .02))
                            if active_mods[0][1] == 1:
                                pyautogui.keyDown('f2')
                                time.sleep(.2 + random.gamma(5, .02))
                            if active_mods[0][0] == 1:
                                pyautogui.keyUp('f1')
                                time.sleep(.1 + random.gamma(2, .02))
                            if active_mods[0][1] == 1:
                                pyautogui.keyUp('f2')
                                time.sleep(.2 + random.gamma(5, .02))
                        set_active_toon(main_toon, main_screen)

                        while is_warping(screens[0]) is True:       # loop for duration of warp
                            time.sleep(.5)
                        current_location = 'fort grid'
                        time.sleep(.1 + random.gamma(3, .15))

                    # ---- dock up -----
                    if dock is True and return_to_site is False and iterations > 0:
                        print(f'\r \n Docking up after {cycle} {action} cycles')
                        for i in range(0, len(toons)):
                            stop_check(stop)
                            set_active_toon(toons[i], screens[i])
                            time.sleep(.3 + random.gamma(3, .15))
                            dock_up(screens[i])
                        time.sleep(20 + random.gamma(5, 2))
                        set_active_toon(scanner, screens[toons.index(scanner)])
                        switch_pod('laptop', 'Virtues')
                        time.sleep(20 + random.gamma(5, 2))
                        switch_ship('laptop', 'Pacifier')
                        quit()

                    # --------  Transfer Ore to structure   --------
                    if hold_status > 5:
                        for i in range(0, len(toons)):
                            stop_check(stop)
                            set_active_toon(toons[i], screens[i])
                            transfer_ore(screens[i])
                            time.sleep(.1 + random.gamma(3, .1))
                        set_active_toon(main_toon, main_screen)
                        time.sleep(.3 + random.gamma(3, .15))
                        if ships == 'Prospects':
                            set_fleet_formation('point', main_screen)
                        change_tab('pve_tab', main_screen)
                        if iterations > 0:
                            print(f'\r  {cycle} {action} cycle completed\n')
                            cycle += 1

                    if return_to_site is False:
                        quit()

                    elif return_to_site is True:

                        # -------- Check for new sigs  --------
                        if new_sigs(main_screen) is True:
                            threading.Thread(target=alarm_sound, args=['sonar']).start()
                            threading.Thread(target=video_capture, args=('Alerts/New_sig', main_screen, .5, 30)).start()
                            continue_scanning = True
                            print(f'\n       NEW SIG after {round((time.time() - start_time) / 60, 1)} minutes\n')
                            time.sleep(5)
                            break

                        # --------  Return to site  --------
                        full = False
                        time.sleep(4 + random.gamma(5, .5))
                        stop_check(stop)
                        new_site_BM = resource_bookmarks[0]
                        print(f'\r Warping to bookmark {new_site_BM}')
                        warp_to_bookmark(who, new_site_BM, main_screen)
                        while is_warping(screens[0]) is False:  # waiting until warp is recognized
                            time.sleep(.5)
                        for i in range(0, len(toons)):
                            stop_check(stop)
                            set_active_toon(toons[i], screens[i])
                            find_ui_element(screens[i], 'close', 1378, 327, 1975, 905, button='left')
                        set_active_toon(main_toon, main_screen)
                        while is_warping(screens[0]) is True:       # loop for duration of warp
                            time.sleep(.5)
                            stop_check(stop)
                        current_location = 'site grid'
                        time.sleep(1 + random.gamma(3, .2))

                        # -------- lock up nearest resource   --------
                        drones = 'Deploy'
                        distance = lock_up_resources(harvest_range, drones=drones)
                        recalled = False
                        if distance > harvest_range:
                            full = True
                            return_to_site = False
        iterations += 1

    #
    # ========/////======/////=======/////======                  ======/////========/////=======/////========
    # =======/////======/////=======/////======  EMERGENCY WARP  ======/////========/////=======/////=========
    # ======/////======/////=======/////======                  ======/////========/////=======/////==========
    #

    stop_check(stop)
    set_active_toon(main_toon, main_screen)

    stop_check(stop)
    if current_location != 'fort grid':
        response = warp_to_bookmark(who, safe_spot, main_screen)
        if response == 'not found':
            time.sleep(.5 + random.gamma(3, .1))
            reset_mouse(main_screen)
            time.sleep(.5 + random.gamma(3, .1))
            response = warp_to_bookmark(who, dropoff_location, main_screen)
            if response == 'not found':
                print(f" Can't initiate emergency warp to {safe_spot}. Goodbye. Don't Die.")
                quit()
        else:
            print('\n Initiating warp to safety', end='')

        # ----- recall drones -----
        if action == 'Mining':
            for i in range(0, len(toons)):
                stop_check(stop)
                set_active_toon(toons[i], screens[i])
                recall_drones(screens[i])
                time.sleep(.1 + random.gamma(1, .1))
            set_active_toon(main_toon, main_screen)

        count = 0
        warped_off = True
        while is_warping(screens[0]) is False:  # waits for warp to initiate
            time.sleep(.5)

        if safe_spot == 'Safe':
            time.sleep(6 + random.gamma(8, .08))

            print('\r Cloaking up', end='')
            for i in range(0, len(toons)):
                stop_check(stop)
                set_active_toon(toons[i], screens[i])
                time.sleep(.3 + random.gamma(3, .04))
                stop_check(stop)
                # double_click_in_space(screens[i])
                # stop_check(stop)
                # toggle_module('MWD + cloak')  # activate MWD
                toggle_module('cloak')

            set_active_toon(main_toon, main_screen)
            time.sleep(.5 + random.gamma(3, .15))
            if who == 'Squad' and ships == 'Prospects':
                set_fleet_formation('point', main_screen)

        while is_warping(screens[0]) is True:  # waits for warp to end
            time.sleep(.5)
        print(f'\r Arrived at {safe_spot}'), time.sleep(.5)

    if safe_spot == 'InstaDock' and dock is True:  # on grid with fort already
        print('\r Docking up')
        for i in range(0, len(toons)):
            stop_check(stop)
            set_active_toon(toons[i], screens[i])
            time.sleep(.3 + random.gamma(3, .15))
            dock_up(screens[i])
        time.sleep(20 + random.gamma(5, 2))
        set_active_toon(scanner, screens[toons.index(scanner)])
        switch_pod('laptop', 'Virtues')
        time.sleep(20 + random.gamma(5, 2))
        switch_ship('laptop', 'Pacifier')
        quit()

    if continue_scanning is True:
        safe_time = time.time()
        number = 1
        while time.time() - safe_time < 60:
            if 'dscan_interval' not in locals() or automate_Dscan is True\
                    and time.time() >= last_dscan_time+dscan_interval:
                stop_check(stop)
                if gw.getActiveWindow() is not None and gw.getActiveWindow().title == 'EVE - ' + main_toon:
                    pyautogui.keyDown('`')
                    time.sleep(.1 + random.gamma(3, .03))
                    pyautogui.keyUp('`')
                    time.sleep(.5)
                    last_dscan_time = time.time()

                    # --------   Save D-Scan results    --------
                    dscan_results = watch_dscan(main_screen, save=True, number=str(number))
                    dscan_interval = 1 + random.gamma(1.5, 1.5)
                    number += 1
    quit()
