import time
import neopixel
import machine

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



    def sweep(self,color,reverse = False):
        for i in range(self.n):
            if not reverse:
                j = i % self.n 
            else:
                j = ((self.n - 1)- i) % self.n

            self.np[j] = color
            time.sleep_ms(25)
            self.np.write()

    def pyramid(self):
        for i in range(self.n//2):
            j = (self.n // 2) + i
            k = (self.n // 2) - i

            if j % 2 == 0 and k % 2 == 0:
                self.np[j] = (255, 0, 0)
                self.np[k] = (255, 0, 0)
            else:
                self.np[j] = (0, 0, 255)
                self.np[k] = (0, 0, 255)

            time.sleep_ms(250)
            self.np.write()


    def presentation(self):
        self.sweep((0, 0, 255),False)
        self.clear()
        time.sleep_ms(500)
        self.sweep((255, 0, 0),True)
        self.clear()
        time.sleep_ms(500)
        self.all((255, 255, 255))
        time.sleep_ms(700)
        self.clear() 
        self.pyramid()
        self.clear()
        time.sleep_ms(500)
        
if __name__ == '__main__':
    np = neopixel.NeoPixel(machine.Pin(13), 60)

    p = Patterns(np,5)
    for _ in range(5):
        p.presentation()