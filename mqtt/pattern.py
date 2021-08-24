import time


class Patterns():

    def __init__(self, np, e):
        self.np = np
        self.n = np.n
        self.e = e

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

    def fade(self):
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

    def clear(self):
        for i in range(self.n):
            self.np[i] = (0, 0, 0)
        self.np.write()
