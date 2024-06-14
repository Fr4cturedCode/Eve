from a1_functions import *




toons = ['Zoe Washborn']
# toon = 'Cave Dweller'
# toon = 'Schnozzberries'
# toon = 'AlienFaceMcGee'
# toon = 'Fr4ctured Mind'
# toon = 'Astina Leanni'
# toon = 'Aetarin Thiesant'
# toon = 'DangLang'
# toon = 'Adopted Clown'
# toon = 'Zoe Washborn'

cloak = 'none'
# cloak = 'standard'
# cloak = 'covert'

mwd = 'ignore'
# mwd = 'mwd align'
# mwd = 'cloak trick'

hold_on_dangerous_gate = False

screen = find_screens(toons)[0]
print('\n-------------------------------------')
print(f' Cloak: {cloak} \n MWD: {mwd}')
print(f' Hold on dangerous gate: {hold_on_dangerous_gate}')

# while gw.getActiveWindow() is not None and gw.getActiveWindow().title != 'EVE - ' + toon:
#     print(f"\r  Click on {toon}'s client.", end='')
#     time.sleep(0.5)

print('\r   ++++  Autopilot Engaged  ++++')
desto = identify_destination(screen)
if desto == 'Amarr' or desto == 'Jita':
    print(f'         Destination: {desto}')
print('--------------------------------------')
time.sleep(0.5)

danger = False
station_bookmark = False

successful_jumps = 0
destination_system = False
while destination_system is False:

    #### selects first stargate on initiation  #####
    if successful_jumps == 0:
        if find_next_gate(screen) == 'no gate found':
            print('No Destination. Autopilot off')
            quit()
        print('Selecting first gate')

    #### checks to see what the desto is  ####
    has_desto = identify_destination(screen)
    if has_desto == 'No Destination':
        if successful_jumps == 0:
            print('No desto chosen')
            quit()

        if successful_jumps > 0:
            print('Arrived at desto')
            time.sleep(5 + random.gamma(3, .5))

            double_click_in_space(screen)
            if cloak == 'covert' or cloak == 'standard':
                time.sleep(.3 + random.gamma(2, .1))
                # print('Cloaking')
                toggle_module('MWD + cloak')
            quit()

    progress = selected_item(screen)

    #### selects a new gate if one is not selected  #####
    if progress == 'no object selected' or progress =='no buttons detected':
        print('Selecting gate')
        if find_next_gate(screen) == 'no gate found':
            print('Autopilot off')
            break

        if mwd != 'cloak trick':
            selected_item(screen, action='warp/dock')
        elif mwd == 'cloak trick':
            selected_item(screen, action='align')

    #### check for dangerous gates  #####
    if progress == 'dangerous gate':
        print('Dangerous gate detected: ', end='')
        danger = True
        if hold_on_dangerous_gate is True:
            print('Entering Holding Pattern')
            response = warp_to_bookmark('Self', 'holding_pattern', 'laptop')
        if hold_on_dangerous_gate is False:
            print('Proceeding')
            selected_item(screen, action='warp/dock')  # clicks on jump gate

    ##### checks to see if the selected item is a station  #######
    elif progress == 'at destination':
        danger = False
        destination_system = True
        print('Arrived in destination system')

        if desto == 'Jita' or desto == 'Amarr':
            response = warp_to_bookmark('Self', f'{desto}_dock', 'laptop')
            print('   - Warping to bookmark')
            station_bookmark = True
        else:
            selected_item(screen, action='warp/dock')
            print('   - Warping directly to station')
            station_bookmark = False

    #### if the selected item is a gate  ######
    elif progress == 'in route':
        danger = False
        if mwd != 'cloak trick':
            selected_item(screen, action='warp/dock')
        elif mwd == 'cloak trick':
            selected_item(screen, action='align')   # clicks on jump gate
        print('Warping to gate', end='')

    #####   stuff prior to warp   ######
    if mwd == 'mwd align':
        time.sleep(.3 + random.gamma(2, .1))
        toggle_module('MWD')
    if mwd == 'cloak trick':
        time.sleep(.3 + random.gamma(2, .1))
        toggle_module('MWD + cloak')
        time.sleep(np.random.uniform(low=6.5, high=8, size=(1))[0])
        toggle_module('cloak')
        time.sleep(.3 + random.gamma(2, .1))
        selected_item(screen, action='warp/dock')  # clicks on jump gate
    if cloak == 'covert' and successful_jumps != 0:
        time.sleep(.3 + random.gamma(2, .1))
        # print('Cloaking')
        toggle_module('cloak')

    ##### detecting if the warp was accepted   #####
    print('\rAligning', end='')
    while is_warping(screen) is False:
        time.sleep(.5)
    print('\rWarping', end='')

    if station_bookmark is True:
        time.sleep(2 + random.gamma(3, .5))
        reset_mouse(screen)
        time.sleep(.5 + random.gamma(3, .1))
        print('\rEngaging autopilot for insta-dock')
        pyautogui.keyDown('p')
        time.sleep(.1 + random.gamma(3, .05))
        pyautogui.keyUp('p')
        break

    while is_warping(screen) is True:
        time.sleep(.5)

    #### if the warp was before a dangerous gate  ####
    if danger is True and hold_on_dangerous_gate is True:
        time.sleep(1)
        if cloak != 'none':
            if is_module_active('cloak', 'laptop') is False:
                toggle_module('cloak')
            print('Cloaking up')
            break

    #####   if the warp was to a station   ######
    if destination_system is True and station_bookmark is False:
        print('\rDocking')
        time.sleep(.5)
        selected_item(screen, action='continue')
        break

    #### waits after exiting warp and before taking the stargate   ######
    print('\rWaiting to jump', end='')
    while selected_item(screen) != 'no object selected':
        time.sleep(0.3)

    #### detects that the selected item disappeared and new system entered  ######
    count = 0
    print('\rJumping')
    while selected_item(screen) == 'no object selected':
        time.sleep(0.5)
        if count == 20:
            print('Reselecting next gate')
            break
        count += 1

    #### different plan if next system is dangerou ###
    if danger is True:
        print('Choosing random outgate bookmark')
        num = str(np.random.randint(1, 5))
        if desto == 'Amarr':
            warp_to_bookmark('self', 'shera' + num, 'laptop')
        if desto == 'Jita':
            warp_to_bookmark('self', 'hyk' + num, 'laptop')

        #####   stuff prior to warp   ######
        if mwd == 'mwd align':
            time.sleep(0.5)
            toggle_module('MWD')
        if mwd == 'cloak trick':
            time.sleep(.3 + random.gamma(2, .1))
            toggle_module('MWD + cloak')
            time.sleep(np.random.uniform(low=8, high=9.5, size=(1))[0])
            toggle_module('cloak')
            selected_item(screen, action='warp/dock')  # clicks on jump gate
        if cloak == 'covert' and successful_jumps != 0:
            time.sleep(0.5)
            print('Cloaking')
            toggle_module('cloak')

        ##### detecting if the warp was accepted   #####
        print('Aligning', end='')
        while is_warping(screen) is False:
            time.sleep(.5)
        print('\rWarping')
        while is_warping(screen) is True:
            time.sleep(.5)


    ### count jumps ####
    successful_jumps += 1
    time.sleep(1)