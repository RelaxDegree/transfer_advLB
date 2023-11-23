import torch
from model.modelAPI import ModelApi
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from torchvision.models import MobileNet_V2_Weights


class Mbv2(ModelApi):

    def __init__(self):
        # 加载预训练的ResNet模型
        self.name = "MobileNet_V2"
        self.model = models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    # 获取图像的预测结果
    def get_conf(self, img, k=5):
        return super().get_conf(img, k)

    # 获取图像对于特定类别的预测结果
    def get_y_conf(self, img, label):
        return super().get_y_conf(img, label)
#
# mbv2 = Mbv2()
# img = Image.open("2.jpg")
# print(mbv2.get_conf(img))