class SMLB:
    def __init__(self, modelApi, vectorApi):
        self.modelApi = modelApi
        self.vectorApi = vectorApi
        self.modelApis = []

    # 获取攻击后的图像
    def getAdvLB(self, **kwargs):
        pass

    def setModels(self, modelApi):
        self.modelApis.append(modelApi)

    def setVectorApi(self, vectorApi):
        self.vectorApi = vectorApi

    def setModelApi(self, modelApi):
        self.modelApi = modelApi
