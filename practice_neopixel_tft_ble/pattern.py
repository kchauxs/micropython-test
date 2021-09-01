import time
import neopixel
import machine


class Patterns():

    def __init__(self, np, e):
        self.np = np
        self.n = np.n
        self.e = e
        self.reverse = False

    def cycle(self, color):
        for i in range(1 * self.n):
            for j in range(self.n):
                self.np[j] = (0, 0, 0)
            self.np[i % self.n] = color
            self.np.write()
            time.sleep_ms(self.e)

    def bounce(self, color):
        for i in range(1 * self.n):
            for j in range(self.n):
                self.np[j] = color
            if (i // self.n) % 2 == 0:
                self.np[i % self.n] = (0, 0, 0)
            else:
                self.np[self.n - 1 - (i % self.n)] = (0, 0, 0)
            self.np.write()
            time.sleep_ms(self.e)

    def fade(self, color=None):
        for i in range(0, 4 * 256, 8):
            for j in range(self.n):
                if (i // 256) % 2 == 0:
                    val = i & 0xff
                else:
                    val = 255 - (i & 0xff)
                self.np[j] = (val, 0, 0)
                self.np.write()

    def all(self, color):
        for i in range(self.n):
            self.np[i] = color
        self.np.write()

    def clear(self, color=None):
        for i in range(self.n):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def sweep(self, color):
        self.reverse = not self.reverse
        for i in range(self.n):
            if not self.reverse:
                j = i % self.n
            else:
                j = ((self.n - 1) - i) % self.n

            self.np[j] = color
            time.sleep_ms(25)
            self.np.write()
        self.clear(None)

    def pyramid(self, color):
        for i in range(self.n//2):
            j = (self.n // 2) + i
            k = (self.n // 2) - i

            if j % 2 == 0 and k % 2 == 0:
                self.np[j] = color
                self.np[k] = color
            else:
                self.np[j] = (255, 255, 255)
                self.np[k] = (255, 255, 255)

            self.np.write()
            time.sleep_ms(50)

        self.clear(None)

    def presentation(self, color=None):
        self.sweep((0, 0, 255))
        time.sleep_ms(500)
        self.sweep((255, 0, 0))
        time.sleep_ms(500)
        self.all((255, 255, 255))
        time.sleep_ms(700)
        self.clear(None)
        self.pyramid(color)
        time.sleep_ms(500)

    def intermittent(self, color):
        self.all(color)
        time.sleep_ms(500)
        self.clear()

    def select_pattern(self, pattern):

        if pattern == 'cycle':
            return self.cycle
        if pattern == 'bounce':
            return self.bounce
        if pattern == 'all':
            return self.all
        if pattern == 'fade':
            return self.fade
        if pattern == 'sweep':
            return self.sweep
        if pattern == 'pyramid':
            return self.pyramid
        if pattern == 'presentation':
            return self.presentation
        if pattern == 'clear':
            return self.clear


if __name__ == '__main__':
    np = neopixel.NeoPixel(machine.Pin(13), 60)

    p = Patterns(np, 5)
    for _ in range(5):
        p.select_pattern('sweep')((255, 0, 0))
