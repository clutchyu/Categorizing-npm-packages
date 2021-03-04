from readme.text2word import TextToWord
import nltk

class UsageToWord:
    def __init__(self,usage,description_token):
        self.usage = usage
        self.description_token = description_token      # description_token = intro_token + feature_token

    # 只出现在 usage 这一部分的类别名应该被剔除
    def removeCateWord(self):
        usage_token = TextToWord(self.usage).processText()
        with open('C:/Users/Admin/Documents/我的坚果云/NPM_Cate/material/category', encoding="utf-8") as files:
            cate_words = files.read()
        tokenizer = nltk.RegexpTokenizer(r"\w+")
        cate4usage = set(usage_token)& set(tokenizer.tokenize(cate_words))
        if cate4usage is None:          # usage 里面没有类别名
            return usage_token
        else:
            for cate in cate4usage:
                if cate not in self.description_token:        # usage 中有类别名但是没有出现在 intro 中
                    while cate in usage_token:
                        usage_token.remove(cate)
            return usage_token

    def processUsage(self):
        stopwords = ['type','boolean','true','false','object','default','option','pattern','return'] # usage 部分独有的 stopwords
        usage_token = self.removeCateWord()
        filtered_token = [w for w in usage_token if not w in stopwords]
        return filtered_token

if __name__=="__main__":
    description_token = ['http','client', 'utility', 'wreck', 'part','string']
    usage = "del(patterns, options?) Returns Promise<string[]> with the deleted paths. del.sync(patterns, options?) Returns string[] with the deleted paths. patterns"

    print(UsageToWord(usage,description_token).processUsage())
