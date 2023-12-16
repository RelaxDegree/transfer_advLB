import math
import random


class AbstractVector:
    def __init__(self, *args):
        self.alpha = None
        self.w = None
        self.q1 = None
        self.q2 = None
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
        if self.q1 >= 1:
            self.q1 = 1
        if self.q1 <= 0:
            self.q1 = 0
        if self.q2 >= 1:
            self.q2 = 1
        if self.q2 <= 0:
            self.q2 = 0
        if self.w < 10:
            self.w = 10
        if self.alpha < 0:
            self.alpha = 0
        if self.alpha > 0.7:
            self.alpha = 0.7

    def print(self):
        print('[makeLB phi]', end=' ')
        print(self.phi)
        print('[makeLB q1]', end=' ')
        print(self.q1)
        print('[makeLB q2]', end=' ')
        print(self.q2)
        print('[makeLB w]', end=' ')
        print(self.w)
        print('[makeLB alpha]', end=' ')
        print(self.alpha)

    @staticmethod
    def pickQ(S):
        pass

    def factory(self, *args):
        pass

    def particleFactory(self, image, samples):
        pass