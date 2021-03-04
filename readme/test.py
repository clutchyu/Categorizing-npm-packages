from collections import Counter
import couchdb
# list = ['a','a','b']
# print(Counter(list))
# dictionary = dict(Counter(list))
# print(dictionary)
from readme.code2word import CodeToWord
from readme.intro2word import IntroToWord
from readme.feature2word import FeatureToWord
from readme.usage2word import UsageToWord
from readme.split_readme import SplitReadme
import json
import nltk
from collections import Counter
import couchdb
import re

class ReadmeToWord:
    def __init__(self,SplitReadme):
        self.intro = SplitReadme.getIntroduction()
        self.featrue = SplitReadme.getFeature()
        self.usage = SplitReadme.getUsage()
        self.code = SplitReadme.getCode()


    def readme2word(self):
        readme_token = []
        tokenizer = nltk.RegexpTokenizer(r"\w+")
        intro = IntroToWord(self.intro).processIntro()
        readme_token.append(intro)
        feature = FeatureToWord(self.featrue).processFeature()
        readme_token.append(feature)
        #usage = UsageToWord(self.usage,intro+feature).processUsage()
        usage = UsageToWord(self.usage, intro).processUsage()
        readme_token.append(usage)
        code = CodeToWord(self.code).processCode()
        readme_token.append(code)
        return readme_token

    def getScore(self,readme_list,weight_list):  # readme 每个部分的词频乘上该部分对应的权重，该词在每个部分的得分之和是最后的得分
        score_dict = dict()
        part_count = 0
        while part_count < len(readme_list):
            weight = weight_list[part_count]
            word_frequency = dict(Counter(readme_list[part_count]))
            for word in word_frequency:
                if word in score_dict:
                    score_dict[word] = float(format(weight * word_frequency[word] + score_dict[word],'.4f'))
                else:
                    score_dict[word] = float(format(weight * word_frequency[word],'.4f'))
            part_count += 1
        return score_dict

def getPackage(path):
    with open(path, encoding="utf-8") as files:
        text = files.readlines()
    pattern = re.compile(r'\[(.*?)\]')
    package_dict = dict()
    for line in text:
        label = re.findall(pattern, line)
        if len(label) == 0:
            continue
        label_text = label[0]  # 一行最开始的[ ]
        if len(label_text) > 0:
            name = re.sub(pattern, ' ', line)
            # words = TextToWord(texts).processText()       # 之前语料库中为description ，现在为处理过的 word
            package_dict[name.split()[0]] = label_text
    return package_dict

if __name__=="__main__":

    server = couchdb.Server('http://wangyu:wangyu.com123@localhost:5984/')
    db_source = server['registry']

    with open('D:/npm_keywords/dataset/github_package', encoding="utf-8") as files:
        text = files.readlines()
    pattern = re.compile(r'\[(.*?)\]')
    package_list = list()
    for line in text:
        name = re.sub(pattern, ' ', line)
        package_list.append(name.split()[0])

    session_len_dic = dict()
    count = 0

    for name in package_list:
        package = db_source[name]
        readme = package['readme']
        if len(readme) == 0:
            print("No readme in this package")
        else:
            part_readme = SplitReadme('express')
            part_readme.split_readme(readme)
            readme = ReadmeToWord(part_readme)
            session_list = readme.readme2word()
            session_len_dic[name] = [len(session_list[0]),len(session_list[1]),len(session_list[2])]

            if len(session_list[2]) == 0:
                print(name)
                print(session_len_dic[name])
                count += 1

    print(count)





