import math
import random

from PIL import Image
import PIL


# 固定了波长、宽度和光强
class Cons_Vector:
    phi = 445
    w = 30
    alpha = 1.0
    # basic
    Q = [
        [0, 0.01, 0, 0, 0],  # l
        [0, 0, 1, 0, 0],  # b
    ]

    def set_laser(self, phi_, w_, alpha_):
        self.phi = phi_
        self.w = w_
        self.alpha = alpha_

    def __init__(self, *args):
        if len(args) == 1 and not isinstance(args[0], list):
            if isinstance(args[0], PIL.Image.Image):
                image_height = args[0].size[0]
            else:
                image_height = args[0].shape[0]
            self.l = random.uniform(-math.pi + 0.1, math.pi / 2 - 0.1)
            self.l = round(self.l, 5)
            self.b = random.uniform(image_height / 5, image_height * 4 / 5)
        elif len(args) == 1 and isinstance(args[0], list):
            self.l = args[0][1]
            self.b = args[0][2]
        elif len(args) == 5:
            self.phi = args[0]
            self.l = args[1]
            self.b = args[2]
            self.w = args[3]
            self.alpha = args[4]

    # def __init__(self, phi, l, b, w, alpha):
    #     self.phi = phi
    #     self.l = l
    #     self.b = b
    #     self.w = w
    #     self.alpha = alpha
    def __add__(self, other):
        try:
            return Cons_Vector(self.phi, self.l + other.l, self.b + other.b, self.w, self.alpha)
        except:
            self.print()
            other.print()

    def __sub__(self, other):
        try:
            return Cons_Vector(self.phi, self.l - other.l, self.b - other.b, self.w,
                               self.alpha)
        except:
            self.print()
            other.print()

    def __mul__(self, size):
        return Cons_Vector(self.phi, self.l * size, self.b * size, self.w, self.alpha)

    def clip(self, image):
        super().clip(image)

    def print(self):
        super().print()

    @staticmethod
    def pickQ(S):
        q = random.choice(Cons_Vector.Q).copy()  # random pick q ∈ Q, s ∈ S
        size = random.randint(2, S)
        for dim in range(2):  # q <- q * s
            q[dim] = round(q[dim] * size, 5)
        return q

    def factory(self, *args):
        if len(args) == 1 and not isinstance(args[0], list):
            if isinstance(args[0], PIL.Image.Image):
                image_height = args[0].size[0]
            else:
                image_height = args[0].shape[0]
            self.l = random.uniform(-math.pi + 0.1, math.pi / 2 - 0.1)
            self.l = round(self.l, 5)
            self.b = random.uniform(image_height / 5, image_height * 4 / 5)
        elif len(args) == 1 and isinstance(args[0], list):
            self.l = args[0][1]
            self.b = args[0][2]
        elif len(args) == 5:
            self.phi = args[0]
            self.l = args[1]
            self.b = args[2]
            self.w = args[3]
            self.alpha = args[4]
