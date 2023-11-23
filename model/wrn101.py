import torch
from model.modelAPI import ModelApi
import torchvision.models as models
from PIL import Image
from torchvision.models import ResNet50_Weights


class Wrn101(ModelApi):

    def __init__(self):
        # 加载预训练的ResNet模型
        self.name = "WRN101"
        self.model = models.wide_resnet101_2(pretrained=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    # 获取图像的预测结果
    def get_conf(self, img, k=5):
        return super().get_conf(img, k)

    # 获取图像对于特定类别的预测结果
    def get_y_conf(self, img, label):
        return super().get_y_conf(img, label)


# rn50 = Rn50()
# img = Image.open("2.jpg")
# print(rn50.get_conf(img))