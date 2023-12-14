import os
import random
from SMLB.pso_transfer import TPSO
from SMLB.pso import PSO

from PIL import Image
from utils.utils import test_log
from SMLB.k_restart import KR
from SMLB.pso import PSO
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
root = 'E:\pythonProject\\nips2017\\images'
random.seed(3407)
data_root = 'dataset/'


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
def testOne(filename, model, times, dataset='nips-2017'):
    vct = Vector()
    atk_kr = KR(mbv2, vct)

    atk = PSO(mbv2, vct)
    suc_times = 0
    suc_num = 0
    file_list = os.listdir(filename)

    for _ in range(times):
        img_name = random.choice(file_list)
        # if _  == 4 or _ == 6:
        #     continue
        # img_name = 'n0274717700001290.jpg'
        img = Image.open(root + '\\' + img_name)
        # theta, atk_times = atk.getAdvLB(image=img, S=30, tmax=100, k=10)
        theta, atk_times = atk.getAdvLB(image=img, num_particles=30, inertia_weight=0.02, cognitive_weight=1.4,
                                        social_weight=1.4, max_iterations=100)
        if atk_times == -1:
            theta, atk_times = atk_kr.getAdvLB(image=img, S=30, tmax=100, k=3, theta=theta)
            if theta is None:
                print('攻击失败')
                continue
        suc_times += atk_times
        suc_num += 1
        print('攻击成功 查询次数 %d' % (suc_times / suc_num))
        img.save('dataset/' + img_name)
    test_log(model=model, method='pso', dateset=dataset, suc_num=suc_num, suc_times=suc_times, times=times)


def testTransfer(filename, model, times=1, dataset='nips-2017'):
    vct = Vector()
    atker = TKR(mbv2, vct)
    # atker = TPSO(mbv2, vct)
    atker.setModels([rn50, dn121])
    # atker.setModels([rn50, mbv2, dn121, vit_b, swin])

    suc_times = 0
    suc_num = 0
    for _ in range(times):

        file_list = os.listdir(filename)
        img_name = random.choice(file_list)
        # img_name = '2.jpg'
        img = Image.open(root + '\\' + img_name)
        # if _ < 5:
        #     continue
        theta, atk_times = atker.getAdvLB(image=img, S=30, tmax=100, k=10)
        # theta, atk_times = atker.getAdvLB(image=img, num_particles=30, inertia_weight=0.4, cognitive_weight=1.4, social_weight=1.4,max_iterations=100)

        if theta is None:
            print('攻击失败')
        else:
            suc_times += atk_times
            suc_num += 1
            print('攻击成功 平均查询次数 %d' % (suc_times / suc_num))
    test_log(model=model, method='pso', dateset=dataset, suc_num=suc_num, suc_times=suc_times, times=times)


testOne(root, 'mbv2', 100)


# testTransfer(data_root, 'mbv2',10)


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
