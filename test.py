import os
import random
from SMLB.pso_transfer import TPSO
from SMLB.pso import PSO

from PIL import Image
from utils.utils import test_log
from SMLB.k_restart import KR
from SMLB.kr_transfer import TKR
from model.rn50 import Rn50
from model.mbv2 import Mbv2
from model.dn121 import Dn121
from model.swin import Swin_b
from model.vitB import Vit_b
from laser.Vector import Vector

rn50 = Rn50()
mbv2 = Mbv2()
dn121 = Dn121()
vit_b = Vit_b()
swin = Swin_b()
root = 'E:\pythonProject\\mini-imagenet'


# img = Image.open("3.jpg")

# print(dn121.get_conf(img))
# print(rn50.get_conf(img))
# print(mbv2.get_conf(img))
# print(vit_b.get_conf(img))
# print(swin.get_conf(img))
# pt = TPSO(mbv2, Vector)
# pt = PSO(mbv2, Vector)
# pt.setModels([rn50, mbv2, dn121, vit_b, swin])
# pt.getAdvLB(num_particles=30, max_iterations=100, image=img, inertia_weight=0.4, cognitive_weight=1, social_weight=1)
def testOne(filename, model):
    vct = Vector()
    kr = KR(dn121, vct)
    suc_times = 0
    suc_num = 0
    file_list = os.listdir(filename)
    img_name = random.choice(file_list)
    img = Image.open(root + '\\' + img_name)
    theta, atk_times = kr.getAdvLB(image=img, S=10, tmax=100, k=10)
    if theta is None:
        print('攻击失败')
    else:
        suc_times += atk_times
        suc_num += 1
        print('攻击成功 查询次数 %d' % (suc_times / suc_num))
    test_log(model=model, method='kr', dateset='mini-imagenet', suc_num=suc_num, suc_times=suc_times, times=1)


testOne(root, 'dn121')


def testTransfer(filename, model):
    vct = Vector()
    kr = TKR(mbv2, vct)
    kr.setModels([rn50, dn121])
    # pt.setModels([rn50, mbv2, dn121, vit_b, swin])

    suc_times = 0
    suc_num = 0
    file_list = os.listdir(filename)
    img_name = random.choice(file_list)
    img = Image.open(root + '\\' + img_name)
    theta, atk_times = kr.getAdvLB(image=img, S=10, tmax=100, k=10)
    if theta is None:
        print('攻击失败')
    else:
        suc_times += atk_times
        suc_num += 1
        print('攻击成功 平均查询次数 %d' % ( suc_times / suc_num))
    test_log(model=model, method='kr', dateset='mini-imagenet', suc_num=suc_num, suc_times=suc_times, times=1)


# testTransfer(1, root, 'vit_b')


def testAll(filename, model):
    vct = Vector()
    kr = KR(rn50, vct)
    suc_times = 0
    times = 0
    suc_num = 0
    file_list = os.listdir(filename)
    print(len(file_list))
    for img_name in file_list:
        theta, atk_times = kr.getAdvLB(image=Image.open(root + '\\' + img_name), S=10, tmax=100, k=10)
        times += atk_times
        if theta is None:
            print('攻击失败')
        else:
            suc_times += atk_times
            suc_num += 1
            print('攻击成功')
    test_log(model=model, method='kr', dateset='mini-imagenet', suc_num=suc_num, suc_times=suc_times, times=times)
