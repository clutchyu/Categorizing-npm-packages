import logging
from nltk.corpus import stopwords
from PyEMD import emd
from gensim.models import KeyedVectors
import gensim
import couchdb
import os
from readme.split_readme import SplitReadme
from readme.readme2word import ReadmeToWord
import json
import re
import numpy as np
from sklearn import metrics

from sklearn.metrics import label_ranking_average_precision_score



def getReadme(package_name,weight_list):
    server = couchdb.Server('http://wangyu:wangyu.com123@localhost:5984/')
    db_source = server['registry']
    try:
        package = db_source[package_name]
    except:
        print("NO this package")
        return None
    try:
        readme = package['readme']
    except:
        return None
    if readme is None or len(readme) == 0:
        print("NO readme")
        return None
    else:
        split_readme = SplitReadme(package_name)
        split_readme.split_readme(readme)
        readme2word = ReadmeToWord(split_readme)
        readme_list = readme2word.readme2word()
        return readme2word.getScore(readme_list,weight_list)


def getKeywordSet(path): # 获取所有类别的 keywordset
    with open(path,'r') as json_file:
        dic = json.load(json_file)
    return dic

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

def nomarlizeWeight(keywords_dict):
    for i in keywords_dict:
        cate_dict = keywords_dict[i]
        value_list = cate_dict.values()
        total_value = sum(value_list)
        for cate in cate_dict:
            index = cate_dict[cate]
            cate_dict[cate] = float(format(index/total_value,'.3f'))

def getCorpus(path,label):
    with open(path, encoding="utf-8") as files:
        text = files.readlines()
    pattern = re.compile(r'\[(.*?)\]')
    for line in text:
        label_list = re.findall(pattern, line)
        if len(label_list) == 0:
            continue
        label_text = label_list[0]      # 一行最开始的[ ]
        for item in label_text.split():
            if item not in cate_list:
               label_text = ''
        if len(label_text) > 0:
            label.append(label_text.split())

def determinTag(tag_distribution):
    tag_list = list(tag_distribution.keys())
    primary_tag = tag_list[0]
    alternative_tag = tag_list[1]
    flag_tag = tag_list[2]
    value_1 = tag_distribution[alternative_tag] - tag_distribution[primary_tag]
    value_2 = tag_distribution[flag_tag] - tag_distribution[alternative_tag]
    if value_1 > value_2:     # 第一个标签与第二个标签的差值 大于 第二个标签与第三个标签的差值， 则最终的选择的是单标签。否则，则选择标签1，2。
        return [primary_tag]
    else:
        return [primary_tag,alternative_tag]

cate_list = ['number','string','time','collection','text','promise','stream','security','debug','error',
             'fs','http','url','util','cli','documentation','image','loader','log','validation','test',
             'database','framework','authentication','email','parser','typescript','markdown','event']

def labelArray(package_label_list):
    final_list = []
    for label_list in package_label_list:
        label_array = np.zeros(len(cate_list))
        for label in label_list:
            postion = cate_list.index(label)
            label_array[postion] = 1
        final_list.append(label_array)
    return np.array(final_list)

def labelScore(tag_distribution):
    final_list = []
    for distribution in tag_distribution:
        score_list = []
        print(distribution)
        for word in distribution:
            score = distribution[word]
            score_list.append(float(format(1/score,'.4f')))
        final_list.append(score_list)
    return np.array(final_list)

if __name__=="__main__":
    with open('C:/Users/Admin/Documents/我的坚果云/NPM_Cate/material/category', encoding="utf-8") as files:
        cate_words = files.read()
    cate_words_list = cate_words.split('\n')

    model = gensim.models.Word2Vec.load('w2v.model')
    model.init_sims(replace=True)  # Normalizes the vectors in the word2vec class.,如果没有这条，距离的差距会变小

    # cate_dict = getKeywordSet('D:/npm_keywords/keywords_del_common_50iter.json')
    cate_dict = getKeywordSet('D:/npm_keywords/final_experiment/keywords_del_common_100iter.json')
    nomarlizeWeight(cate_dict)
    # for cate in cate_dict:
    #     print(cate)
    #     print(cate_dict[cate])

    # weight_list = [0.4, 0.1, 0.2, 0.3]
    # weight_list = [0.4, 0.1, 0.3, 0.2]
    # weight_list = [0.4, 0.2, 0.1, 0.3]
    # weight_list = [0.4, 0.2, 0.2, 0.2]
    # weight_list = [0.4, 0.2, 0.3, 0.1]
    # weight_list = [0.4, 0.3, 0.2, 0.1]
    # weight_list = [0.4, 0.3, 0.1, 0.2]
    # weight_list = [0.5, 0.1, 0.1, 0.3]
    # weight_list = [0.5, 0.1, 0.2, 0.2]
    # weight_list = [0.5, 0.1, 0.3, 0.1]
    # weight_list = [0.5, 0.2, 0.1, 0.2]
    # weight_list = [0.5, 0.2, 0.2, 0.1]
    # weight_list = [0.5, 0.3, 0.1, 0.1]
    # weight_list = [0.6, 0.1, 0.1, 0.2]
    # weight_list = [0.6, 0.1, 0.2, 0.1]
    # weight_list = [0.6, 0.2, 0.1, 0.1]
    weight_list = [0.7, 0.1, 0.1, 0.1]

    label_test = []
    getCorpus('D:/npm_keywords/new_experiment/test_data/test_corpus_intro.txt',label_test)
    y_true = labelArray(label_test)

    package_dict = getPackage('D:/npm_keywords/new_experiment/test_data/test_package_name.txt')


    tag_result = []
    tag_distribution = []
    for package in package_dict:
        readme = getReadme(package,weight_list)
        if readme is None:
            # print('package error')
            continue
        else:

            distance_list = dict()

            for item in cate_dict:
                distance = float(format(model.wv.wmdistance(cate_dict[item],readme),'.4f'))
                distance_list[item] = distance
            list_1 = list(distance_list.items())
            my_dict_sortbyvalue = dict(sorted(list_1, key=lambda x: x[1], reverse=False))
            tag_distribution.append(my_dict_sortbyvalue)
            tag_result.append(determinTag(my_dict_sortbyvalue))


    y_pred = labelArray(tag_result)
    y_score = labelScore(tag_distribution)


    print('macro-f1:')
    print(metrics.f1_score(y_true, y_pred, average="macro"))
    print('micro-f1:')
    print(metrics.f1_score(y_true, y_pred, average="micro"))
    print('hamming_loss:')
    print(metrics.hamming_loss(y_true,y_pred))
    print('LRAP:')
    print(label_ranking_average_precision_score(y_true, y_score))

    #         if list(my_dict_sortbyvalue.keys())[0] == package_dict[package]:
    #             cate = package_dict[package]
    #             if cate in cate_count:
    #                 cate_count[cate] += 1
    #             else:
    #                 cate_count[cate] = 1
    #             correct += 1
    #             correct_list.append(package)
    # print(correct)
    # print(cate_count)





# KeyedVectors.py 引用了 pyemd 库，需要 install pyemd , 且最新版本的 pyemd 库无法适用，这里下载的是0.3.0版本
# 此外，安装 pyemd 库需要windows 环境中安装 visualsudio c++ 14.0.0 , 这里通过 visulsudio build tool 进行了安装 https://pan.baidu.com/s/1WaBxFghTll6Zofz1DGOZBg
# 最后需要把 from pyemd import emd 改成 from PyEMD import emd