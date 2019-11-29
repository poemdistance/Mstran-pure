from bs4 import BeautifulSoup
from termcolor import cprint
import time
import logging
import requests
from bdtran import HeadersSource
from bdtran import GetSignature
import urllib
import json
import re
import math

class Translator(object):

    def __init__(self):

        #logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(message)s')

        self.baseurl = "https://fanyi.baidu.com/"
        self.asyncurl = "https://fanyi.baidu.com/sug"
        self.audiourlen = "https://fanyi.baidu.com/gettts?lan=en&spd=3&source=web&text="
        self.audiourluk = "https://fanyi.baidu.com/gettts?lan=uk&spd=3&source=web&text="
        self.wordurl = "https://fanyi.baidu.com/sug/?kw="
        self.advancedurl = "https://fanyi.baidu.com/v2transapi/?simple_means_flag=3&transtype&query="
        self.correcttxtcb = 'https://correctxt.baidu.com/correctxt?ie=utf-8&version=0&from=FanyiWeb&text='
        self.clickurl = "https://click.fanyi.baidu.com/?src=1&locate=zh&action=query&type=1&page=1"

        self.wordFormTable = { 'word_third':'三单形式','word_er':'比较级','word_est':'最高级','word_ing':\
                '现在分词','word_pl':'复数','word_past':'过去式','word_done':'过去分词', 'word_proto':'的最高级'};

        self.session = requests.Session()

        #All resource get from server will be stored here
        self.retryCon = 0
        self.time = time.time()
        self.establish = False;
        self.isupdateheaders = False;
        self.isword = False;
        self.ischinese = False
        self.only1result = False;
        self.audiouk = None;
        self.audioen = None;
        self.response = None;
        self.from2where = None;
        self.enTrans = [];
        self.zhTrans = [];
        self.phonetic = [];
        self.synonym = set() ;
        self.example = [];
        self.pos = [];
        self.wordForm = []
        self.didyoumean = None
        self.keywords = []

    def getKeywords(self, data):

        self.keywords.clear()

        try:
            group = []
            for word in data['trans_result']['keywords']:

                group.clear()

                group.append(word['word'])
                group.append(word['means'])

                self.keywords.append(group[:])
        except Exception as e:
            logging.info('Capture error in getKeywords:'+str(e))


    def getOtherWordForm(self, data):

        self.wordForm.clear()

        try:
            for form in data['dict_result']['simple_means']['exchange']:
                if form == 'word_proto':

                    self.wordForm.append(\
                     str([e for e in  data['dict_result']['simple_means']['exchange'][form]])+\
                     self.wordFormTable[form])

                    continue

                self.wordForm.append(
                    (self.wordFormTable[form]+':'+\
                    data['dict_result']['simple_means']['exchange'][form][0]))

        except Exception as e:

            logging.info('Capture error in getOtherWordForm: '+str(e))


    def correctTextCallback(self, word):

        self.didyoumean = None

        try:
            #记得更新headers，不然无法获取到数据
            self.session.headers.update(HeadersSource.getCorrecttxtHeaders())
            self.isupdateheaders = False

            try:
                data = self.session.get(self.correcttxtcb+urllib.parse.quote(word), timeout=1)
            except KeyboardInterrupt as e:
                cprint(str(e), 'red')
                exit(0)

            data = data.json()

            if data['errmsg'] == 'NoError':
                return None
            elif data['errmsg'] == 'OK':
                return data['correctxt']
            else:
                logging.info('Something wrong happened in correctTextCallback func')
        except Exception as e:
            logging.info('Capture error in correctTextCallback:'+str(e))

    #获取音标
    def getPhonetic(self, data):

        self.phonetic.clear()

        try:
            usPhonetic = data['dict_result']['simple_means']['symbols'][0]['ph_am']
            if usPhonetic: self.phonetic.append('美:['+usPhonetic+']')

            enPhonetic = data['dict_result']['simple_means']['symbols'][0]['ph_en']
            if enPhonetic: self.phonetic.append('英:['+enPhonetic+']')
        except Exception as e:
            logging.info('Capture error in getPhonetic:'+str(e))

    def getSynonym(self, data):
        self.synonym.clear()
        try:
            for item in data['dict_result']['edict']['item'][0]['tr_group']:
                synonym = item['similar_word']
                if synonym:
                    for word in synonym:
                        self.synonym.add(word)
        except Exception as e:
            logging.info('Capture error in getSynonym:'+str(e))

    def getExample(self,data,Input):
        self.example.clear()
        try:
            for item in data['dict_result']['edict']['item'][0]['tr_group']:
                example = item['example']
                for e in example:
                    if e and Input in e: self.example.append(e)
        except Exception as e:
            logging.info('Capture error in getExample:'+str(e))

    def getPartOfSpeech(self,data):
        self.pos.clear()
        try:
            for item in data['dict_result']['simple_means']['symbols'][0]['parts']:
                pos = item['part']
                if pos : self.pos.append(pos)
        except Exception as e:
            logging.info('Capture error in getPartOfSpeech:'+str(e))

    def getEnglishTranslatrion(self,data):
        self.enTrans.clear()
        group = []
        try:
            data = data['dict_result']['oxford']['entry'][0]['data'][1]['data']
        except (IndexError,TypeError) as e:
            try:
                data = data['dict_result']['oxford']['entry'][0]['data'][0]['data']
            except (IndexError,TypeError) as e:
                logging.info('Capture error in getEnglishTranslatrion pos 1:', e)

        except KeyError as e:
            logging.info('Capture error in getEnglishTranslatrion pos 2:'+str(e))
            return


        for i,item in enumerate(data):

            if i == 0: continue
            if i == len(data)-1: break

            group.clear()
            try:
                group.append(item['data'][0]['enText'])
                group.append(item['data'][0]['chText'])
            except (KeyError, IndexError, TypeError):
                continue

            try:
                group.append(item['data'][1]['data'][0]['enText'])
                group.append(item['data'][1]['data'][0]['chText'])
            except (KeyError , IndexError) as e:
                try:
                    group.append(item['data'][1]['data'][1]['enText'])
                    group.append(item['data'][1]['data'][1]['chText'])
                except (IndexError , KeyError) as e:
                    pass

            # Need to be a deep copy, so use '[:]'
            self.enTrans.append(group[:])

    def getTranslationResults(self,data):

        self.zhTrans.clear()

        try:
            for result in data['dict_result']['simple_means']['symbols'][0]['parts']:
                means = result['means']
                if means:
                    if not self.ischinese:

                        #针对百度翻译中的乱码而设计
                        if '𤟥' in means[0]:
                            means = means[0].replace('𤟥', '缇犬')

                        if '𧴌' in means[0]:
                            means = means[0].replace('𧴌', '香猫')

                        self.zhTrans.append(means)
                    else:
                        for e in means:
                            self.zhTrans.append(e['word_mean'])
        except TypeError:
            pass

        if not self.zhTrans:
            result = data['trans_result']['data'][0]['dst']
            if result:
                self.zhTrans.append(result)


    def decodeInfo(self):
        print('Data get from advanced url:')
        print(" data['liju_result'] decode method:")
        print("  ")
        print(str(data['liju_result']['double'])
                .encode('utf-8').decode('unicode-escape'))
        #Do not need decode
        print(str(data['liju_result']['tag']))

        print(str(data['liju_result']['single'])
                    .encode('utf-8').decode('unicode-escape'))

    def getAudiolink(self, word):
        self.audioen = self.audiourlen+urllib.parse.quote(word)
        self.audiouk = self.audiourluk+urllib.parse.quote(word)

    def establishConnection(self):

        try:
            #establish connection through two get requests with different headers
            self.session.get(self.baseurl, headers=HeadersSource.getHeaders0(), timeout=1)
            self.response = self.session.get(self.baseurl, headers=HeadersSource.getHeaders1(), timeout=1)
        except Exception as e:
            if self.retryCon <= 5:
                cprint('In establishConnection:'+str(e), 'red')

            if self.retryCon <= 10:
                self.retryCon += 1

            time.sleep(self.retryCon*0.2)
            self.establishConnection()

        #链接成功，失败尝试次数归零
        self.retryCon = 0

        #Get the token and gtk value from html content
        result = self.response.content.decode('utf8')
        self.token = re.findall(r'token:.+?([\w]+)\',',result)[0]
        self.gtk = re.findall(r'window\.gtk.+?([\d]+\.[\d]+)\';', result)[0]

        self.establish = True

    def isContainChinese(self,Input):

        self.ischinese = False

        for ch in Input:
            if '\u4e00' <= ch <= '\u9fa5':
                self.ischinese = True
                return True

        return False

    def getSentenceUrl(self, sentence):
        return self.advancedurl+urllib.parse.quote_plus(sentence)+"&sign="+\
                urllib.parse.quote_plus(self.sign)+"&token="+urllib.parse.quote_plus(self.token)\
                +self.from2where

    def getWordUrl(self, Input):
        return self.wordurl+urllib.parse.quote(Input)

    def isWord(self, Input):
        result = re.findall(r'\b\w+\b', Input)

        self.isword = False

        if len(result) == 1:
            self.isword = True
            return True

        return False

    def selectUrl(self, Input, specific=""):

        self.from2where = '&from=zh&to=en'\
           if self.isContainChinese(Input) else '&from=en&to=zh'

        #Get the singnature first
        self.sign = GetSignature.getSign(Input, self.gtk)

        if self.isWord(Input):

            #return advanced url if contain chinese
            #which length more than 2 characters
            if self.isContainChinese(Input):
                if len(Input) > 2:
                    return self.getSentenceUrl(Input), "advanced"

            #Storage the audio link if input is a word of English
            self.getAudiolink(Input)

            #Just return the advanced url if type 'advanced' \
            #has been specificed
            if specific == 'advanced':
                return self.getSentenceUrl(Input), "advanced"

            return self.getWordUrl(Input), "base"

        #Not a word, need to use advanced url to get the translation
        else:
            return self.getSentenceUrl(Input), "advanced"

    def getTran(self, Input, specific=""):

        self.example.clear()
        self.enTrans.clear()
        self.wordForm.clear()
        self.keywords.clear()
        self.synonym.clear()
        self.zhTrans.clear()
        self.phonetic.clear()
        self.pos.clear()
        self.audioen = None
        self.audiouk = None

        if not self.establish:
            self.establishConnection()

        url, urltype = self.selectUrl(Input, specific)

        #self.session.headers.update(HeadersSource.getClickHeaders())
        #self.isupdateheaders = False
        #self.session.get (self.clickurl, timeout=1)

        try:
            data = self.session.get(url, timeout=1, headers=HeadersSource.getHeadersForV2tranapi())
        except KeyboardInterrupt as e:
            cprint(str(e), 'red')
            exit(0)

        if data.content:
            data = data.json()
        else:
            cprint('百度翻译获取数据为空<In BdTran.py>, You must be handle it, exit...!', 'red');
            #exit(0) "这里不应该退出..."
            #TODO
            return None, None

        if urltype != 'advanced' and data['errno'] == '1':
            self.getTran(Input, 'advanced')

        if urltype == 'advanced':

            if 'dict_result' in data and len(data['dict_result']) > 0 and \
                    'simple_means' in data['dict_result']:

                self.getPhonetic(data)
                self.getSynonym(data)
                self.getExample(data, Input)
                self.getPartOfSpeech(data)
                self.getEnglishTranslatrion(data)
                self.getOtherWordForm(data)
                self.getTranslationResults(data)

                if self.isword:
                    didyoumean = self.correctTextCallback(Input)
                    if didyoumean != Input:
                        self.didyoumean = didyoumean
                else:
                    try:
                        self.getKeywords(data)
                    except Exception as e:
                        logging.info( 'Capture error in getTran:'+str(e))
                        pass

                    self.only1result = True
            else:
                self.zhTrans.append ( data['trans_result']['data'][0]['dst'] )


        return data, urltype
