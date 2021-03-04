from readme.code2word import CodeToWord
from readme.intro2word import IntroToWord
from readme.feature2word import FeatureToWord
from readme.usage2word import UsageToWord
from readme.split_readme import SplitReadme
import os
import nltk
from collections import Counter
import couchdb
import json

class ReadmeToWord:
    def __init__(self,SplitReadme):
        self.intro = SplitReadme.getIntroduction()
        self.featrue = SplitReadme.getFeature()
        self.usage = SplitReadme.getUsage()
        self.code = SplitReadme.getCode()

        # with open('C:/Users/Admin/PycharmProjects/WMD/readme/readme_code_identifier.json', 'r') as json_file:
        #     dic = json.load(json_file)
        # package_name = SplitReadme.getName()
        # if package_name in dic:
        #     self.code = dic[SplitReadme.getName()]
        # else:
        #     self.code = ''


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



if __name__=="__main__":
    # directory = 'D:/dataset/description-tag/totest_1/'
    # filenames = ['del','filehound','filesize','file-stream-rotator','file-type','find-up','node-dir','superstatic','trash','vfile']
    # filenames = ['axios','follow-redirects','http-parser-js','http-proxy-agent','http-shutdown','http-status','morgan','needle','popsicle','socks-proxy-agent']
    # filenames = ['@connectedcars_logutil','abstract-logging','fancy-log','frontail','gitlog','log','logt','nimble-logging','simple-node-logger','webpack-log']
    # filenames = ['call-me-maybe','delay','fildes','p-map','pn','p-retry','promise-ployfill','promise-retry','q','tmp-promise']
    # filenames = ['archiver','end-of-stream','event-stream','gulp','isstream','sorted-union-stream','stream-browserify','stream-http','streamroller','through']
    # filenames = ['anymatch','cli-truncate','get-stream','magic-string','pad','query-string','querystringify','repeat-string','slice-ansi','split-on-first']
    # filenames = ['autolinker','build-url','encodeurl','normalize-url','parse-domain','query-string','urijs','url-assembler','url-pattern','valid-data-url']
    #filenames = ['bms-query-string','droppy','firstline','get-uri','json-stringify-safe','laabr','logrotate-stream','nock','phin','pino-toke','promise-readable','protocolify','requires-port','responselike','roarr','rotating-file-stream','rsvp',
      #           'sformat','stream-promise','strtok3','Table','tar-fs','tinyurl','tracer','write-file-atomic']
    # filenames = ['@hapi_wreck','cacheable-request','chokidar','Consola','console-log-level','embedza','flashheart',
    #             'fs-jetpack','global-agent','graceful-fs','make-dir','multistream','peek-stream',
    #             'readable-stream','signale','speakingurl','storyboard','stream-combiner2','tempy','winston']

    # for name in filenames:
    #     readme = ReadmeToWord(directory+name)
    #     readme_token = readme.readme2word()
    #     print(readme_token)
    #     collect_file = directory + 'word.txt'
    #     with open(collect_file, 'a') as file_object:
    #         for word in readme_token:
    #             file_object.write(word + ' ')
    #         file_object.write('\n')

    server = couchdb.Server('http://wangyu:wangyu.com123@localhost:5984/')
    db_source = server['registry']
    package = db_source['tmpin']
    readme = package['readme']
    if len(readme) == 0:
        print("No readme in this package")
    else:
        part_readme = SplitReadme('express')
        part_readme.split_readme(readme)
        readme = ReadmeToWord(part_readme)
        weight_list = [0.4,0.3,0.2,0.1]
        readme_list = readme.readme2word()
        print(readme_list)

        list_1 = list(readme.getScore(readme_list,weight_list).items())
        my_dict_sortbyvalue = dict(sorted(list_1, key=lambda x: x[1], reverse=True))
        print(my_dict_sortbyvalue)





