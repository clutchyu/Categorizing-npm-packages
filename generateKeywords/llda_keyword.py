import sys, string, random, numpy
from nltk.corpus import reuters
from description2keywords.llda import LLDA
from optparse import OptionParser
from functools import reduce
import couchdb
import re
from readme.text2word import TextToWord
from time import time
import json




class Getkeywords:

    def getCate(self):
        pattern = re.compile(r'\[(.*?)\]')
        with open('../material/category', encoding="utf-8") as files:
            category_file = files.readlines()
        cate_dict = dict()
        for line in category_file:
            cate = re.findall(pattern, line)[0]
            texts = re.sub(pattern, ' ', line)
            seed_words = texts.split()
            cate_dict[cate] = seed_words
        self.cate_dict = cate_dict

    def configuration(self):
        parser = OptionParser()
        parser.add_option("--alpha", dest="alpha", type="float", help="parameter alpha", default=0.001)
        parser.add_option("--beta", dest="beta", type="float", help="parameter beta", default=0.001)
        parser.add_option("-k", dest="K", type="int", help="number of topics", default=29)
        parser.add_option("-i", dest="iteration", type="int", help="iteration count", default=100)
        parser.add_option("-s", dest="seed", type="int", help="random seed", default=None)
        parser.add_option("-n", dest="samplesize", type="int", help="dataset sample size", default=100)
        (options, args) = parser.parse_args()
        return (options, args)

    # category_list 为类别列表， label_list 为各个包所标记的类别， corpus 为各个包的description汇总的列表
    def getKeywords(self,category_list,label_list,corpus,cate_dict):
        (options, args) = self.configuration()
        llda = LLDA(options.K, options.alpha, options.beta)
        llda.set_corpus(category_list, corpus, label_list)
        print("M=%d, V=%d, L=%d, K=%d" % (len(corpus), len(llda.vocas), len(labelset), options.K))
        for i in range(options.iteration):
            sys.stderr.write("-- %d : %.4f\n" % (i, llda.perplexity()))
            llda.inference()
        print("perplexity : %.4f" % llda.perplexity())

        phi = llda.phi()
        for k, label in enumerate(labelset):
            if label not in cate_dict:
                word_dict = dict()
                probability_list = list()
                for w in numpy.argsort(-phi[k])[:50]:       #   L-LDA 输出前50个词
                    word_dict[llda.vocas[w]] = [float(format(phi[k,w],'.4f'))]
            else:
                word_dict = cate_dict[label]
                for w in numpy.argsort(-phi[k])[:50]:
                    if llda.vocas[w] in word_dict:
                        word_dict[llda.vocas[w]].append(float(format(phi[k,w],'.4f')))
                    else:
                        word_dict[llda.vocas[w]] = [float(format(phi[k,w],'.4f'))]
            cate_dict[label] = word_dict
        return cate_dict

    def getCorpus(self,path,label,corpus):
        with open(path, encoding="utf-8") as files:
            text = files.readlines()
        pattern = re.compile(r'\[(.*?)\]')
        for line in text:
            label_list = re.findall(pattern, line)
            if len(label_list) == 0:
                continue
            label_text = label_list[0]      # 一行最开始的[ ]
            for item in label_text.split():
                if item not in self.cate_dict.keys():
                   label_text = ''
            if len(label_text) > 0:
                label.append(label_text.split())
                texts = re.sub(pattern, ' ', line)
                # words = TextToWord(texts).processText()       # 之前语料库中为description ，现在为处理过的 word
                corpus.append(texts.split())


    def getMean(self,probabilty_llist,count):
        value = 0
        for item in probability_list:
            value += item
        return float(format(value/count,'.4f'))



    def dealKeywords(self,keywords_dict,cate):
        # 每个类下的关键词去重， 删除其他类别词的 seed words
        if cate == 'common':
            return
        seed_words_list = list()
        for item in self.cate_dict.values():
            seed_words_list = seed_words_list + item


        for word in self.cate_dict[cate]:       # 移除自身类别的 seed word ,得到其他类别 seed word 的合集
             seed_words_list.remove(word)

        keyword_list = list(keywords_dict.keys())

        cate_intersect =  set(keyword_list) & set(seed_words_list)
        if cate_intersect:
            for word in cate_intersect:
                del keywords_dict[word]


    def nomarlizeWeight(self,keywords_dict):
        value_list = keywords_dict.values()
        total_value = sum(value_list)
        for cate in keywords_dict:
            index = keywords_dict[cate]
            keywords_dict[cate] = float(format(index/total_value,'.3f'))


if __name__ == '__main__':

    start = time()
    labels = []
    corpus = []
    getkeywords = Getkeywords()
    getkeywords.getCate()
    # getkeywords.getCorpus("corpus_del_uninformative.txt",labels,corpus)
    getkeywords.getCorpus("D:/npm_keywords/final_experiment/train_data_intro.txt", labels, corpus)
    labelset = list(set(reduce(list.__add__, labels)))
    print(labelset)
    cate_dict = dict()
    for  i in range(0,1):
        keywords = getkeywords.getKeywords(labelset,labels,corpus,cate_dict)
        labelset.remove('common')

    del keywords['common']
    result_dict = dict()
    for category in keywords:
        keywords4cate = str()
        keywords4cate = '[' + category +']'
        print(keywords4cate)
        keywords_set = keywords[category]
        for word in keywords_set.keys():
            probability_list = keywords_set[word]
            keywords_set[word] = getkeywords.getMean(probability_list,1)

        # 删除类别词和重复词，再排序
        getkeywords.dealKeywords(keywords[category],category)
        # 对概率降序排列输出字典
        list_1 = list(keywords[category].items())
        my_dict_sortbyvalue = dict(sorted(list_1, key=lambda x: x[1],reverse=True)[:50])        # 取前30个词
        # 标准化权重
        getkeywords.nomarlizeWeight(my_dict_sortbyvalue)
        print(my_dict_sortbyvalue)
        result_dict[category] = my_dict_sortbyvalue

    # with open('keywords_del_uninformative_100iter.json', 'w') as json_file:
    #     json.dump(result_dict, json_file)
    with open('D:/npm_keywords/final_experiment/keywords_50.json', 'w') as json_file:
        json.dump(result_dict, json_file)

    print('Cell took %.2f seconds to run.' % (time() - start))