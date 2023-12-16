from SMLB.smlb import SMLB
import random
import math
from laser.Vector import Particle
import copy
from laser.laser import makeLB
from utils.utils import write_log
import matplotlib.pyplot as plt
import numpy as np


class PSO(SMLB):
    threshold = 0.0

    def setHyperParams(self, **kwargs):
        self.num_particles = kwargs['num_particles']
        self.image = kwargs['image']
        self.inertia_weight_max = kwargs['inertia_weight_max']
        self.inertia_weight_min = kwargs['inertia_weight_min']
        self.cognitive_weight = kwargs['cognitive_weight']
        self.social_weight = kwargs['social_weight']
        self.max_iterations = kwargs['max_iterations']
        self.particles = []
        self.label, self.conf = self.modelApi.get_conf(self.image)[0]
        self.fitness = 0
        self.atk_times = 0
        self.best_theta = None
        self.best_conf = None
        print('[adv开始] label:%s conf:%f' % (self.label, self.conf))

    def __init__(self, modelApi, vectorApi):
        super().__init__(modelApi, vectorApi)
        self.fitness = None
        self.num_particles = None
        self.image = None
        self.inertia_weight = None
        self.inertia_weight_max = None
        self.inertia_weight_min = None
        self.cognitive_weight = None
        self.social_weight = None
        self.max_iterations = None
        self.particles = None
        self.label = None
        self.conf = None
        self.atk_times = None
        self.best_theta = None
        self.best_conf = None

    def latin_hypercube_sampling(self, dimension, num_samples):
        # 生成初始的拉丁超立方采样矩阵
        initial_matrix = [[(i + random.random()) / num_samples for i in range(num_samples)] for _ in range(dimension)]

        # 对每一列进行随机置换
        for i in range(dimension):
            random.shuffle(initial_matrix[i])

        # 对每一列进行归一化，得到最终的拉丁超立方采样样本
        samples = [[initial_matrix[i][j] for i in range(dimension)] for j in range(num_samples)]
        return samples

    def initialize_particles(self):
        # 生成拉丁超立方采样样本
        samples = self.latin_hypercube_sampling(5, self.num_particles)
        transformed_samples = self.vectorApi.latin_transform(samples)
        for i in range(self.num_particles):
            particle = self.vectorApi.particleFactory(self.image, transformed_samples[i])
            self.particles.append(particle)

    def update_global_best(self):
        global_best_fitness = float('inf')
        global_best_theta = None
        for particle in self.particles:
            conf = self.evaluate_fitness(particle.theta)
            # 当粒子的当前位置优于其历史最优位置时，或者当前状态为解时，更新其历史最优位置
            if conf < particle.conf:
                particle.best_theta = copy.copy(particle.theta)
                particle.conf = conf

            # 更新全局最优位置
            if conf < global_best_fitness:
                global_best_fitness = conf
                global_best_theta = copy.copy(particle.theta)
        # 更新历史全局最优位置
        if self.best_conf is None or self.best_conf > global_best_fitness:
            self.best_conf = global_best_fitness
            self.best_theta = copy.copy(global_best_theta)
        print('[pso最低分数] conf:%f' % self.best_conf)

    def evaluate_fitness(self, theta):
        image_new = makeLB(theta, self.image)
        self.atk_times += 1
        conf = self.modelApi.get_y_conf(image_new, self.label)
        return conf

    def update_weight(self, iter):
        self.inertia_weight = self.inertia_weight_max - self.inertia_weight_min * iter / self.max_iterations

    def getAdvLB(self, **kwargs):
        self.setHyperParams(**kwargs)

        self.initialize_particles()
        self.update_global_best()
        for _ in range(self.max_iterations):
            self.update_weight(_)
            tuple1, tuple2 = self.modelApi.get_conf(makeLB(self.best_theta, self.image))[0:2]
            argmax, confmax = tuple1
            argsec, confsec = tuple2
            print(argmax, confmax, argsec, confsec)
            self.atk_times += 1
            if argmax != self.label and confmax > confsec + self.threshold:
                print("[psoLB] 标签%s被攻击为%s" % (self.label, argmax))
                print("[psoLB] 参数 波长:%f 位置:(%f %f) 宽度:%f 强度:%f" % (self.best_theta.phi, self.best_theta.q1,
                                                                   self.best_theta.q2, self.best_theta.w,
                                                                   self.best_theta.alpha))
                saveFile = 'adv/' + str(self.label) + '--' + str(argmax) + '--' + str(confmax) + '.jpg'
                makeLB(self.best_theta, self.image).save(saveFile)
                write_log(self.label, argmax, self.best_theta, self.conf, confmax, self.atk_times, self.modelApi.name)
                return self.best_theta, self.atk_times
            for particle in self.particles:
                particle.update_velocity(self.best_theta, self.inertia_weight, self.cognitive_weight,
                                         self.social_weight)
                particle.update_theta()
            self.update_global_best()
        print("[psoLB] 未找到攻击样本")
        # saveFile = 'adv/' + str(self.label) + '--' + str(self.conf) + '.jpg'
        # self.image.save(saveFile)
        return self.best_theta, -1
