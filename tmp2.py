import numpy as np
from mealpy.swarm_based.PSO import OriginalPSO


# 定义函数
def fitness_function(solution):
    print(type(solution))
    return np.sum(solution ** 2)


# 参数
problem_dict1 = {
    "fit_func": fitness_function,
    "lb": [0, 0, 0, 0, 0],
    "ub": [10, 15, 12, 8, 20],
    "minmax": "min",
}
# PSO参数
epoch = 1000
pop_size = 50
c1 = 2.05
c2 = 2.05
w_min = 0.4
w_max = 0.9
model = OriginalPSO(epoch, pop_size, c1, c2, w_min, w_max)
best_position, best_fitness = model.solve(problem_dict1)
print(f"Solution: {best_position}, Fitness: {best_fitness}")
