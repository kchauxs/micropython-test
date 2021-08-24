import time
import esp32
import machine
import network
import _thread
import neopixel
import ubinascii
from machine import unique_id, Pin
from umqttsimple import MQTTClient
from pattern import Patterns

# WIFI
ssid = ''  # Nombre de la Red
password = ''  # Contraseña de la red

# MQTT
mqtt_server = ''
port_mqtt = 1883
# user
user_mqtt = ''
pswd_mqtt = ''
# topico
root_topic = ''
subtopic = ''

node = root_topic + '/' + subtopic + '/'

# LEDS
led_2 = Pin(2, Pin.OUT)
np = neopixel.NeoPixel(machine.Pin(13), 60)
color = (0, 0, 255)
pattern = 'all'
p = Patterns(np, 5)
# buzzer - (opcional)
buzzer = Pin(12, Pin.OUT)


def activate_buzzer(function):
    def wrapper(*args, **kwargs):
        function(*args, **kwargs)
        buzzer.on()
        time.sleep_ms(200)
        buzzer.off()
    return wrapper


@activate_buzzer
def change_color(msg):
    global color
    msg = msg.lstrip('#')
    color = tuple(int(msg[i:i+2], 16) for i in (0, 2, 4))


@activate_buzzer
def change_pattern(msg):
    global pattern
    if pattern == msg:
        return
    pattern = msg


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
    client = MQTTClient(client_id, mqtt_server,
                        port_mqtt, user_mqtt, pswd_mqtt)
    client.set_callback(form_sub)
    client.connect()
    client.subscribe(b''+node+'#')

    #print('connected to %s' % mqtt_server, 20, 30, 0)
    print('MQTT:%s' % mqtt_server)
    led_2.on()
    return client


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print('.....')
    print('network config:', wlan.ifconfig())


# Reinicia la conexión de MQTT
def Restart_Connection():
    led_2.off()
    print('Fallo en la conexion. Intentando de nuevo...')
    time.sleep(10)
    machine.reset()


def patterns():
    global color
    global pattern

    if pattern == 'cycle':
        p.cycle(color)

    if pattern == 'bounce':
        p.bounce(color)

    if pattern == 'all':
        p.all(color)

    if pattern == 'fade':
        p.fade()

    if pattern == 'clear':
        p.clear()


def start_leds():
    while 1:
        patterns()


def fahrenhei_celsius(x):
    return round((x-32)*(5/9), 2)


if __name__ == '__main__':
    do_connect()

    try:
        client = Connection_MQTT()
    except OSError as e:
        Restart_Connection()

    _thread.start_new_thread(start_leds, ())

    last_message = 0
    message_interval = 5
    counter = 0

    while True:

        try:
            client.check_msg()

            if (time.time() - last_message) > message_interval:
                temp = fahrenhei_celsius(esp32.raw_temperature())
                msg = b'Temp %d:' % counter + ' %d' % temp
                client.publish(node+'temp', msg)
                counter += 1
                last_message = time.time()
                time.sleep_ms(50)

        except OSError as e:
            Restart_Connection()
