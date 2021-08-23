import time
import machine, neopixel

def demo(np, pattern='cycle'):
    n = np.n

    if pattern == 'cycle':
        for i in range(1 * n):
            for j in range(n):
                np[j] = (0, 0, 0)
            np[i % n] = (255, 255, 255)
            np.write()
            time.sleep_ms(25)

    if pattern == 'bounce':
        for i in range(1 * n):
            for j in range(n):
                np[j] = (0, 0, 128)
            if (i // n) % 2 == 0:
                np[i % n] = (0, 0, 0)
            else:
                np[n - 1 - (i % n)] = (0, 0, 0)
            np.write()
            time.sleep_ms(25)

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

if __name__ == '__main__':
    np = neopixel.NeoPixel(machine.Pin(13), 60)
    demo(np,'fade')
