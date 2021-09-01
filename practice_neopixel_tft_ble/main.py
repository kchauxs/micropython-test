import time
import _thread
import neopixel
from ST7735 import TFT
from machine import Pin, SPI
from sysfont import sysfont
from ble import ESP32_BLE
from pattern import Patterns


np = neopixel.NeoPixel(Pin(13), 60)
spi = SPI(1, 1000000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(27))
tft = TFT(spi, 26, 25, 33)  # DC/AO, RST, CS

tft.initr()
tft.rgb()
tft.rotation(2)
tft.fill(TFT.BLACK)


ble = ESP32_BLE("ESP32BLE_BLACK")
p = Patterns(np, 5)
color = (0, 0, 255)
pattern = 'all'

led_2 = Pin(2, Pin.OUT, value=0)
led_12 = Pin(12, Pin.OUT)


def tft_draw_char(string, px, py):
    long = len(string)
    for x in range(long):
        c = string[x]
        tft.text((px, py), str(c), TFT.PURPLE, sysfont, 1)
        time.sleep_ms(120)
        px = px + 6


y = 30


def notification(function):

    def wrapper(*args, **kwargs):
        global y
        is_change = function(*args, **kwargs)
        if is_change:
            led_12.on()
            time.sleep_ms(200)
            led_12.off()

            if y >= 140:
                tft.fill(TFT.BLACK)
                tft.text((25, 10), "Notification", TFT.CYAN, sysfont, 1)
                y = 30

            tft.text((5, y), ">>>", TFT.GREEN, sysfont, 1)
            tft_draw_char(args[0], 26, y)
            y += 10

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


def init():
    tft.fill(TFT.BLACK)
    time.sleep_ms(1200)
    tft.text((13, 10), "Espressif Esp-32", TFT.GREEN, sysfont, 1)
    tft.text((20, 20), "Con MicroPython", TFT.GREEN, sysfont, 1)
    time.sleep_ms(1500)
    tft.text((5, 40), "Sistema Inicializado", TFT.GREEN, sysfont, 1)
    time.sleep_ms(500)
    tft.text((5, 50), "Verificando Comandos", TFT.GREEN, sysfont, 1)
    time.sleep_ms(400)
    tft.text((5, 70), ">>>", TFT.GREEN, sysfont, 1)
    time.sleep_ms(1400)
    tft_draw_char("led.on()", 26, 70)
    led_2.on()
    tft.text((5, 80), ">>>", TFT.GREEN, sysfont, 1)
    time.sleep_ms(1400)
    tft_draw_char("led.off()", 26, 80)
    led_2.off()
    time.sleep_ms(4000)
    tft.fill(TFT.BLACK)
    tft.text((25, 10), "Notification", TFT.CYAN, sysfont, 1)


if __name__ == '__main__':
    init()
    bluetooth_run()
