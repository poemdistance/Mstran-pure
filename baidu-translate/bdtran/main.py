#!/usr/bin/python3

from termcolor import cprint
from bdtran import BdTran
import requests
import time
import sysv_ipc as ipc
import readline
import warnings
import sys

def testOutput(tl):
    print('phonetic:'+str(tl.phonetic))
    print('pos:'+str(tl.pos))
    print('English translation:'+str(tl.enTrans))
    print('synonym:'+str(tl.synonym))
    print('Example:'+str(tl.example))
    print('Translation result:'+str(tl.zhTrans))
    pass

def connectShm():

    warnings.simplefilter("ignore")
    path = "/tmp"
    projectID = 2334
    key = ipc.ftok(path, projectID)
    shm = ipc.SharedMemory(key, 0, 0)
    shm.attach(0,0)

    return shm

def leftIsAllPuntuation(Input):

    for e in Input:
        if 0 <= ord(e) <= 64 or 91 <= ord(e) <= 96 or 123 <= ord(e) <= 127:
           continue
        else:
           return False

    return True
    

def main():

    if useShm:
       shm = connectShm()
       offset = 0
       actualStart = 10

    tl = BdTran.Translator()
    retryConnect = 0
    retryConnectTimes = 0

    while True:

        try:
            #不要清除掉相关标志位，由C语言端来完成即可，
            #不然取词翻译无法获取到结果

            #if useShm:
            #    for i in range(10):
            #        shm.write('0', i);

            if not retryConnect:
                Input = str(input('> '))

            retryConnect = 0

            if time.time() - tl.time > 420:
                tl.session = requests.Session()
                tl.establishConnection()
                tl.time = time.time()

            #skip spaces symbols
            if Input == "" or str.isspace(Input): continue


            if useShm:
                reachLimit = 0
                cprint('百度翻译获取输入: ' + Input[:5000]+'<', 'yellow');

                if len(Input) > 5000:
                    cprint('元数据过长，截取为百度翻译上限5000字符', 'red')
                    reachLimit = 1

                if Input == '@@@@@ ':
                    tl.getTran('@')
                    continue

            #remove punctuation symbols
            if not useShm:
                if 0 <= ord(Input[-1]) <= 64 or \
                   91 <= ord(Input[-1]) <= 96 or \
                   123 <= ord(Input[-1]) <= 127:

                    storage = Input
                    Input = Input[:-1]

                    if leftIsAllPuntuation ( Input ):
                        cprint(storage, 'cyan')
                        continue

                    if not Input:
                        cprint(storage, 'cyan')
                        continue

            #remove punctuation symbols.Reading from pipe line would get extra space symbol .
            #so its length would be big one byte than the situation when do not read from pipe line
            if useShm and not reachLimit:
                if 0 <= ord(Input[-2]) <= 64 or \
                   91 <= ord(Input[-2]) <= 96 or \
                   123 <= ord(Input[-2]) <= 127:

                    storage = Input
                    Input = Input[:-2]

                    if not Input or leftIsAllPuntuation(Input):
                        cprint('left is all puntuantioins', 'red')
                        shm.write('||'+storage+'|||', actualStart)
                        shm.write('1', 0)
                        continue

        except (KeyboardInterrupt, EOFError):
            cprint('Good bye~', 'cyan')
            exit(0)


        try:
            data, urltype = tl.getTran(Input[:5000], 'advanced')
            retryConnectTimes = 0

            if data is None:
                #Write empty content
                shm.write("|||||||", actualStart)
                shm.write('1', 0)
                continue

        except Exception as e:
            cprint('Error in main:'+str(e), 'red')

            #if "timed out" in str(e) or "Failed" in str(e):
            tl.session = requests.Session()
            tl.establishConnection()
            tl.time = time.time()
            retryConnect = 1

            if retryConnectTimes <= 4:
                retryConnectTimes += 1

            time.sleep(retryConnectTimes * 0.3)
            #if retryConnectTimes <= 10:
            continue
            #end if

            cprint('Captured error, exit...')

            if useShm:
                shm.write('4', 0)
                shm.detach();

            exit(1)

        offset = 0

        if tl.isword:
            if not useShm:
                cprint('\n    '+Input, 'yellow', end='');
                if tl.phonetic:
                    cprint('\n      |--', 'yellow', end='')
                for ph in tl.phonetic:
                    cprint(ph, 'yellow', end='  ')
                print()

            elif useShm:

                shm.write('0', 1)
                string = Input+'|'
                shm.write(string, actualStart)
                offset = len(string.encode('utf8'))
                #print(string))
                
                if tl.phonetic:
                    string = ""
                    for p in tl.phonetic:
                        string +=  '   ' + p
                        
                    string += '|'
                    shm.write(string, actualStart+offset)
                    offset += len(string.encode('utf8'))

                    shm.write('1', 1)
                    #print(string))
                else:
                    string = '|'
                    shm.write(string, actualStart+offset)
                    offset += len(string.encode('utf8'))
                    shm.write('0', 1)

        elif useShm:
            string = '||'
            shm.write(string, actualStart+offset)
            offset += len(string.encode('utf8'))
            shm.write('0', 1)

        if tl.zhTrans:
            if not useShm:
                print()
                num = 0
                for i, words in enumerate(tl.zhTrans):
                    if tl.pos and len(tl.pos) > i:
                        cprint('    '+tl.pos[i]+' ', 'cyan', end='')
                    else:
                        print('    ', end='')
                    if not tl.isword:
                        if isinstance(words, list):
                            for i, word in enumerate(words):
                                cprint(word, 'cyan', end='')
                                if i < len(words) -1 :
                                    cprint('',end=', ')
                        else:
                            cprint(words, 'cyan')
                    elif tl.ischinese:
                            cprint(words, 'cyan', end='.')
                            num += 1
                            if num == 5:
                                print()
                    elif not tl.didyoumean:
                        if len(words) > 1 and isinstance(words, list):
                            for word in words:
                                cprint(word, 'cyan', end=', ')
                        elif isinstance(words, list):
                            cprint(words[0], 'cyan')
                        else: 
                            cprint(words, 'cyan')
                    else:
                        cprint(words, 'cyan')

                    if not tl.ischinese:
                        print()
            else:

                if not tl.isword:
                    num = 1

                    string = ""
                    if isinstance(tl.zhTrans[0], list):
                        for i,tran in enumerate(tl.zhTrans):
                            if i < len(tl.pos):
                                string += tl.pos[i]
                            for i, word in enumerate(tran):
                                string += word
                                if i < len(tran) - 1:
                                    string += '. '

                            string += '|'
                            num = num + 1

                    else: 
                        string = tl.zhTrans[0] + '|'

                    shm.write(string, offset+actualStart)
                    #print(string))
                    offset += len(string.encode('utf8'))

                    #Numbers of zhTrans = 1
                    shm.write(str(num),2)

                elif not tl.ischinese:
                    if tl.didyoumean:
                        string = tl.zhTrans[0][0] + '|'
                        string += 'Did you mean: ' + tl.didyoumean + '|'
                        shm.write(string, offset+actualStart)
                        #print(string))
                        offset += len(string.encode('utf8'))

                        #Numbers of zhTrans = 1
                        shm.write('1',2)

                    else:
                        string = ""
                        for i, words in enumerate(tl.zhTrans):
                            if tl.pos and len(tl.pos) > i:
                                string += tl.pos[i]
                            if len(words) > 1 and isinstance(words, list):
                                for j, word in enumerate(words):
                                    if j < len(words) - 1:
                                        string += word + ','
                                    else:
                                        string += word + '.'
                            elif isinstance(words, list): string += words[0] + '. '
                            else: string += words + '. '

                            string += '|'

                        shm.write(string, actualStart+offset)
                        offset += len(string.encode('utf8'))

                        #Numbers of zhTrans = i+1
                        shm.write(str(i+1),2)

                #Chinese ->  English
                else:
                    string = ""
                    for i, words in enumerate(tl.zhTrans):
                        string += words + '. '
                        if i >= 5: break;

                    string += '|'
                    shm.write(string, actualStart+offset)
                    offset += len(string.encode('utf8'))

                    #Numbers of Trans = 1
                    shm.write('1',2)




        if tl.enTrans:
            if not useShm:
                cprint('\n    英语释义:    ', 'blue')
                for j, result in enumerate(tl.enTrans):
                    #cprint('      |-'+str(result), 'blue');
                    for i, item in enumerate(result):
                        if i == 0:
                            cprint('      |- '+item, 'blue', end='')
                        if i == 1:
                            cprint('   '+item, 'blue')
                        if i == 2:
                            cprint('      | |_'+item, 'blue')
                        if i == 3:
                            cprint('      |   |_'+item, 'blue', end='\n\n')

                    if j == 4: break;
            else:
                string = ""

                shm.write('0',3)
                
                num = 0;

                if tl.enTrans:
                    for j, result in enumerate(tl.enTrans):
                        #cprint('      |-'+str(result), 'blue');
                        for i, item in enumerate(result):
                            if len(result) == 4:
                                if i == 2:
                                    string += item + ' ('
                                if i == 3:
                                    string += ' '+item +' )' + '|'
                                num = 1
                            elif len(result) == 1:
                                string += item + '|'
                                num = 1
                            elif len(result) == 2:
                                if i == 0:
                                    string += item + ' ('
                                if i == 1:
                                    string += ' '+item +' )' + '|'
                                num = 1

                        break;

                    shm.write(string, actualStart+offset)
                    offset += len(string.encode('utf8'))

                    #Numbers of enTrans = 1+i
                    shm.write(str(num),3)

        elif useShm:

            string = "|"
            shm.write(string, actualStart+offset)
            offset += len(string.encode('utf8'))

            #Numbers of enTrans = 1+i
            shm.write('0',3)

        if tl.example:
            if not useShm:
                print()
                cprint('    例句:'+tl.example[0] )

        if tl.synonym:
            if not useShm:
                cprint('\n    相似词:','green', end='')
                for word in tl.synonym:
                    cprint(word, 'green', end=', ')
                print()

        if tl.wordForm:
            if not useShm:
                cprint('\n    '+str(tl.wordForm), 'green')
            else:
                shm.write('0',4)
                string = str(tl.wordForm) + '|'
                shm.write(string, actualStart+offset)
                #print(string))
                offset += len(string.encode('utf8'))

                shm.write('1',4)

        elif useShm:

            string = "|"
            shm.write(string, actualStart+offset)
            offset += len(string.encode('utf8'))

            #Numbers of enTrans = 1+i
            shm.write('0',4)

        if tl.didyoumean:
            if not useShm:
                cprint('\n    Did you mean:'+tl.didyoumean,'green')

        if tl.keywords:
            if not useShm:
                cprint('\n    关键词:', 'green')
                for keyword in tl.keywords:
                    cprint('      '+str(keyword), 'green')
        
        if not useShm:
            print()

        if useShm:
            num = '0'
            shm.write('0', 5)
            if tl.audioen or tl.audiouk:
                if tl.audioen:
                    string = tl.audioen + '|'
                    num = '1'
                if tl.audiouk:
                    string += tl.audiouk + '|'
                    num = '2'
                
                shm.write(string, actualStart+offset)
                offset += len(string.encode('utf8'))

                #Numbers of audio links 
                shm.write(num, 5)

        if useShm:
            shm.write('1', 0)
            shm.write('\0', offset+actualStart)
            print('\n百度翻译结果写入完成\n')

#共享内存使用标识
useShm = 0
sys.argv.remove(sys.argv[0])
if len(sys.argv) >= 1:
    for arg in sys.argv:
        if arg == '-s':
            cprint('Using SharedMemory (baidu translate)', 'cyan')
            useShm = 1

main()
