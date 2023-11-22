import torch
import torchvision.transforms as transforms
labels_file = "model\\imagenet_labels.txt"
with open(labels_file) as f:
    labels = f.readlines()
labels = [label.strip() for label in labels]


class ModelApi:

    # 获取图像的预测结果
    def get_conf(self, img, k=5):
        # image = Image.open(image_path)
        # print(type(image))
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(img)
        input_tensor = input_tensor.to(self.device)
        input_batch = input_tensor.unsqueeze(0)

        # 将图像输入模型并进行预测
        with torch.no_grad():
            output = self.model(input_batch.to(self.device))
        # 获取预测结果
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top_k = torch.topk(probabilities, k)

        conf_list = []
        for i in range(k):
            index = top_k.indices[i].item()
            probability = top_k.values[i].item()

            label = labels[index + 1]
            conf_list.append((label, probability))
            # print(f"{label}: {probability:.5f}")
        return conf_list

    # 获取图像对于特定类别的预测结果
    def get_y_conf(self, img, label):
        conf_list = self.get_conf(img, 1000)
        for i in range(len(conf_list)):
            if conf_list[i][0] == label or label in conf_list[i][0]:
                return conf_list[i][1]
        return 0
