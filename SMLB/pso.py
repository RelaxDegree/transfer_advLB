from SMLB.smlb import SMLB
from sko.PSO import PSO as OriginalPSO

import random
import math
from laser.Vector import Particle
import copy
from laser.laser import makeLB
from utils.utils import write_log
import matplotlib.pyplot as plt
import numpy as np

# from mealpy.swarm_based.PSO import OriginalPSO

threshold = 0.0
image = None
model_api = None
vector_api = None
atk_times = 0
particles = []
label, conf = None, 0


# 定义函数
def fitness_function(solution):
    global image
    global atk_times
    global model_api
    global label
    theta = vector_api.factory(solution.tolist())
    image_new = makeLB(theta, image)
    atk_times += 1
    return model_api.get_y_conf(image_new, label)


problem_dict1 = {
    "fit_func": fitness_function,
    "lb": [380, 0, 0, 10, 0.2],
    "ub": [750, 1, 1, 50, 1],
    "minmax": "min",
}
# Use all available stopping conditions together
term_dict = {
    # "max_epoch": 1100,
    # "max_fe": 0.07,
    # "max_time": 60,
    "max_early_stop": 8
}


def check_stop(gbest_x):
    global vector_api
    global model_api
    global atk_times
    atk_times += 1
    while type(gbest_x) == np.ndarray:
        if len(gbest_x) != 1:
            break
        gbest_x = gbest_x[0]

    best_vector = vector_api.factory(gbest_x.tolist())
    imgnew = makeLB(best_vector, image)
    tuple1, tuple2 = model_api.get_conf(imgnew)[0:2]
    argmax, confmax = tuple1
    argsec, confsec = tuple2
    if argmax != label and confmax > confsec + threshold:
        return True
    return False


class PSO(SMLB):
    # 参数

    def setHyperParams(self, **kwargs):
        global image
        global label
        global conf
        global problem_dict1
        global atk_times
        global vector_api
        vector_api = self.vectorApi
        problem_dict1["lb"] = self.vectorApi.get_lb()
        problem_dict1["ub"] = self.vectorApi.get_ub()
        self.num_particles = kwargs['num_particles']
        image = kwargs['image']
        self.inertia_weight_max = kwargs['inertia_weight_max']
        self.inertia_weight_min = kwargs['inertia_weight_min']
        self.cognitive_weight = kwargs['cognitive_weight']
        self.social_weight = kwargs['social_weight']
        self.max_iterations = kwargs['max_iterations']

        label, conf = self.modelApi.get_conf(image)[0]
        atk_times = 0
        print('[adv开始] label:%s conf:%f' % (label, conf))

    def __init__(self, modelApi, vectorApi):
        super().__init__(modelApi, vectorApi)

        global model_api, vector_api
        model_api = self.modelApi
        vector_api = self.vectorApi
        self.num_particles = None
        self.inertia_weight_max = None
        self.inertia_weight_min = None
        self.cognitive_weight = None
        self.social_weight = None
        self.max_iterations = None

    def getAdvLB(self, **kwargs):
        self.setHyperParams(**kwargs)
        global vector_api
        max_iter = self.max_iterations
        pop_size = self.num_particles
        c1 = self.cognitive_weight
        c2 = self.social_weight
        w_min = self.inertia_weight_min
        w_max = self.inertia_weight_max

        # model = OriginalPSO(epoch, pop_size, c1, c2, w_min, w_max)
        print(vector_api.get_lb())
        print(vector_api.get_ub())
        pso = OriginalPSO(func=fitness_function, n_dim=5, pop=pop_size, max_iter=max_iter, lb=vector_api.get_lb(),
                          ub=vector_api.get_ub(), w=0.8, c1=c1, c2=c2, verbose=True)
        pso.setCheck(check_stop)
        pso.run(precision=1e-5, N=10)
        # best_position, best_fitness = model.solve(problem_dict1, termination=term_dict)
        # model.history.save_global_objectives_chart(filename="diagram/")
        # model.history.save_local_objectives_chart(filename="diagram/")
        global atk_times, threshold, label, conf, atk_times, model_api
        gbest = pso.gbest_x
        while type(gbest) == np.ndarray:
            if len(gbest) != 1:
                break
            gbest = gbest[0]
        best_vector = self.vectorApi.factory(gbest.tolist())
        imgnew = makeLB(best_vector, image)
        tuple1, tuple2 = self.modelApi.get_conf(imgnew)[0:2]
        argmax, confmax = tuple1
        argsec, confsec = tuple2
        msg = None
        if argmax != label and confmax > confsec + threshold:
            best_vector.print()
            msg = "源标签%s\n被误分类为%s" % (label, argmax)
            print("[psoLB]" + msg)
            saveFile = 'adv/' + str(label) + '--' + str(argmax) + '--' + str(confmax) + '.jpg'
            imgnew.save(saveFile)
            write_log(label, argmax, best_vector, conf, confmax, atk_times, model_api.name)
            return best_vector, atk_times, argmax, msg
        return best_vector, -1, argmax, msg
