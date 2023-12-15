import math
import random
from laser.AbstractVector import AbstractVector
from PIL import Image
import PIL

phi = 445
w = 30
alpha = 1.0

# 固定了波长、宽度和光强
class Cons_Vector(AbstractVector):
    # basic
    Q = [
        [0, 0.03, 0, 0, 0],  # l
        [0, 0, 5, 0, 0],  # b
    ]

    def set_laser(self, phi_, w_, alpha_):
        global phi, w, alpha
        phi = phi_
        w = w_
        alpha = alpha_
        print(phi, w, alpha)


    def __init__(self, *args):
        super().__init__(*args)
        self.phi = phi
        self.w = w
        self.alpha = alpha
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
        return Cons_Vector(self.phi, self.l, self.b, self.w, self.alpha)

    def particleFactory(self, image, samples):
        return Cons_Particle(image, samples)
    @staticmethod
    def latin_transform(img, samples):

        new_samples = []
        for sample in samples:
            sample[1] = -math.pi / 2 + math.pi * sample[1]
            sample[2] = img.size[1] * sample[2]
            new_samples.append(sample)

        return samples
        return new_samples


import copy


class Cons_Particle:
    def __init__(self, image, lst):
        self.theta = Cons_Vector(lst)
        self.velocity = random.choice(self.theta.Q).copy()
        self.best_theta = copy.copy(self.theta)
        self.image = image
        self.argmax = ''
        self.conf = 0
        self.conf_sec = 0

    def update_velocity(self, global_best_theta, inertia_weight, cognitive_weight, social_weight):
        for i in range(4):
            self.velocity[i] *= inertia_weight
        theta1 = (self.best_theta - self.theta) * cognitive_weight
        theta2 = (global_best_theta - self.theta) * social_weight
        self.velocity[1] += random.uniform(0, 1) * theta1.l + random.uniform(0, 1) * theta2.l
        self.velocity[2] += random.uniform(0, 1) * theta1.b + random.uniform(0, 1) * theta2.b

    def update_theta(self):
        self.theta.l += self.velocity[1]
        self.theta.b += self.velocity[2]
        self.theta.clip(self.image)
