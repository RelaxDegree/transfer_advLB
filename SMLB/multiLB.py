from sko.PSO import PSO
import matplotlib.pyplot as plt


# 定义优化的目标函数，这里使用 Rosenbrock 函数
def rosenbrock(x):
    return sum(100 * (x[i + 1] - x[i] ** 2) ** 2 + (1 - x[i]) ** 2 for i in range(len(x) - 1))


# 初始化 PSO 算法
pso = PSO(func=rosenbrock, n_dim=2, pop=40, max_iter=100, lb=[-10, -10], ub=[10, 10], w=0.8, c1=0.5, c2=0.5)

# 执行优化
pso.run(precision=1e-7, N=10)

# 输出最优解
print('最优解:', pso.gbest_x)
print('最优解的目标函数值:', pso.gbest_y)

# 绘制目标函数值的变化
plt.plot(pso.gbest_y_hist)
plt.xlabel('Iterations')
plt.ylabel('Best fitness')
plt.show()
