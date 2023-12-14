import time
import random

from SMLB.smlb import SMLB
from utils.utils import write_log
from laser.laser import makeLB

savefilename = 'tdata/'


class TKR(SMLB):
    threshold = 0
    change_threshold = 0.0000001

    def setModels(self, modelApis):
        for api in modelApis:
            self.modelApis.append(api)

    def getFitness(self, img, label):
        fitness = 0
        for api in self.modelApis:
            score = api.get_y_conf(img, label)
            # print(api.name, score)
            fitness += score
        return fitness / len(self.modelApis)

    def showTransfer(self, img, label):
        lst = []
        for api in self.modelApis:
            score = api.get_y_conf(img, label)
            lst.append((api.name, score))
        return lst

    def isEnd(self, image, label):
        for api in self.modelApis:
            if api.get_conf(image)[0][0] == label:
                return False
        return True

    def getAdvLB(self, **kwargs):
        open_time = time.time()
        image, S, tmax, k = kwargs['image'], kwargs['S'], kwargs['tmax'], kwargs['k']
        label = self.modelApi.get_conf(image)[0][0]  # conf* <- fy(x)
        conf_ = self.getFitness(image, label)
        times = 0
        print('[adv开始] label:%s conf:%f' % (label, conf_))
        for i in range(k):  # for i = 1 to k do
            theta = self.vectorApi.factory(image)  # Initialization theta
            conf = conf_
            conf_before = conf
            # for t in range(tmax):  # for t = 1 to tmax do
            while True:  # 算法改进，不再固定迭代次数，而是在置信不再变化时停止
                times += 1
                if times % (5 * S) == 0:
                    if conf_before == conf:
                        break
                    else:
                        conf_before = conf
                q = self.vectorApi.pickQ(S)
                theta1 = theta + self.vectorApi.factory(q)  # theta' <- theta ± q
                theta2 = theta - self.vectorApi.factory(q)
                theta1.clip(image)  # theta' <- clip(theta', emin, emax)
                theta2.clip(image)
                image1 = makeLB(theta1, image)
                image2 = makeLB(theta2, image)
                conf1 = self.getFitness(image1, label)  # conf <- fy(xl_theta)
                if conf > conf1 + self.change_threshold:  # if conf >= conf* then
                    theta = theta1  # theta <- theta'
                    conf = conf1  # conf* <- conf
                    print('[adv 更新置信 +：]' + str(conf1))
                conf2 = self.getFitness(image2, label)
                if conf > conf2 + self.change_threshold:  # if conf >= conf* then
                    theta = theta2
                    conf = conf2
                    print('[adv 更新置信 -：]' + str(conf2))
                res_image = makeLB(theta, image)
                # print("[advLB]")
                # argmax, now_conf = self.modelApi.get_conf(res_image)[0]
                # if argmax != label and now_conf > conf + self.threshold:  # if argmax != label then
                if self.isEnd(res_image, label):
                    argmax, now_conf = self.modelApi.get_conf(res_image)[0]
                    if label == argmax:
                        print("[advTLB] 对抗样本无效")
                        return None, times
                    write_log(label, argmax, theta, conf_before, conf, times)
                    print("[advLB] 标签%s被攻击为%s" % (label, argmax))
                    saveFile = savefilename + str(label) + '--' + str(argmax) + '--' + str(conf) + '.jpg'
                    print(
                        "[advLB] 参数 波长:%f 位置:(%f %f) 宽度:%f 强度:%f" % (theta.phi, theta.l, theta.b, theta.w, theta.alpha))
                    res_image.save(saveFile)
                    image.save(savefilename + str(label) + '原图.jpg')
                    close_time = time.time()
                    print("[advLB] 迁移性信息" + str(self.showTransfer(res_image, label)))
                    print("[advLB] 目标模型检测为%s, 置信度%f" % (argmax, now_conf))
                    print("[advLB] 耗时%f, 平均一次查询时间为 %f ms" % (
                        close_time - open_time, (close_time - open_time) / times * 1000))
                    return theta, times  # return theta

        print("[advLB] 攻击失败")
        close_time = time.time()
        print("[advLB] 耗时%f, 平均一次查询时间为 %f ms" % (close_time - open_time, (close_time - open_time) / times * 1000))
        return None, times
