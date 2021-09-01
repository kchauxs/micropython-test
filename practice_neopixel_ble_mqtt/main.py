import time
import esp32
import btree
import machine
import _thread
import network
import ubinascii
import neopixel
from machine import unique_id, Pin
from pattern import Patterns
from umqttsimple import MQTTClient
from ble import ESP32_BLE

try:
    f = open("mydb", "r+b")
except OSError:
    f = open("mydb", "w+b")

db = btree.open(f)
np = neopixel.NeoPixel(machine.Pin(13), 60)
p = Patterns(np, 5)
led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)
noti = Pin(12, Pin.OUT)
color = (0, 0, 255)
pattern = 'all'


ble = ESP32_BLE("ESP32BLE_WEMOS")
client = None


# MQTT
mqtt_server = ''
port_mqtt = 0
# user
user_mqtt = ''
pswd_mqtt = ''
# topico
root_topic = ''
subtopic = ''
node = root_topic + '/' + subtopic + '/'


def notification(function):
    def wrapper(*args, **kwargs):
        is_change = function(*args, **kwargs)
        if is_change:
            noti.on()
            time.sleep_ms(200)
            noti.off()
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


def form_sub(topic, msg):
    msg = str(msg.decode())
    if len(msg) != 0:

        if topic.decode() == node+'rgb':
            change_color(msg)

        if topic.decode() == node+'pattern':
            change_pattern(msg)

        print("[INFO] Recivido de:", (topic.decode(), msg))


def Connection_MQTT():
    client_id = ubinascii.hexlify(unique_id())
    """ 
    client = MQTTClient(client_id,
                        db[b'mqtt_server'].decode(),
                        db[b'port_mqtt'].decode(),
                        db[b'user_mqtt'].decode(),
                        db[b'pswd_mqtt'].decode())
    """
    client = MQTTClient(client_id,
                        mqtt_server,
                        port_mqtt,
                        user_mqtt,
                        pswd_mqtt)

    client.set_callback(form_sub)
    client.connect()
    client.subscribe(b''+node+'#')

    led.on()
    return client


def do_connect(data):
    try:
        if db[b'ssid'].decode() != data[0]:
            db[b'ssid'] = data[0]

        if db[b'ssid'].decode() != data[1]:
            db[b'password'] = data[1]

    except Exception:
        db[b'ssid'] = data[0]
        db[b'password'] = data[1]

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(db[b'ssid'].decode(), db[b'password'].decode())

    while not wlan.isconnected():
        print('.....')

    if not wlan.isconnected():
        print('Not connected to WIFI')
        return False

    print('network config:', wlan.ifconfig())
    return True


def Restart_Connection():
    db.close()
    f.close()
    led.off()
    print('Fallo en la conexion. Intentando de nuevo...')
    time.sleep(5)
    machine.reset()


def buttons_irq(pin):
    global ble
    led.value(not led.value())


def fahrenhei_celsius(x): return round((x-32)*(5/9), 2)


def patterns():
    global color
    global pattern
    global reverse
    p.select_pattern()[pattern](color)


def start_leds():
    while True:
        patterns()


def wifi_run():
    try:

        last_message = 0
        message_interval = 5
        counter = 0

        while True:
            client.check_msg()

            if (time.time() - last_message) > message_interval:
                msg = b'Temp %d:' % counter + \
                    ' %d' % fahrenhei_celsius(esp32.raw_temperature())
                client.publish(node+'temp', msg)
                counter += 1
                last_message = time.time()
                time.sleep_ms(50)

    except OSError as e:
        Restart_Connection()


def bluetooth_run():
    global ble
    global client
    led.off()
    _thread.start_new_thread(start_leds, ())
    done = True

    while done:
        msg = ble.ble_msg.split(':')

        if msg[0] == 'wifi' and len(msg) == 3:
            if do_connect(msg[1:]):
                client = Connection_MQTT()
                done = False
            else:
                ble.send('Not connected to WIFI')

        if msg[0] == 'led':
            buttons_irq(None)
            ble.send('LED is ON.' if led.value() else 'LED is OFF')

        if msg[0] == 'rgb':
            change_color(msg[1].strip())

        if msg[0] == 'pattern':
            change_pattern(msg[1].strip())

        ble.ble_msg = ""
        time.sleep_ms(100)

    try:
        ble.ble.active(False)
    except OSError:
        del ble


if __name__ == '__main__':

    but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)
    bluetooth_run()
    wifi_run()
