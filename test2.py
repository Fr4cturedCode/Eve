import vlc
import time


def alarm_sound():
    p = vlc.MediaPlayer('sounds/alarm.mp3')
    p.play()
    time.sleep(1)