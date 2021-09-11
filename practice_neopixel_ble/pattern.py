import time
import neopixel
import machine


class Patterns():

    def __init__(self, np, color, sleep, pattern):
        self.np = np
        self.n = np.n
        self.sleep = sleep
        self.reverse = False
        self.color = color
        self.pattern = pattern

    def cycle(self):
        for i in range(1 * self.n):
            for j in range(self.n):
                self.np[j] = (0, 0, 0)
            self.np[i % self.n] = self.color
            self.np.write()
            time.sleep_ms(self.sleep)

    def bounce(self):
        for i in range(1 * self.n):
            for j in range(self.n):
                self.np[j] = self.color
            if (i // self.n) % 2 == 0:
                self.np[i % self.n] = (0, 0, 0)
            else:
                self.np[self.n - 1 - (i % self.n)] = (0, 0, 0)
            self.np.write()
            time.sleep_ms(self.sleep)

    def fade(self):
        for i in range(0, 4 * 256, 8):
            for j in range(self.n):
                if (i // 256) % 2 == 0:
                    val = i & 0xff
                else:
                    val = 255 - (i & 0xff)
                self.np[j] = (val, 0, 0)
                self.np.write()

    def all(self):
        for i in range(self.n):
            self.np[i] = self.color
        self.np.write()

    def clear(self):
        for i in range(self.n):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def sweep(self):
        self.reverse = not self.reverse
        for i in range(self.n):
            if not self.reverse:
                j = i % self.n
            else:
                j = ((self.n - 1) - i) % self.n

            self.np[j] = self.color
            time.sleep_ms(25)
            self.np.write()
        self.clear()

    def pyramid(self):
        for i in range(self.n//2):
            j = (self.n // 2) + i
            k = (self.n // 2) - i

            if j % 2 == 0 and k % 2 == 0:
                self.np[j] = self.color
                self.np[k] = self.color
            else:
                self.np[j] = (255, 255, 255)
                self.np[k] = (255, 255, 255)

            self.np.write()
            time.sleep_ms(50)

        self.clear()

    def presentation(self):
        self.sweep((0, 0, 255))
        time.sleep_ms(500)
        self.sweep((255, 0, 0))
        time.sleep_ms(500)
        self.all((255, 255, 255))
        time.sleep_ms(700)
        self.clear()
        self.pyramid()
        time.sleep_ms(500)

    def intermittent(self):
        self.all()
        time.sleep_ms(500)
        self.clear()
        time.sleep_ms(500)

    def select_pattern(self):
        if self.pattern == 'cycle':
            return self.cycle
        if self.pattern == 'bounce':
            return self.bounce
        if self.pattern == 'all':
            return self.all
        if self.pattern == 'fade':
            return self.fade
        if self.pattern == 'sweep':
            return self.sweep
        if self.pattern == 'pyramid':
            return self.pyramid
        if self.pattern == 'presentation':
            return self.presentation
        if self.pattern == 'clear':
            return self.clear
        if self.pattern == 'intermittent':
            return self.intermittent


if __name__ == '__main__':
    np = neopixel.NeoPixel(machine.Pin(13), 60)

    p = Patterns(np, (255, 0, 0), 5, 'sweep')
    while 1:
        p.select_pattern()()
