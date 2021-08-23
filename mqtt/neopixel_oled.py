# Librerias
import time
import esp32
import machine
import network
import _thread
import neopixel
import ssd1306
import ubinascii
from machine import unique_id, Pin
from umqttsimple import MQTTClient


# DISPLAY
scl = machine.Pin(19, machine.Pin.OUT, machine.Pin.PULL_UP)
sda = machine.Pin(21, machine.Pin.OUT, machine.Pin.PULL_UP)
i2c = machine.SoftI2C(scl=scl, sda=sda, freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
# WIFI
ssid = 'Kevin'  # Nombre de la Red
password = 'nqs4085A'  # Contraseña de la red
# MQTT
root_topic = 'hG6NETWFkyoklYw'
subtopic = 'devices'
node = root_topic + '/' + subtopic + '/'
# LEDS
led_2 = Pin(2, Pin.OUT)
np = neopixel.NeoPixel(machine.Pin(13), 60)
buzzer = Pin(26, Pin.OUT)
color = (0, 255, 0)
pattern = 'all'


def activate_buzzer(_time=200):
    buzzer.on()
    time.sleep_ms(_time)
    buzzer.off()


def print_text(msg, x, y, clr):
    if clr:
        oled.fill(0)
    oled.text(msg, x, y)
    oled.show()


def change_color(msg):
    global color
    msg = str(msg.decode()).lstrip('#')
    color = tuple(int(msg[i:i+2], 16) for i in (0, 2, 4))
    # activate_buzzer()


def change_pattern(msg):
    global pattern
    msg = str(msg.decode())
    if len(msg) != 0:
        pattern = msg
        # activate_buzzer()


def form_sub(topic, msg):
    if topic.decode() == node+'rgb':
        change_color(msg)

    if topic.decode() == node+'pattern':
        change_pattern(msg)

    print("[INFO] Recivido de:", (topic.decode(), msg.decode()))


def Conexion_MQTT():
    client_id = ubinascii.hexlify(unique_id())
    mqtt_server = 'ioticos.org'
    port_mqtt = 1883
    # Si su servidor no necesita usuario escribe None sin comillas
    user_mqtt = '4kwXM81rCJ0NAbj'
    # Si su servidor no necesita contraseña escribe None sin comillas
    pswd_mqtt = 'yfp14kGTueiG3CL'
    client = MQTTClient(client_id, mqtt_server,
                        port_mqtt, user_mqtt, pswd_mqtt)
    client.set_callback(form_sub)
    client.connect()
    client.subscribe(b'hG6NETWFkyoklYw/devices/#')

    #print('Conectado a %s' % mqtt_server, 20, 30, 0)
    print('MQTT:%s' % mqtt_server)
    led_2.on()
    return client

# Reinicia la conexión de MQTT


def Reinciar_conexion():
    led_2.off()
    print('Fallo en la conexion. Intentando de nuevo...')
    time.sleep(10)
    machine.reset()


def patterns(e):
    n = np.n

    if pattern == 'cycle':
        for i in range(1 * n):
            for j in range(n):
                np[j] = (0, 0, 0)
            np[i % n] = color
            np.write()
            time.sleep_ms(e)

    if pattern == 'bounce':
        for i in range(1 * n):
            for j in range(n):
                np[j] = color
            if (i // n) % 2 == 0:
                np[i % n] = (0, 0, 0)
            else:
                np[n - 1 - (i % n)] = (0, 0, 0)
            np.write()
            time.sleep_ms(e)

    if pattern == 'fade':
        for i in range(0, 4 * 256, 8):
            for j in range(n):
                if (i // 256) % 2 == 0:
                    val = i & 0xff
                else:
                    val = 255 - (i & 0xff)
                np[j] = (val, 0, 0)
            np.write()

    if pattern == 'clear':
        for i in range(n):
            np[i] = (0, 0, 0)
        np.write()

    if pattern == 'all':
        for i in range(n):
            np[i] = color
        np.write()


def start_leds(e):
    while 1:
        patterns(e)


def show_on_display(e):
    while 1:
        oled.fill(0)
        oled.text('Pattern:'+pattern, 10, 5)
        oled.text('RGB: ('+str(color[0])+',' +
                str(color[1])+','+str(color[2])+')', 1, 30)
        oled.show()
        time.sleep_ms(e)



def fahrenhei_celsius(x):
    return str(round((x-32)*(5/9)))


if __name__ == '__main__':

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)  # Activa el Wifi
    wlan.connect(ssid, password)  # Hace la conexión

    while wlan.isconnected() == False:  # Espera a que se conecte a la red
        print_text('....', 20, 30, 1)

    print('WiFi: %s' % ssid)
    print(wlan.ifconfig())

    try:
        client = Conexion_MQTT()
    except OSError as e:
        Reinciar_conexion()

    _thread.start_new_thread(start_leds, (25,))
    _thread.start_new_thread(show_on_display, (25,))

    while True:
        try:
            client.check_msg()
            time.sleep_ms(25)

        except OSError as e:
            Reinciar_conexion()