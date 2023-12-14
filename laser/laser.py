import numpy as np
import math
from PIL import Image
import cv2
from utils.utils import *


def simple_add(base_img, light_pattern, alpha=1.0):
    light_pattern = light_pattern.astype(np.float32)
    resized_light_pattern = cv2.resize(light_pattern, (base_img.shape[1], base_img.shape[0]))
    c = cv2.addWeighted(base_img, 0.7, resized_light_pattern, alpha * 3, 0)
    return c


def gaussian_add(base_img, light_pattern, eps=128):
    base_img = base_img.astype(np.float32)
    resized_light_pattern = cv2.resize(light_pattern, (base_img.shape[1], base_img.shape[0]))
    mu, sigma = 0, 1.0  # mean and standard deviation
    s = np.random.normal(mu, sigma, base_img.shape)
    gaussian_matric = np.clip(s * eps * (resized_light_pattern / 255.0), -1 * eps, eps)
    print(np.amax(gaussian_matric))
    c = base_img + gaussian_matric
    return c


def tube_light_generation_by_func(k, b, alpha, beta, wavelength, w=400, h=400):
    full_light_end_y = int(math.sqrt(beta) + 0.5)
    light_end_y = int(math.sqrt(beta * 20) + 0.5)
    c = wavelength_to_rgb(wavelength)
    t = math.sqrt(1 + k * k)
    c0 = c[0] * alpha
    c1 = c[1] * alpha
    c2 = c[2] * alpha
    x_coords = np.arange(w)
    y_coords = np.arange(h)

    # Create 2D grid of x and y coordinates
    x_grid, y_grid = np.meshgrid(x_coords, y_coords)

    # Calculate distances for all x and y coordinates in one go
    distances = np.abs(k * x_grid - y_grid + b) / t

    # Create 3D array to represent tube_light, initially filled with zeros
    tube_light = np.zeros((h, w, 3))

    # Full light condition
    full_light_mask = distances <= full_light_end_y
    tube_light[full_light_mask, 0] = c0
    tube_light[full_light_mask, 1] = c1
    tube_light[full_light_mask, 2] = c2

    # Attenuation condition
    attenuation_mask = (full_light_end_y < distances) & (distances <= light_end_y)
    # if distances == 0:
    #     attenuation = 1
    # else:
    attenuation = beta / (distances * distances)
    tube_light[attenuation_mask, 0] = c0 * attenuation[attenuation_mask]
    tube_light[attenuation_mask, 1] = c1 * attenuation[attenuation_mask]
    tube_light[attenuation_mask, 2] = c2 * attenuation[attenuation_mask]

    return tube_light


def makeLB(vector, image):
    k = round(math.tan(vector.l), 2)
    b = vector.b
    alpha = vector.alpha
    wl = vector.phi
    beta = vector.w

    tube_light = tube_light_generation_by_func(k, b, alpha=alpha, beta=beta, wavelength=wl, w=image.size[0],
                                               h=image.size[1])

    img = np.asarray(image.convert('RGB'), dtype=np.float32)
    img_with_light = simple_add(img, tube_light * 255.0, alpha)
    img_with_light = np.clip(img_with_light, 0.0, 255.0)
    result = Image.fromarray(np.uint8(img_with_light))

    return result

# root = '../valdata/'
#
# image = Image.open('stop.jpg')
# theta = Vector(image)
# theta.alpha = 0.8
# theta.b = 110
# theta.phi = 400
# theta.l = math.pi / 3
# im = makeLB(theta, image)
# im.show()
