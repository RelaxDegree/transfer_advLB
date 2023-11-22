from SMLB.smlb import SMLB
import random
import math
from laser.Vector import Particle
import copy
from laser.laser import makeLB
from utils.utils import write_log
import matplotlib.pyplot as plt
import numpy as np


class TPSO(SMLB):
    threshold = 0.02

    def setHyperParams(self, **kwargs):
        self.num_particles = kwargs['num_particles']
        self.image = kwargs['image']
        self.inertia_weight = kwargs['inertia_weight']
        self.cognitive_weight = kwargs['cognitive_weight']
        self.social_weight = kwargs['social_weight']
        self.max_iterations = kwargs['max_iterations']
        self.particles = []
        self.label, self.conf = self.modelApi.get_conf(self.image)[0]
        self.fitness = 0
        self.atk_times = 0
        print('[adv开始] label:%s conf:%f' % (self.label, self.conf))

    def __init__(self, modelApi, vectorApi):
        super().__init__(modelApi, vectorApi)
        self.fitness = None
        self.num_particles = None
        self.image = None
        self.inertia_weight = None
        self.cognitive_weight = None
        self.social_weight = None
        self.max_iterations = None
        self.particles = None
        self.label = None
        self.conf = None
        self.atk_times = None

    def latin_hypercube_sampling(self, dimension, num_samples):
        # 生成初始的拉丁超立方采样矩阵
        initial_matrix = [[(i + random.random()) / num_samples for i in range(num_samples)] for _ in range(dimension)]

        # 对每一列进行随机置换
        for i in range(dimension):
            random.shuffle(initial_matrix[i])

        # 对每一列进行归一化，得到最终的拉丁超立方采样样本
        samples = [[initial_matrix[i][j] for i in range(dimension)] for j in range(num_samples)]
        return self.vectorApi.latin_transform(self.image, samples)

    def initialize_particles(self):
        # 生成拉丁超立方采样样本
        samples = self.latin_hypercube_sampling(5, self.num_particles)
        for i in range(self.num_particles):
            particle = Particle(self.image, samples[i])
            self.particles.append(particle)

    def update_global_best(self):
        global_best_fitness = float('-inf')
        global_best_theta = None
        for particle in self.particles:
            fitness = self.evaluate_fitness(particle.theta)
            if fitness > global_best_fitness:
                global_best_fitness = fitness
                global_best_theta = copy.deepcopy(particle.theta)
        print('[adv最低分数] fitness:%f' % global_best_fitness)

        return global_best_theta, global_best_fitness

    def evaluate_fitness(self, theta):
        image_new = makeLB(theta, self.image)
        fitness = 0
        for api in self.modelApis:
            conf = api.get_y_conf(image_new, self.label)
            fitness += 1 - conf
        fitness = math.e ** fitness
        return fitness

    def checkBlackBox(self, theta):
        image_new = makeLB(theta, self.image)
        self.atk_times += 1
        conf_list = self.modelApi.get_conf(image_new)
        argmax, conf_max = conf_list[0]
        conf_sec = conf_list[1][1]
        return argmax, conf_max, conf_sec

    def setModels(self, modelApis):
        for api in modelApis:
            self.modelApis.append(api)

    def getAdvLB(self, **kwargs):
        self.setHyperParams(**kwargs)
        self.initialize_particles()
        global_best_theta = self.update_global_best()[0]

        for _ in range(self.max_iterations):
            for particle in self.particles:
                particle.update_velocity(global_best_theta, self.inertia_weight, self.cognitive_weight,
                                         self.social_weight)
                particle.update_theta()

            global_best_theta = self.update_global_best()[0]

        argmax, conf_max, conf_sec = self.checkBlackBox(global_best_theta)
        if argmax != self.label:
            print('[advLB成功] label:%s conf:%f' % (argmax, conf_max))
            saveFile = 'adv/' + str(self.label) + '--' + str(argmax) + '--' + '.jpg'
            makeLB(global_best_theta, self.image).save(saveFile)
            write_log(self.label, argmax, global_best_theta, self.conf, conf_max, self.atk_times)
            return global_best_theta, self.atk_times
        else:
            print('[advLB失败] label:%s conf:%f' % (argmax, conf_max))
            saveFile = 'adv/' + str(self.label) + '--' + str(self.conf) + '.jpg'
            self.image.save(saveFile)
            return None, self.atk_times
