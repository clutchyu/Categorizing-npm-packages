import couchdb
import re
from readme.text2word import TextToWord
# 找出可以作为 L-LDA 输入的包， 条件为包的 tag 词同时存在于 description 中
# 找出的包存入数据库中

server = couchdb.Server('http://wangyu:wangyu.com123@localhost:5984/')
db_source = server['registry']
db_target = server['llda_new_corpus']

class getData:

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

    def deterPacakge(self,tag_list,description_word_list):
        cate_list = list()
        phrase = {'file system','command line'}
        phrase_interset = phrase & set(tag_list)
        if len(phrase_interset) > 0:
            if 'file system' in phrase_interset:
                tag_list.remove('file system')
                tag_list.append('file_system')
            elif 'command line' in phrase_interset:
                tag_list.remove('command line')
                tag_list.append('command_line')

        for cate in self.cate_dict.keys():
            cate_tag = set(self.cate_dict[cate]) & set(tag_list)        # 类别 seed words 与 包的tag 的交集
            cate_description = set(self.cate_dict[cate]) & set(description_word_list)   # 类别 seed words 与 包的 description word 的交集
            if  len(cate_tag) == 0 and len(cate_description) == 0 :
                continue
            if  len(cate_tag) > 0 and len(cate_description) > 0 :    # 两个交集同时不为空，说明 tag 和 description 中都能匹配到cate 的 seed words  , 无论是否相同，都是属于这个类的，例如 fs  file
                cate_list.append(cate)
            else:       # tag 与 description 中包含的类别并不能对应
                return []
        return cate_list

if __name__=="__main__":
    getdata = getData()
    getdata.getCate()
    cate_counter = dict()
    for package_name in db_source:
        package = db_source[package_name]
        if 'keywords' not in package:
            continue
        keywords = package['keywords']
        if 'description' not in package:
            continue
        description = package['description']
        if len(keywords) == 0 or description is None:
            continue
        description_words = TextToWord(description).processText()
        cate_list = getdata.deterPacakge(keywords,description_words)

        if len(cate_list) > 0:  # 能够对应， 插入数据库
            # doc = {'_id':package_name,'name':package_name,'keywords':keywords,'description':description,'readme':package['readme']}
            for cate in cate_list:      # 计数
                if cate in cate_counter:
                    cate_counter[cate] += 1
                else:
                    cate_counter[cate] = 1
            del package['_rev']   # 删除版本号，添加到新的数据库时会赋予其新的版本号 ，或者就把有用的信息拿出来形成一个新的doc
            package['category'] = cate_list
            db_target.save(package)

    print(cate_counter)



# 在新的数据库文档中加一个字段 ， category ，这样为下一步的输入作了准备

