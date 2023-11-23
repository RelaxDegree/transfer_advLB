import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
from model.modelVitAPI import ModelVitApi


class Vit_b(ModelVitApi):

    def __init__(self):
        # 加载预训练的ResNet模型
        self.name = "Vit_b"
        model_name = "E:\\pretrained_models\\vitB"
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        # self.model.eval()

    def get_conf(self, img, k=5):
        return super().get_conf(img, k)

    def get_y_conf(self, img, label):
        return super().get_y_conf(img, label)



