import matplotlib.pyplot as plt
import numpy as np

# 生成模拟数据
iterations = np.arange(0, 201, 15)
resnet50_scores = [0.885, 0.543, 0.385, 0.300, 0.242, 0.192, 0.171, 0.169, 0.173, 0.171, 0.166, 0.164, 0.160, 0.171]
mobilenetv2_scores = [0.823, 0.417, 0.317, 0.254, 0.235, 0.232, 0.227, 0.230, 0.225, 0.219, 0.217, 0.212, 0.219, 0.221]
vitb_scores = [0.985, 0.826, 0.653, 0.521, 0.406, 0.317, 0.246, 0.192, 0.154, 0.127, 0.097, 0.111, 0.097, 0.098]

# 绘制折线图，每个数据点以原点呈现，用点横虚线连接
plt.plot(iterations, resnet50_scores, 'o--', label='ResNet50')
plt.plot(iterations, mobilenetv2_scores, 'o--', label='MobileNet-v2')
plt.axvline(x=88,ymin=0,ymax=0.12, linestyle='--', color='gray', linewidth=2)
plt.axvline(x=42,ymin=0,ymax=0.21, linestyle='--', color='gray', linewidth=2)
plt.axvline(x=152,ymin=0,ymax=0.05, linestyle='--', color='gray', linewidth=2)
plt.plot(iterations, vitb_scores, 'o--', label='Vit-B')

# 设置图表标题和标签
plt.xlabel('Iterations')
plt.ylabel('Average Confidence Score')

# 设置图例
plt.legend()

# 显示图表
plt.show()
