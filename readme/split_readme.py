import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import couchdb



class SplitReadme:
    def __init__(self,name):
        self.name = name
        self.Introduction = ''
        self.Feature = ''
        self.Usage = ''
        self.Code = ''


    def restore(self,wordset):
        newset = set()
        wnl = WordNetLemmatizer()
        for word in wordset:
            word = wnl.lemmatize(word.lower(), wordnet.NOUN)
            newset.add(word)
        return newset


    def firstLevel(self,readme):   # 按照 readme 中最高级别的标题进行划分
        title_rule_1 = re.compile('\n\s#[#]* |\r\n#[#]* ')
        position_1 = -1
        if title_rule_1.search(readme) is not None:
            position_1 = title_rule_1.search(readme).span()[0]
        title_rule_2 = re.compile(r'(.*?)\n---[-]*\n')
        position_2 = -1
        if title_rule_2.search(readme) is not None:
            position_2 = title_rule_2.search(readme).span()[0]

        if position_1 == -1 or (position_2 != -1 and position_2 < position_1):  # 同时查找 # 和 ----的位置，谁的位置靠前以谁进行划分
            split_line = re.compile(r'(.*?)\n---[-]*\n')
            readme_segment = re.split(split_line,readme)
            section = len(readme_segment)
            if section % 2 == 0:
                count = 0
            else:
                count = 1
            while count <= section/2:
                title = readme_segment[count]
                readme_segment.remove(title)
                readme_segment[count] = title+' '+readme_segment[count]
                count += 1
        else:
            level_1 = re.compile(r'\n\s# |\r\n# ')
            level_2 = re.compile(r'\n\s## |\r\n## ')
            level_3 = re.compile(r'\n\s### |\r\n### ')
            level_4 = re.compile(r'\n\s#### |\r\n#### ')
            readme_segment = re.split(level_1, readme)
            if len(readme_segment) == 1:        # 没有一级标题
                readme_segment = re.split(level_2, readme)
                if len(readme_segment) == 1:    # 没有二级标题
                    readme_segment = re.split(level_3, readme)
                    if len(readme_segment) == 1:
                        readme_segment = re.split(level_4,readme)
        return readme_segment

    def delete_format(self,readme):
        # 删除 markdown 图片，五种不同形式的markdown 图片,顺序不可换
        readme = re.sub(r'\[(<(.*?)>)\]\((.*?)\)', '', readme)      # [<img>](http://)
        readme = re.sub(r'\[(?:!\[(.*?)\]\((.*?)\))\]\((.*?)\)','',readme)  #[![npm version](http://image)](http://)
        readme = re.sub(r'\[(?:!\[(.*?)\]\((.*?)\))\]\[(.*?)\]','',readme)    # [![npm version](http://image)][url]
        readme = re.sub(r'!\[(.*?)\]\((.*?)\)', '', readme)              # ![test](http://)
        readme = re.sub(r'(\*|-|\+|) \[(.*?)\]\((.*?)\)','',readme)             # * [test](http://) 或者 - [test](http://) 列表


        readme = re.sub(r'\[(.*?)\]:(.*?)\n','',readme)             # [tests]: http://img
        readme = re.sub(r'\[(?:!\[(.*?)\]\[(.*?)\])\]\[(.*?)\]','',readme) # [![tests][tests]][test-url]

        # 删除 html 格式
        readme = re.sub(r'</?\w+[^>]*>', '', readme)
        rule = re.compile('[a-zA-Z]|#')         # 找第一个非空字符，删掉之前的换行符
        start = re.search(rule, readme).span()[0]
        if start != 0:
            readme = readme[start:]
        return readme

    def split_readme(self,readme):
        readme = self.delete_format(readme)
        # print(readme)
        readme_segment = self.firstLevel(readme)
        pattern_title = re.compile(r'\A.*')         # 只匹配第一行的内容，即标题
        pattern_code = re.compile(r'```([a-z]*[\n|\r\n][\s\S]*?\n)```')    # 匹配代码
        del_title = {'installation', 'license', 'people', 'contributing','table','contributor',
                     'optional','maintainer','setting','provider','test','download','development',
                     'install','installing','contribute','tank','documentation','document','start','community',
                     'note','changelog','pattern','option','copyright','credit','author','contact','backer','sponsor'}
        intro_title = {'introduction','description','overview',self.name}
        usage_tilte = {'usage','api','parameter','specifier','example'}
        if not readme_segment[0]:
            readme_segment.remove(readme_segment[0])
        self.Introduction = readme_segment[0]
        readme_segment.remove(self.Introduction)

        # intro_code = re.findall(pattern_code,self.Introduction)
        # if intro_code:
        #     self.Introduction.remove(intro_code)
        #     self.Code += intro_code

        for segment in readme_segment:
            title = re.findall(pattern_title,segment)
            if not title:
                continue
            title_word = set(title[0].split())
            title_word = self.restore(title_word)
            if title_word & intro_title:                    # 若接下来的部分中含有Introduction , description , package name， 则这一部分也该被分为 Introduction
                self.Introduction += segment
                continue
            if title_word & del_title:      # 删除无用的部分，如 Installation 等
                continue
            code = re.findall(pattern_code,segment)  # 匹配代码部分
            if code :
                for c in code:
                    self.Code += c  # 将所有代码汇总到 Code 中
                del_code = re.sub(pattern_code,'',segment)
                self.Usage += del_code   # 除去 code 的文字汇总到 Usage
            else:
                if title_word & usage_tilte:  # 虽然里面没有代码但是标题是 usage title
                    self.Usage += segment
                else:
                    self.Feature += segment
        self.Introduction = re.sub(pattern_code,'',self.Introduction)


    def getIntroduction(self):
        return self.Introduction
    def getFeature(self):
        return self.Feature
    def getUsage(self):
        return self.Usage
    def getCode(self):
        return self.Code
    def getName(self):
        return self.name

if __name__=="__main__":

    server = couchdb.Server('http://wangyu:wangyu.com123@localhost:5984/')
    db_source = server['registry']
    package = db_source['pen']
    readme = package['readme']
    # print(readme)

    part_readme = SplitReadme('express')
    part_readme.split_readme(readme)
    # print(part_readme.getIntroduction())
    intro = part_readme.getIntroduction()
    print(intro)


    # print('===========')
    # print(part_readme.getCode())
    print('===========')
    print(part_readme.getFeature())
    print('===========')
    print(part_readme.getUsage())



