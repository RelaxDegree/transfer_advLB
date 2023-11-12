import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt

def build_CAM_model(base_model):
    # 获取MobileNetV2模型的最后一个卷积层输出
    last_conv_layer = base_model.get_layer('block_16_project_BN')
    last_conv_layer_model = tf.keras.Model(inputs=base_model.inputs, outputs=last_conv_layer.output)

    # 构建CAM模型
    cam_model = tf.keras.Sequential([
        base_model,
        last_conv_layer_model
    ])
    return cam_model

def generate_CAM(image_path, cam_model):
    # 加载图像并进行预处理
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # 获取预测类别的输出和最后一个卷积层输出
    preds = cam_model.predict(img_array)
    predicted_class = np.argmax(preds)
    last_conv_output = cam_model.layers[-1].output

    # 计算注意力热图
    grads = tf.gradients(preds[:, predicted_class], last_conv_output)[0]
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    cam = tf.reduce_sum(tf.multiply(pooled_grads, last_conv_output), axis=-1)
    cam = np.maximum(cam, 0)
    cam /= np.max(cam)
    return cam, predicted_class

# 加载预训练的MobileNetV2模型
base_model = MobileNetV2(weights='imagenet')

# 构建CAM模型
cam_model = build_CAM_model(base_model)

# 生成注意力热图
image_path = 'path_to_your_image.jpg'
cam, predicted_class = generate_CAM(image_path, cam_model)

# 可视化注意力热图
original_img = image.load_img(image_path, target_size=(224, 224))
plt.imshow(original_img)
plt.imshow(cam, cmap='jet', alpha=0.5)
plt.show()
