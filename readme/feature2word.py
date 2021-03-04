from readme.text2word import TextToWord

class FeatureToWord:
    def __init__(self,feature):
        self.feature = feature


    def processFeature(self):
        return TextToWord(self.feature).processText()



