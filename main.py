import matplotlib.pyplot as plt

# 定义两条直线的x轴上的点
x = [0, 1]
y_line1 = [2, 3]
y_line2 = [-4, -5]

plt.figure()  # 创建图形对象
plt.fill(x + x[::-1], y_line1 + y_line2)  # 绘制闭合曲线并填充颜色
plt.show()  # 显示图形