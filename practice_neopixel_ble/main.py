import time
import _thread
import neopixel
from machine import Pin

from ble import ESP32_BLE
from pattern import Patterns

np = neopixel.NeoPixel(Pin(13), 60)
p = Patterns(np, 5)
ble = ESP32_BLE("ESP32BLE_BLACK")

color = (209, 6, 182)
pattern = 'all'

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
def change_color(msg):
    global color
    msg = msg.lstrip('#')
    msg = tuple(int(msg[i:i+2], 16) for i in (0, 2, 4))
    if color != msg:
        color = msg
        return True
    return False


@notification
def change_pattern(msg):
    global pattern
    if pattern != msg:
        pattern = msg
        return True
    return False


def buttons_irq(pin):
    global ble
    led_2.value(not led_2.value())


def start_leds():
    while True:
        patterns()


def patterns():
    global color
    global pattern
    p.select_pattern(pattern)(color)


def bluetooth_run():
    global ble
    global client
    led_2.off()
    _thread.start_new_thread(start_leds, ())
    done = True

    while done:

        msg = list(map(lambda x: x.strip(), ble.ble_msg.split(':')))

        if msg[0] == 'led':
            buttons_irq(None)
            ble.send('LED is ON.' if led_2.value() else 'LED is OFF')

        if msg[0] == 'rgb':
            change_color(msg[1])

        if msg[0] == 'pattern':
            change_pattern(msg[1])

        ble.ble_msg = ""
        time.sleep_ms(100)


if __name__ == '__main__':
    bluetooth_run()
