import torch
from PIL import Image

from matplotlib import pyplot as plt
from torchvision import models
from transformers import AutoModelForImageClassification


def grad_cam(model, image, label):
  """
  使用Grad-CAM计算模型的注意力热图。

  Args:
    model: 要分析的模型。
    image: 输入图像。
    label: 要预测的类别标签。

  Returns:
    注意力热图。
  """

  # 将图像转换为模型输入格式。
  # image = image.unsqueeze(0)
  image = torch.transpose(image, 3, 1)

  # 前向传播。
  logits = model(image)

  # 计算类别预测。
  prediction = logits.argmax(dim=1)
  if prediction != label:
    return None

  # 计算梯度。
  loss = -logits[0, label]
  gradients = torch.autograd.grad(loss, model.parameters(), create_graph=True)[0]

  # 计算注意力热图。
  attention_map = gradients.squeeze(0).mean(dim=1)
  attention_map = attention_map.reshape(image.size()[1:])

  # 归一化注意力热图。
  attention_map = attention_map / attention_map.max()

  return attention_map


# 加载模型。
model_name = "E:\\pretrained_models\\vitB"
model = AutoModelForImageClassification.from_pretrained(model_name)

# 加载图像。
image = Image.open("2.jpg")

# 计算注意力热图。
attention_map = grad_cam(model, image, 0)

# 显示注意力热图。
plt.imshow(attention_map)
plt.show()
