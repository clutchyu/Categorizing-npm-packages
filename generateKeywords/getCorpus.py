import couchdb
from readme.split_readme import SplitReadme
from readme.intro2word import IntroToWord
import os
import re

server = couchdb.Server('http://wangyu:wangyu.com123@localhost:5984/')
# db_source = server['llda_new_corpus']
# labels = []
# corpus = []
#
# for package_name in db_source:
#     package = db_source[package_name]
#     label_text = str()
#     label = package['category']
#     for item in label:
#         label_text = label_text  + item + ' '
#     description = package['description']
#     if 'readme' in package:
#         readme = package['readme']
#     else:
#         continue        # 没有readme 就不要了
#     if len(readme) == 0 or readme == 'ERROR: No README data found!':
#         continue
#     try:
#         part_readme = SplitReadme(package_name)
#         part_readme.split_readme(readme)
#         intro = part_readme.getIntroduction()
#
#         words = IntroToWord(description+' '+intro).processIntro()
#         if len(words) < 10:
#             continue
#
#         content = '[' + label_text + ']'+ ' '.join(words)
#         # print(package_name)
#         f = open('./corpus_del_uninformative.txt', 'a', encoding='utf-8')
#         f.write(content)
#         f.write('\n')
#     except:
#         pass


def getPackage(path):
    with open(path, encoding="utf-8") as files:
        text = files.readlines()
    pattern = re.compile(r'\[(.*?)\]')
    package_list = []
    for line in text:
        name = re.sub(pattern, ' ', line)
        # words = TextToWord(texts).processText()       # 之前语料库中为description ，现在为处理过的 word
        package_list.append(name.split()[0])

    return package_list

db_source = server['score_data']
labels = []
corpus = []

cate_list = ['number','string','time','collection','text','promise','stream','security','debug','error',
             'fs','http','url','util','cli','documentation','image','loader','log','validation','test',
             'database','framework','authentication','email','parser','typescript','markdown','event']
path = 'D:/npm_keywords/new_experiment/test_data/'
package_list = getPackage(path+'test_package_name.txt')
print(len(package_list))


for package_name in package_list:
    if package_name not in db_source:
        continue
    package = db_source[package_name]
    label_text = str()
    if 'category' not in package:
        continue
    label = package['category']
    for item in label:
        label_text = label_text  + item + ' '
    if 'description' not in package:
        continue
    description = package['description']
    if 'readme' in package:
        readme = package['readme']
    else:
        continue        # 没有readme 就不要了
    if len(readme) == 0 or readme == 'ERROR: No README data found!':
        continue
    try:
        part_readme = SplitReadme(package_name)
        part_readme.split_readme(readme)
        intro = part_readme.getIntroduction()

        words = IntroToWord(description+' '+intro).processIntro()
        if len(words) < 10:
            continue

        content = '[' + label_text + ']'+ ' '.join(words)
        # content = '[' + label_text + ']' + ' ' + package_name
        print(content)
        f = open(path+'test_corpus_intro.txt', 'a', encoding='utf-8')
        f.write(content)
        f.write('\n')
    except:
        pass
