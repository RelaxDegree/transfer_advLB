from smlb import SMLB
import random
import math
from laser.Vector import Particle
import copy
from laser.laser import makeLB
from utils.utils import write_log
import matplotlib.pyplot as plt
import numpy as np


class PSO(SMLB):
    threshold = 0.02

    def setHyperParams(self, num_particles, image, inertia_weight, cognitive_weight, social_weight, max_iterations, ):
        self.num_particles = num_particles
        self.image = image
        self.inertia_weight = inertia_weight
        self.cognitive_weight = cognitive_weight
        self.social_weight = social_weight
        self.max_iterations = max_iterations
        self.particles = []
        self.label, self.conf = self.modelApi.get_conf(image)[0]
        self.atk_times = 0
        print('[adv开始] label:%s conf:%f' % (self.label, self.conf))

    def __init__(self, modelApi,vectorApi):
        super().__init__(modelApi, vectorApi)
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
        return self.particles[0].latin_transform(samples)

    def initialize_particles(self):
        # 生成拉丁超立方采样样本
        samples = self.latin_hypercube_sampling(5, self.num_particles)
        for i in range(self.num_particles):
            particle = Particle(self.image, samples[i])
            self.particles.append(particle)

    def update_global_best(self):
        global_best_fitness = float('inf')
        global_best_theta = None
        for particle in self.particles:
            argmax, fitness, conf_sec = self.evaluate_fitness(particle.theta)
            if argmax == self.label and fitness < particle.conf:
                particle.best_theta = copy.copy(particle.theta)
                particle.conf = fitness
                particle.argmax = argmax
                particle.conf_sec = conf_sec
            elif argmax != self.label:
                particle.best_theta = copy.copy(particle.theta)
                particle.conf = fitness
                particle.argmax = argmax
                particle.conf_sec = conf_sec
            if argmax == self.label and fitness < global_best_fitness:
                global_best_fitness = fitness
                global_best_theta = copy.copy(particle.theta)
        print('[adv最低分数] conf:%f' % global_best_fitness)

        return global_best_theta, global_best_fitness

    def evaluate_fitness(self, theta):
        image_new = makeLB(theta, self.image)
        self.atk_times += 1
        conf_list = self.modelApi.get_conf(image_new)
        argmax, conf_max = conf_list[0]
        conf_sec = conf_list[1][1]
        return argmax, conf_max, conf_sec

    def getAdvLB(self, **kwargs):
        self.setHyperParams(**kwargs)
        self.initialize_particles()
        global_best_theta = self.update_global_best()[0]

        for _ in range(self.max_iterations):
            for particle in self.particles:
                if particle.argmax != self.label and particle.conf > particle.conf_sec + self.threshold:
                    print("[advLB] 标签%s被攻击为%s" % (self.label, particle.argmax))
                    print("[advLB] 参数 波长:%f 位置:(%f %f) 宽度:%f 强度:%f" % (particle.theta.phi, particle.theta.l,
                                                                       particle.theta.b, particle.theta.w,
                                                                       particle.theta.alpha))
                    saveFile = 'adv/' + str(self.label) + '--' + str(particle.argmax) + '--' + str(
                        particle.conf) + '.jpg'
                    makeLB(particle.theta, self.image).save(saveFile)
                    write_log(self.label, particle.argmax, particle.theta, self.conf, particle.conf, self.atk_times)
                    return particle.theta, self.atk_times
            for particle in self.particles:
                particle.update_velocity(global_best_theta, self.inertia_weight, self.cognitive_weight,
                                         self.social_weight)
                particle.update_theta()

            global_best_theta = self.update_global_best()[0]
        print("[advLB] 未找到攻击样本")
        saveFile = 'adv/' + str(self.label) + '--' + str(self.conf) + '.jpg'
        self.image.save(saveFile)
        theta = None
        return theta, self.atk_times

    def optimize_analyze(self):
        self.initialize_particles()
        fitness_lst = []
        global_best_theta, global_best_fitness = self.update_global_best()
        fitness_lst.append(global_best_fitness)
        for _ in range(self.max_iterations):
            print('第%d次迭代=================================================' % _)
            for particle in self.particles:
                particle.update_velocity(global_best_theta, self.inertia_weight, self.cognitive_weight,
                                         self.social_weight)
                particle.update_theta()

            global_best_theta, global_best_fitness = self.update_global_best()
            fitness_lst.append(global_best_fitness)
        # 生成一些示例数据
        x = np.linspace(1, self.max_iterations, len(fitness_lst))
        print(x)
        print(len(x))
        y = np.array(fitness_lst)

        # 设置图形的大小和分辨率（可选）
        plt.figure(figsize=(8, 6), dpi=80)

        # 绘制折线图
        plt.plot(x, y, color='blue', linewidth=2, label='fitness')

        # 设置图形标题和轴标签
        plt.title('PSO')
        plt.xlabel('X Axis')
        plt.ylabel('Y Axis')

        plt.grid(True, linestyle='--', alpha=0.7)

        # 添加图例
        plt.legend()

        # 保存图形（可选）
        plt.savefig('sin_function.png')

        # 显示图形
        plt.show()
        return global_best_theta, self.atk_times

    def getAdvLB(self, **kwargs):

        pass
