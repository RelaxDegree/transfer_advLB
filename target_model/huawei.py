import json
import requests

# 账号信息

access_key = "your_access_key"

secret_key = "your_secret_key"

# 接口参数

endpoint = "https://api-endpoint.huawei.com"

uri = "/v1/infers/your_service_id"

# 待分类的图像路径

image_path = "path_to_your_image.jpg"


def send_request():
    # 构造请求头

    headers = {

        "Content-Type": "application/json",

        "X-Auth-Token": access_key + " " + secret_key

    }

    # 构造请求体

    payload = {

        "image": open(image_path, "rb")

    }

    try:

        # 发送POST请求

        response = requests.post(endpoint + uri, headers=headers, files=payload)

        # 解析响应结果

        result = json.loads(response.text)

        # 打印分类结果

        print("图像分类结果：", result["result"][0]["label"])

    except Exception as e:

        print("请求失败：", str(e))