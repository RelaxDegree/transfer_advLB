import random
import time
from SMLB.smlb import SMLB
from utils.utils import write_log
from laser.laser import makeLB

savefilename = 'adv/'


class KR(SMLB):
    threshold = 0.02
    change_threshold = 0.0

    def getAdvLB(self, **kwargs):
        open_time = time.time()
        image, S, tmax, k = kwargs['image'], kwargs['S'], kwargs['tmax'], kwargs['k']
        if 'theta' not in kwargs.keys():
            theta = self.vectorApi.factory(image)  # Initialization theta
        else:
            theta = kwargs['theta']
        label, conf_ = self.modelApi.get_conf(image)[0]  # conf* <- fy(x)
        times = 0
        print('[kr开始] label:%s conf:%f' % (label, conf_))
        for i in range(k):  # for i = 1 to k do
            conf = conf_
            conf_before = conf
            # for t in range(tmax):  # for t = 1 to tmax do
            while True:  # 算法改进，不再固定迭代次数，而是在置信不再变化时停止
                times += 1
                if times % 50 == 0:
                    print('[kr %d]' % times)
                if times % (2 * S) == 0:
                    if conf_before == conf:
                        theta = self.vectorApi.factory(image)  # Initialization theta
                        print('[kr 重置theta]')
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
                conf1 = self.modelApi.get_y_conf(image1, label)  # conf <- fy(xl_theta)
                flg = False
                if conf > conf1 + self.change_threshold:  # if conf >= conf* then
                    theta = theta1  # theta <- theta'
                    conf = conf1  # conf* <- conf
                    print('[kr 更新置信 +：]' + str(conf1))
                    flg = True
                conf2 = self.modelApi.get_y_conf(image2, label)
                if conf > conf2 + self.change_threshold:  # if conf >= conf* then
                    theta = theta2
                    conf = conf2
                    print('[kr 更新置信 -：]' + str(conf2))
                    flg = True
                res_image = makeLB(theta, image)
                # print("[advLB]")
                argmax, now_conf = self.modelApi.get_conf(res_image)[0]
                # if conf < 0.1 and flg:
                #     flg = False
                #     res_image.show()
                #     print(self.modelApi.get_conf(res_image))
                if argmax != label and now_conf > conf + self.threshold:  # if argmax != label then
                    msg = "源标签标签%s\n被误分类为%s" % (label, argmax)
                    print("[kr LB]" + msg)
                    write_log(label, argmax, theta, conf_before, conf, times, self.modelApi.name)
                    saveFile = savefilename + str(label) + '--' + str(argmax) + '--' + str(conf) + '.jpg'
                    print(
                        "[kr LB] 参数 波长:%f 位置:(%f %f) 宽度:%f 强度:%f" % (theta.phi, theta.q1, theta.q2, theta.w, theta.alpha))
                    # res_image.show()
                    res_image.save(saveFile)
                    # image.save(savefilename + str(label) + '原图.jpg')
                    return theta, times, argmax, msg  # return theta

        print("[kr LB] 未找到对抗样本")
        close_time = time.time()
        print("[kr LB] 耗时%f, 平均一次查询时间为 %f ms" % (close_time - open_time, (close_time - open_time) / times * 1000))
        return None, times,None, None
