import time
import _thread
import neopixel
from machine import Pin

from ble import ESP32_BLE
from pattern import Patterns

np = neopixel.NeoPixel(Pin(13), 60)
p = Patterns(np, color=(209, 6, 182), sleep=5, pattern='all')
ble = ESP32_BLE("ESP32BLE_BLACK")


colors = {
    0: (209, 6, 182),
    1: (255, 0, 0),
    2: (0, 255, 0),
    3: (0, 0, 255),
    4: (1, 231, 255),
    5: (239, 255, 1),
}


patterns = {
    0: 'cycle',
    1: 'bounce',
    2: 'all',
    3: 'sweep',
    4: 'intermittent'
}

len_colors = len(colors)
color = 0

len_patterns = len(patterns)
pattern = 0

led_2 = Pin(2, Pin.OUT, value=0)
led_12 = Pin(12, Pin.OUT)


def notification(function):
    def wrapper(*args, **kwargs):
        is_change = function(*args, **kwargs)
        if is_change:
            led_12.on()
            time.sleep_ms(200)
            led_12.off()
            ble.send('>>> ' + args[0])
    return wrapper


@notification
def set_color(msg):
    msg = msg.lstrip('#')
    msg = tuple(int(msg[i:i+2], 16) for i in (0, 2, 4))
    if p.color != msg:
        p.color = msg
        return True
    return False


@notification
def set_pattern(msg):
    if p.pattern != msg:
        p.pattern = msg
        return True
    return False


@notification
def change_color(is_continue):
    global color
    try:
        is_continue = int(is_continue)
    except:
        return False

    if not 0 <= is_continue < 2:
        return False

    if is_continue:
        color -= 1
    else:
        color += 1

    color = color % len_colors
    p.color = colors[color]
    return True


@notification
def change_pattern(is_continue):
    global pattern
    is_continue = int(is_continue)

    if is_continue:
        pattern -= 1
    else:
        pattern += 1

    pattern = pattern % len_patterns
    p.pattern = patterns[pattern]
    return True


def buttons_irq():
    global ble
    led_2.value(not led_2.value())


def start_leds():
    while True:
        set_patterns()


def set_patterns():
    global pattern
    p.select_pattern()()


def bluetooth_run():
    global ble
    global client
    led_2.off()
    _thread.start_new_thread(start_leds, ())
    done = True

    while done:

        msg = list(map(lambda x: x.strip(), ble.ble_msg.split(':')))

        if msg[0] == 'led':
            buttons_irq()
            ble.send('LED is ON.' if led_2.value() else 'LED is OFF')

        if msg[0] == 'rgb':
            set_color(msg[1])

        if msg[0] == 'pattern':
            set_pattern(msg[1])

        if msg[0] == 'change_color':
            change_color(msg[1])

        if msg[0] == 'change_pattern':
            change_pattern(msg[1])

        ble.ble_msg = ""
        time.sleep_ms(100)


if __name__ == '__main__':
    bluetooth_run()

