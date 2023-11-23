from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

# 加载Bit-50模型和处理器
model_name = "openai/bit-50"
processor = CLIPProcessor.from_pretrained(model_name)
model = CLIPModel.from_pretrained(model_name)

# 图像预处理
image_path = 'path_to_your_image.jpg'
image = Image.open(image_path)
inputs = processor(text="a photo", images=image, return_tensors="pt")

# 使用模型进行预测
with torch.no_grad():
    outputs = model(**inputs)

# 获取图像特征
image_features = outputs.last_hidden_state[:, 0, :]

# 在实际应用中，您可能需要将图像特征传递给分类器进行最终的图像分类

# 输出图像特征的形状
print("Image features shape:", image_features.shape)
