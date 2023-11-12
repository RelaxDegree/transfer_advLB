import math
import random


class AbstractVector:
    def __init__(self, *args):
        self.alpha = None
        self.w = None
        self.b = None
        self.l = None
        self.phi = None

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, size):
        pass

    def clip(self, image):
        image_height, image_width = image.size[0], image.size[1]
        if self.phi >= 750:
            self.phi = 750
        if self.phi <= 380:
            self.phi = 380
        if self.l >= math.pi / 2:
            self.l = round(self.l, 5)
            self.l -= int(self.l / math.pi + 0.5) * math.pi
            self.l = round(self.l, 5)
        if self.l <= -math.pi / 2:
            self.l = round(self.l, 5)
            self.l += -int(self.l / math.pi - 0.5) * math.pi
            self.l = round(self.l, 5)
        if self.b < 0:
            self.b = 0
        if self.b > image_height:
            self.b = image_height
        if self.w < 10:
            self.w = 10
        if self.alpha < 0:
            self.alpha = 0
        if self.alpha > 0.7:
            self.alpha = 0.7

    def print(self):
        print('[makeLB phi]', end=' ')
        print(self.phi)
        print('[makeLB l]', end=' ')
        print(self.l)
        print('[makeLB b]', end=' ')
        print(self.b)
        print('[makeLB w]', end=' ')
        print(self.w)
        print('[makeLB alpha]', end=' ')
        print(self.alpha)

    @staticmethod
    def pickQ(S):
        pass

    def factory(self, *args):
        pass
