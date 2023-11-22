import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import requests
from model.modelAPI import ModelApi


class ModelVitApi(ModelApi):

    def get_conf(self, img, k=5):
        inputs = self.processor(images=img, return_tensors="pt")
        inputs.to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        top_k = torch.topk(probabilities, 10)
        conf_list = []
        for i in range(10):
            index = top_k.indices[0][i].item()
            probability = top_k.values[0][i].item()
            conf_list.append((self.model.config.id2label[index], probability))
        # 打印结果
        return conf_list

    def get_y_conf(self, img, label):
        conf_list = self.get_conf(img, 1000)
        for i in range(len(conf_list)):
            if conf_list[i][0] == label or label in conf_list[i][0]:
                return conf_list[i][1]
        return 0
