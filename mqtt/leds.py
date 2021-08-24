# Librerias
import machine
import time
import ubinascii
from umqttsimple import MQTTClient
from machine import unique_id, Pin
import micropython
import network
import esp32
import ssd1306


# DISPLAY
scl = machine.Pin(19, machine.Pin.OUT, machine.Pin.PULL_UP)
sda = machine.Pin(21, machine.Pin.OUT, machine.Pin.PULL_UP)
i2c = machine.I2C(scl=scl, sda=sda, freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
# WIFI
ssid = ''  # Nombre de la Red
password = ''  # Contraseña de la red
# MQTT
root_topic = ''
subtopic = ''
node = root_topic + '/' + subtopic + '/'
# LEDS
led_2 = Pin(2, Pin.OUT)
led_22 = Pin(22, Pin.OUT)
led_23 = Pin(23, Pin.OUT)
buzzer_15 = Pin(15, Pin.OUT)


BUZZER = 'buzzer'
LED_22 = 'a'
LED_23 = 'b'

DEVICES = {
    BUZZER: buzzer_15,
    LED_22: led_22,
    LED_23: led_23,
}


def print_text(msg, x, y, clr):
    if clr:
        oled.fill(0)
    oled.text(msg, x, y)
    oled.show()


def activate_buzzer(_time=200):
    buzzer_15.on()
    time.sleep_ms(_time)
    buzzer_15.off()


def on_off_device(area, msg):
    led = DEVICES[area]

    if (msg.decode() == "on"):
        print('[INFO] Device: ON')
        led.on()
    if (msg.decode() == "off"):
        led.off()
        print('[INFO] Device: OFF')

    activate_buzzer()


def form_sub(topic, msg):
    if topic.decode() == node+BUZZER:
        on_off_device(BUZZER, msg)

    if topic.decode() == node+LED_22:
        on_off_device(LED_22, msg)

    if topic.decode() == node+LED_23:
        on_off_device(LED_23, msg)

    print("[INFO] Recivido de:", (topic.decode(), msg.decode()))


def Conexion_MQTT():
    client_id = ubinascii.hexlify(unique_id())
    mqtt_server = ''
    port_mqtt = 1883
    # Si su servidor no necesita usuario escribe None sin comillas
    user_mqtt = ''
    # Si su servidor no necesita contraseña escribe None sin comillas
    pswd_mqtt = ''
    client = MQTTClient(client_id, mqtt_server,
                        port_mqtt, user_mqtt, pswd_mqtt)
    client.set_callback(form_sub)
    client.connect()
    client.subscribe(b'')

    #print_text('Conectado a %s' % mqtt_server, 20, 30, 0)
    print_text('MQTT:%s' % mqtt_server, 2, 40, 0)
    led_2.on()
    return client

# Reinicia la conexión de MQTT


def Reinciar_conexion():
    led_2.off()
    print('Fallo en la conexion. Intentando de nuevo...')
    time.sleep(10)
    machine.reset()


wlan = network.WLAN(network.STA_IF)
wlan.active(True)  # Activa el Wifi
wlan.connect(ssid, password)  # Hace la conexión

while wlan.isconnected() == False:  # Espera a que se conecte a la red
    print_text('...', 20, 20, 1)

print_text('WiFi: %s' % ssid, 2, 20, 0)
print_text(wlan.ifconfig()[0], 2, 30, 0)


try:
    client = Conexion_MQTT()
except OSError as e:
    Reinciar_conexion()


last_message = 0
message_interval = 3
counter = 0

while True:
    try:
        client.check_msg()

        if (time.time() - last_message) > message_interval:
            msg = b'Counter: %d' % counter
            client.publish('', msg)
            last_message = time.time()
            counter += 1
            led_23.on()
            time.sleep_ms(50)
        else:
            led_23.off()
    except OSError as e:
        Reinciar_conexion()