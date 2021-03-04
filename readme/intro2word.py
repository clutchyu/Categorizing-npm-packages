from readme.text2word import TextToWord
import re

class IntroToWord:
    def __init__(self,intro):
        self.intro = intro

    def removeUseless(self):
        pattern_1 = re.compile(r'\[(.*?)\]')
        pattern_2 = re.compile(r'<(.*?)>')
        intro_change = re.sub(pattern_1,'',self.intro)
        return re.sub(pattern_2,'',intro_change)

    def processIntro(self):
        return TextToWord(self.removeUseless()).processText()


if __name__ == '__main__':
    readme = "<p align=\"center\" style=\"text-align: center\"><img src=\"https://raw.githubusercontent.com/ethanent/phin/master/media/phin-textIncluded.png\" width=\"250\" alt=\"phin logo\"/></p>\n\n---\n\n> The ultra-lightweight Node.js HTTP client\n\n[Full documentation](https://ethanent.github.io/phin/) | [GitHub](https://github.com/ethanent/phin) | [NPM](https://www.npmjs.com/package/phin)\n\n\n"
    intro = IntroToWord(readme)
    print(readme)
    print(intro.processIntro())

