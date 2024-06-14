from a1_functions import *
toons = []


#
# ==================================

hold_on_dangerous_gate = False

# toons = ['Cave Dweller']
# toons = ['Aetarin Thiesant']
toons = ['Astina Leanni']

# ==================================
#

if not toons:
    windows = gw.getAllTitles()
    for title in windows:
        if 'EVE - ' in title:
            toons.append(title[6:])
screens = find_screens(toons)

ships = []
cloak = []
autopilot = []
mwd = []
covert = []
at_safe = []
for i in range(0, len(toons)):
    autopilot.append(True)
    mwd.append('ignore')
    covert.append(False)
    cloak.append('none')
    ships.append('Unrecognized')
    at_safe.append(False)

covert_capable = ['Pacifier', 'Prowler']
MWD_align_ships = ['Orca', 'Bowhead']
MWD_cloak_trick = ['Mastodon']

print('\n-------------------------------------')
# print(f' Cloak: {cloak} \n MWD: {mwd}')
print(f' Hold on dangerous gate: {hold_on_dangerous_gate}')
print('\r   ++++  Autopilot Engaged  ++++')
print('--------------------------------------')
time.sleep(0.5)

iterations = 0
while True in autopilot:

    for i in range(0, len(toons)):

        # stop_check(stop)
        if autopilot[i] is True:
            set_active_toon(toons[i], screens[i])

            # ================= First iteration / setup ================
            if iterations == 0:
                # ------ ensure that there is a route/destination -------
                desto = identify_destination(screens[i])
                if desto == 'No Destination':
                    print(f'\r {toons[i]} No destination set', end='')
                    autopilot[i] = False
                    time.sleep(.5 + random.gamma(3, .1))
                    continue

                # ----- select first gate -----
                change_tab('pvp_tab', screens[i])
                time.sleep(.3 + random.gamma(3, .1))
                if find_next_gate(screens[i]) == 'no gate found':
                    print(f'\r {toons[i]} No warp object found', end='')
                    autopilot[i] = False
                    time.sleep(.5 + random.gamma(3, .1))
                    continue

                # ------ determine ship/modules -------
                present_modules = detect_present_modules(screens[i])
                ships[i] = detect_current_ship(screens[i], present_modules)
                # ---- cloak setting ------
                if 'cloak' in present_modules:
                    cloak[i] = 'cloak'
                if ships[i] in covert_capable:
                    cloak[i] = 'covert'
                # ---- mwd setting -----
                if ships[i] in MWD_align_ships:
                    mwd[i] = 'mwd align'
                if ships[i] in MWD_cloak_trick:
                    mwd[i] = 'cloak trick'
                print(f'\r {toons[i]}: {ships[i]}', end='')

            # ----------------------------///                 ///----------------------------
            # ===========================///    MAIN LOOP    ///=============================
            # --------------------------///                 ///-----------------------------

            # ========= detect if input needed (ship stopped) =========
            aligning = False          # resetting value
            stopped = find_ui_element(screens[i], 'stopped', 681, 1372, 1057, 1599, silent=True, threshold=.95)
            if stopped == 'not found':
                response = find_ui_element(screens[i], 'aligning', 641, 1202, 1159, 1306, silent=True, threshold=.95)
                if response != 'not found':
                    aligning = True   # used for MWD align protection
            if stopped != 'not found' or aligning is True:

                # ========== check for route/destination ===========
                if iterations > 0:
                    desto = identify_destination(screens[i])
                    if desto == 'No Destination':
                        if cloak[i] != 'none':
                            time.sleep(5 + random.gamma(3, .5))
                            double_click_in_space(screens[i])
                            time.sleep(.3 + random.gamma(2, .1))
                            print(f'\r {toons[i]} Cloaking', end='')
                            toggle_module('MWD + cloak')
                        print(f'\r {toons[i]} Arrived. \n Removing from autopilot list', end='')
                        autopilot[i] = False
                        time.sleep(.5 + random.gamma(3, .1))
                        continue

                # ---- examine selected outgate/object ----
                progress = selected_item(screens[i])

                # ================================       ======================================
                # =============================   WARPING   ===================================
                # ================================       ======================================

                # ============ Nothing selected ===========
                if progress == 'no object selected' or progress == 'no buttons detected':
                    time.sleep(2 + random.gamma(3, .5))
                    progress = selected_item(screens[i])

                    if progress == 'no object selected' or progress == 'no buttons detected':
                        time.sleep(2 + random.gamma(3, .5))
                        print(f'\r {toons[i]} Selecting gate', end='')
                        if find_next_gate(screens[i]) == 'no gate found':
                            print(f'\r {toons[i]} No outgate found. \n Removing from autopilot list', end='')
                            autopilot[i] = False
                            time.sleep(.5 + random.gamma(3, .1))
                            continue

                # =========== if GATE selected ===========
                elif progress == 'in route':
                    print(f'\r {toons[i]} Warping to gate', end='')
                    if mwd[i] != 'cloak trick' or aligning is True:
                        selected_item(screens[i], action='warp/dock')
                    elif mwd[i] == 'cloak trick':
                        selected_item(screens[i], action='align')  # clicks on jump gate

                    if mwd[i] == 'mwd align' and aligning is False:
                        time.sleep(0.5)
                        toggle_module('MWD')
                    if mwd[i] == 'cloak trick' and aligning is False:
                        time.sleep(.3 + random.gamma(2, .1))
                        toggle_module('MWD + cloak')
                        time.sleep(np.random.uniform(low=6.5, high=8, size=(1))[0])
                        toggle_module('cloak')
                        selected_item(screens[i], action='warp/dock')  # clicks on jump gate
                    if cloak[i] == 'covert':
                        time.sleep(0.5)
                        print(f' {toons[i]} Cloaking', end='')
                        toggle_module('cloak')

                # ========= if STATION selected ============
                elif progress == 'at destination':
                    destination_system = True
                    print(f'\r {toons[i]} In destination system', end='')

                    # --------- warp to station bookmark/instadock ------------
                    if desto == 'Jita' or desto == 'Amarr':
                        response = warp_to_bookmark('Self', f'{desto}_dock', 'laptop')
                        print(f'\r {toons[i]} Warping to InstaDock', end='')

                        if mwd[i] == 'mwd align' and aligning is False:
                            time.sleep(0.5)
                            toggle_module('MWD')
                        # if mwd[i] == 'cloak trick' and aligning is False:
                        #     time.sleep(.3 + random.gamma(2, .1))
                        #     toggle_module('MWD + cloak')
                        #     time.sleep(np.random.uniform(low=6.5, high=8, size=(1))[0])
                        #     toggle_module('cloak')
                        #     selected_item(screens[i], action='warp/dock')  # clicks on jump gate
                        if cloak[i] == 'covert':
                            time.sleep(0.5)
                            print(f' {toons[i]} Cloaking', end='')
                            toggle_module('cloak')

                        # --- engaging autopilot for instadock
                        time.sleep(2 + random.gamma(3, .5))
                        reset_mouse(screens[i])
                        time.sleep(.5 + random.gamma(3, .1))
                        print(f'\r {toons[i]} Engaging autopilot for docking', end='')
                        pyautogui.keyDown('p')
                        time.sleep(.1 + random.gamma(3, .05))
                        pyautogui.keyUp('p')
                        autopilot[i] = False
                        time.sleep(.5 + random.gamma(3, .1))
                        continue

                    # ----------- warping directly to station -----------
                    else:
                        print(f'\r {toons[i]} Warping directly to station', end='')
                        if mwd[i] != 'cloak trick' or aligning is True:
                            selected_item(screens[i], action='warp/dock')
                        elif mwd[i] == 'cloak trick':
                            selected_item(screens[i], action='align')  # clicks on jump gate

                        if mwd[i] == 'mwd align' and aligning is False:
                            time.sleep(0.5)
                            toggle_module('MWD')
                        if mwd[i] == 'cloak trick' and aligning is False:
                            time.sleep(.3 + random.gamma(2, .1))
                            toggle_module('MWD + cloak')
                            time.sleep(np.random.uniform(low=6.5, high=8, size=(1))[0])
                            toggle_module('cloak')
                            selected_item(screens[i], action='warp/dock')  # clicks on jump gate
                        if cloak[i] == 'covert':
                            time.sleep(0.5)
                            print(f' {toons[i]} Cloaking', end='')
                            toggle_module('cloak')

                # =============================================================================
                # ============================== DANGEROUS SYSTEMS ============================
                # =============================================================================
                elif 'dangerous' in progress:
                    print(f'\r {toons[i]} Dangerous gate detected: {progress[15:]}..', end='')

                    # ========  behavior for specific systems =========   (ignores "Hold_on")
                    if 'Lor' in progress or 'Hykkota' in progress or 'Shera' in progress:

                        # --- check if in Ahbazon ----
                        response = find_ui_element(screens[i], 'ahbazon_bookmarks', 448, 0, 773, 350, silent=True)

                        # ---- not in Ahbazon, continue ----
                        if response == 'not found':
                            print('\r Not yet in Ahbazon', end='')
                            selected_item(screens[i], action='warp/dock')

                        # ----- inside Ahbazon -------
                        else:
                            num = str(np.random.randint(1, 5))
                            if 'Lor' in progress:
                                safe = 'lor' + num
                            if 'Hykkota' in progress:
                                safe = 'hyk' + num
                            if 'Shera' in progress:
                                safe = 'shera' + num
                            print(f'\r {toons[i]} Warping to {safe} prior to gate', end='')
                            warp_to_bookmark('Self', safe, screens[i])  # warps to bookmark

                            if mwd[i] == 'mwd align':
                                time.sleep(.5 + random.gamma(2, .2))
                                toggle_module('MWD')
                            # if mwd[i] == 'cloak trick':
                            #     time.sleep(.3 + random.gamma(2, .1))
                            #     toggle_module('MWD + cloak')
                            #     time.sleep(np.random.uniform(low=6.5, high=8, size=(1))[0])
                            #     toggle_module('cloak')
                            #     selected_item(screens[i], action='warp/dock')  # clicks on jump gate
                            if cloak[i] == 'covert':
                                time.sleep(.5 + random.gamma(2, .2))
                                print(f' {toons[i]} Cloaking', end='')
                                toggle_module('cloak')

                            while is_warping(screens[i]) is False:
                                time.sleep(.5)
                            while is_warping(screens[i]) is True:  # waits
                                time.sleep(.5)
                            time.sleep(.5 + random.gamma(2, .1))

                            print(f'\r {toons[i]} Warping to gate', end='')
                            selected_item(screens[i], action='warp/dock')  # warps from bookmark to gate
                            if mwd[i] == 'mwd align':
                                time.sleep(.5 + random.gamma(2, .2))
                                toggle_module('MWD')

                    # ======== not one of the specific systems listed above ========
                    else:
                        if hold_on_dangerous_gate is True:

                            # ------ stops in at bookmark in system before Ahbazon ---------
                            if 'Ahbazon' in progress:
                                print(' Holding', end='')
                                response = warp_to_bookmark('Self', 'holding_pattern', screens[i])

                                if mwd[i] == 'mwd align' and aligning is False:
                                    time.sleep(.5 + random.gamma(2, .2))
                                    toggle_module('MWD')
                                # if mwd[i] == 'cloak trick' and aligning is False:
                                #     time.sleep(.3 + random.gamma(2, .1))
                                #     toggle_module('MWD + cloak')
                                #     time.sleep(np.random.uniform(low=6.5, high=8, size=(1))[0])
                                #     toggle_module('cloak')
                                #     selected_item(screens[i], action='warp/dock')  # clicks on jump gate

                                if cloak[i] == 'covert':
                                    time.sleep(.5 + random.gamma(2, .2))
                                    print(f' {toons[i]} Cloaking', end='')
                                    toggle_module('cloak')

                                elif cloak[i] != 'none':
                                    while is_warping(screens[i]) is False:
                                        time.sleep(.5)
                                    while is_warping(screens[i]) is True:
                                        time.sleep(.5)
                                    time.sleep(5 + random.gamma(3, 2))
                                    toggle_module('cloak')
                                autopilot[i] = False
                                time.sleep(.5 + random.gamma(3, .1))
                                continue

                            # ------ any other dangerous unrecognized gate ------- (add low-sec awareness)
                            else:
                                if cloak[i] != 'none':
                                    time.sleep(5 + random.gamma(3, .5))
                                    double_click_in_space(screens[i])
                                    time.sleep(.3 + random.gamma(2, .1))
                                    print(f'\r {toons[i]} Cloaking', end='')
                                    toggle_module('MWD + cloak')
                                print(f'\r {toons[i]} Holding before dangerous gate', end='')
                                autopilot[i] = False
                                time.sleep(.5 + random.gamma(3, .1))
                                continue

                        elif hold_on_dangerous_gate is False:
                            print(' Proceeding', end='')
                            selected_item(screens[i], action='warp/dock')

            time.sleep(.5 + random.gamma(2, .1))

    # --- reselects valid autopilot toon on first iteration (annoyance fix) ----
    if iterations == 0:
        for i in range(0, len(toons)):
            if autopilot[i] is True:
                set_active_toon(toons[i], screens[i])
                break

    time.sleep(5 + random.gamma(5, .5))
    iterations += 1

print('\n  ---Autopilot Complete---')


