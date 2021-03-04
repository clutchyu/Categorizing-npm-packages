from nltk.corpus import stopwords,wordnet
from nltk.stem import WordNetLemmatizer
from nltk import  pos_tag
import nltk
import os
import re

def getStopWords():
    with open('C:/Users/Admin/Documents/我的坚果云/NPM_Cate/material/nodejs-globals-keywords',encoding="utf-8") as files:
        stop_words_node = files.read()
    with open('C:/Users/Admin/Documents/我的坚果云/NPM_Cate/material/javascript-keywords',encoding="utf-8") as files:
        stop_words_javascript = files.read()
    with open('C:/Users/Admin/Documents/我的坚果云/NPM_Cate/material/delete-words',encoding="utf-8") as files:
        delete_words_list = files.read()
    delete_words = delete_words_list.split()
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    stop_words_code = set(tokenizer.tokenize(stop_words_node)).union(set(tokenizer.tokenize(stop_words_javascript)))
    stop_words_code = stop_words_code.union(set(delete_words))
    stop_words = set(stopwords.words('english')).union(stop_words_code)
    return stop_words
stopwords = getStopWords()

class CodeToWord:
    def __init__(self,code):
        self.code = code
        self.stopwords = stopwords

    # 获取单词的词性
    def get_wordnet_pos(self,tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    def removeUseless(self,code):
        #1.去除引号内的内容 2.去除数字 3.去除url
        pattern = re.compile(r'(\'|\")(.*?)\1')
        pattern2 = re.compile(r'([1-9]\d*\.?\d*)|(0\.\d*[1-9])')
        pattern3 = re.compile(r"((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?")
        code_nomark = re.sub(pattern,'',code)
        code_nonumber = re.sub(pattern2,'',code_nomark)
        code_done = re.sub(pattern3,'',code_nonumber)
        return code_done

    def lower(self,tokenlist):
        token_list = []
        for w in tokenlist:
            token_list.append(w.lower())
        return token_list

    def processCode(self):
        code_preprocess = CodeToWord.removeUseless(self,self.code)  # 预处理
        tokenizer = nltk.RegexpTokenizer(r"\w+")
        code_token = CodeToWord.lower(self,set(tokenizer.tokenize(code_preprocess)))  # 转成 token,并去重
        filtered_sentence = [w for w in code_token if not w in self.stopwords]
        # print(filtered_sentence)

        tagged_sent = pos_tag(filtered_sentence)  # 获取单词词性
        wnl = WordNetLemmatizer()
        code_processed = []
        for tag in tagged_sent:
            wordnet_pos = CodeToWord.get_wordnet_pos(self,tag[1]) or wordnet.NOUN
            code_processed.append(wnl.lemmatize(tag[0], pos=wordnet_pos))  # 词形还原

        return code_processed



if __name__=="__main__":
    with open('E:/dataset/code_test', encoding="utf-8") as files:
        code_text = files.read()
    test = CodeToWord(code_text)
    print(test.processCode())


