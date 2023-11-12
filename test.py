import os
import random

from PIL import Image

from SMLB.k_restart import KR
from model.rn50 import Rn50
from laser.Vector import Vector
rn = Rn50()
vct = Vector()
kr = KR(rn, vct)
root = 'E:\pythonProject\\mini-imagenet'
file_list = os.listdir(root)
img_name = random.choice(file_list)
kr.getAdvLB(image=Image.open(root + '\\' + img_name), S=10, tmax=100, k=10)
