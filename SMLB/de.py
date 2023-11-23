import random
import copy
from utils.utils import write_log
from laser.laser import makeLB
from SMLB.smlb import SMLB


class DE(SMLB):
    def __init__(self, modelApi, vectorApi):
        super().__init__(modelApi, vectorApi)
        self.fitness = None
        self.num_particles = None
        self.image = None
        self.scale_factor = None
        self.cross_probability = None
        self.max_iterations = None
        self.population = None
        self.label = None
        self.conf = None
        self.atk_times = None

    def setHyperParams(self, **kwargs):
        self.num_particles = kwargs['num_particles']
        self.image = kwargs['image']
        self.scale_factor = kwargs['scale_factor']
        self.cross_probability = kwargs['cross_probability']
        self.max_iterations = kwargs['max_iterations']
        self.population = []
        self.label, self.conf = self.modelApi.get_conf(self.image)[0]
        self.fitness = 0
        self.atk_times = 0
        print('[adv开始] label:%s conf:%f' % (self.label, self.conf))

    def initialize_population(self):
        for _ in range(self.num_particles):
            particle = Particle(self.image)
            self.population.append(particle)

    def mutate(self, target, a, b, c):
        # Mutation operation for DE
        candidate = copy.deepcopy(target)
        indices = list(range(len(candidate.theta)))

        # Randomly select three distinct indices
        random.shuffle(indices)
        rand1, rand2, rand3 = indices[:3]

        for i in range(len(candidate.theta)):
            if random.random() < self.cross_probability or i == rand3:
                candidate.theta[i] = target.theta[rand1] + a * (target.theta[rand2] - target.theta[rand3])
            else:
                candidate.theta[i] = target.theta[i]

        return candidate

    def crossover(self, target, mutant):
        # Crossover operation for DE
        for i in range(len(target.theta)):
            if random.random() < self.cross_probability:
                target.theta[i] = mutant.theta[i]

        return target

    def update_global_best(self):
        global_best_fitness = float('inf')
        global_best_theta = None
        for particle in self.population:
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

        self.initialize_population()
        global_best_theta = self.update_global_best()[0]

        for _ in range(self.max_iterations):
            for i in range(self.num_particles):
                target = self.population[i]

                # Mutation
                mutant = self.mutate(target, 0.5, 0.5, 0.5)

                # Crossover
                trial = self.crossover(target, mutant)

                # Selection
                argmax, fitness, conf_sec = self.evaluate_fitness(trial.theta)
                if argmax == self.label and fitness < target.conf:
                    target.theta = copy.copy(trial.theta)
                    target.conf = fitness
                    target.argmax = argmax
                    target.conf_sec = conf_sec
                elif argmax != self.label:
                    target.theta = copy.copy(trial.theta)
                    target.conf = fitness
                    target.argmax = argmax
                    target.conf_sec = conf_sec

            global_best_theta = self.update_global_best()[0]

            for particle in self.population:
                if particle.argmax != self.label and particle.conf > particle.conf_sec + PSO.threshold:
                    print("[advLB] 标签%s被攻击为%s" % (self.label, particle.argmax))
                    print("[advLB] 参数 波长:%f 位置:(%f %f) 宽度:%f 强度:%f" % (particle.theta.phi, particle.theta.l,
                                                                       particle.theta.b, particle.theta.w,
                                                                       particle.theta.alpha))
                    saveFile = 'adv/' + str(self.label) + '--' + str(particle.argmax) + '--' + str(
                        particle.conf) + '.jpg'
                    makeLB(particle.theta, self.image).save(saveFile)
                    write_log(self.label, particle.argmax, particle.theta, self.conf, particle.conf, self.atk_times)
                    return particle.theta, self.atk_times

        print("[advLB] 未找到攻击样本")
        saveFile = 'adv/' + str(self.label) + '--' + str(self.conf) + '.jpg'
        self.image.save(saveFile)
        theta = None
        return theta, self.atk_times
