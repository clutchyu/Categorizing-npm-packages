from nltk.corpus import stopwords,wordnet,words
from nltk.stem import WordNetLemmatizer
from nltk import  pos_tag
import nltk
import re
from nltk.tokenize import MWETokenizer,word_tokenize
import string
import json

class TextToWord:
    def __init__(self,text):
        self.text = text

    # 获取单词的词性
    def get_wordnet_pos(self,tag):
        if tag == 'NNP':
            return 'NNP'
        elif tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    def removeUseless(self,text):
        #1.去除数字 2.去除url 3.去除非英文字符
        #pattern = re.compile(r'([1-9]\d*\.?\d*)|(0\.\d*[1-9])')
        pattern1 = re.compile(r"((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?")
        pattern2 = re.compile(r'[^A-Za-z \n[(.*\\!:;\')*?\]]*')
        #text_nonumber = re.sub(pattern,'',text)
        text_nourl = re.sub(pattern1,'',text)  # 去掉url
        text_no_cli = re.sub(r'\$.*','',text_nourl)  # 去掉指令
        text_no_punc = re.sub(r'[^\w\s]',' ',text_no_cli)  # 去除标点
        text_done = re.sub(pattern2,'',text_no_punc)  # 去掉非英文字符
        return text_done

    def lower(self,tokenlist):
        token_list = []
        for w in tokenlist:
            token_list.append(w.lower())
        return token_list

    def processText(self):
        stop_words = set(stopwords.words('english'))
        # tokenizer = nltk.RegexpTokenizer(r"\w+")


        tokenizer = MWETokenizer([('web', 'framework'), ('file', 'system'), ('command', 'line')])  # 针对短语
        text_process = TextToWord.removeUseless(self,self.text)
        # text_token = TextToWord.lower(self,tokenizer.tokenize(text_process)) # 转成 token  不应该先lower，因为pos 的时候会根据大写判断 专有名词
        text_token = tokenizer.tokenize(word_tokenize(text_process))
        text_token = TextToWord.lower(self,text_token)
        filtered_sentence = [w for w in text_token if not w in stop_words]
        # print(filtered_sentence)

        tagged_sent = pos_tag(filtered_sentence)  # 获取单词词性
        wnl = WordNetLemmatizer()
        text_processed = []
        custom_dictionary = ['fs']
        for tag in tagged_sent:
            if tag[0] in custom_dictionary:
                wordnet_pos = 'NNP'
            else:
                wordnet_pos = TextToWord.get_wordnet_pos(self,tag[1]) or wordnet.NOUN
            if wordnet_pos == 'NNP':    # 专有名词不进行还原
                text_processed.append(tag[0])
            else:
                text_processed.append(wnl.lemmatize(tag[0], pos=wordnet_pos))  # 词形还原

        with open('C:/Users/Admin/Documents/我的坚果云/NPM_Cate/material/delete-words',encoding="utf-8") as files:
            delete_words_list = files.read()
        delete_words = delete_words_list.split()

        # with open('C:/Users/Admin/Documents/我的坚果云/NPM_Cate/material/uninformative-words.json', 'r') as json_file:
        #     uninformative_words = json.load(json_file)
        #
        # delete_words = set(delete_words + uninformative_words)

        text_processed = [w for w in text_processed if not w in delete_words]


        return  text_processed       # 最后小写化

if __name__=="__main__":
    sentence = "# 1-liners cli\n\n<p align=\"center\">\n  <img alt=\"Screenshot of the CLI starting\" src=\"https://gist.githubusercontent.com/loklaan/41f5408d99832b9afc011abdb5c0b509/raw/c651c391fb44d6efcf6b487b2fb22c26ca829d17/1-liners-cli.png\" width=\"700px\" />\n</p>\n\n<p align=\"center\">\n  Copy common util functions to clipboard, courtesy of <a href=\"https://github.com/1-liners/1-liners\"><strong><code>1-liners</code></strong></a>\n</p>\n\n## Quick Start\n\n```bash\n$ npx 1-liners-cli\n```\n\n## Keep It Around\n\n```bash\n$ npm install -g 1-liners-cli      # Install globally\n$ 1-liners"
    text2word = TextToWord(sentence)
    print(text2word.processText())


