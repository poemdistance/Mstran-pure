
def getHeaders0():

    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'AcceptLanguage':'en-US,en;q=0.5',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'DNT':'1',
            'Host':'fanyi.baidu.com',
            "Upgrade-Insecure-Requests": '1',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
            }

    return headers

def getHeaders1():

    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'AcceptLanguage':'en-US,en;q=0.5',
            'Connection':'keep-alive',
            'DNT':'1',
            'Host':'fanyi.baidu.com',
            'TE':'Trailers',
            "Upgrade-Insecure-Requests": '1',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
            }

    return headers

def getHeadersForV2tranapi():

    headers = {
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'AcceptLanguage':'en-US,en;q=0.5',
            'Connection':'keep-alive',
            'X-Requested-With':'XMLHttpRequest',
            'DNT':'1',
            'TE':'Trailers',
            'Host':'fanyi.baidu.com',
            'Referer':'https://fanyi.baidu.com',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
            }
    return headers

def getCorrecttxtHeaders():

    headers = {

            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'AcceptLanguage':'en-US,en;q=0.5',
            'Connection':'keep-alive',
            'X-Requested-With':'XMLHttpRequest',
            'DNT':'1',
            'Host':'correctxt.baidu.com',
            'Referer':'https://fanyi.baidu.com',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
            }

    return headers

def getClickHeaders():

    headers = {

            'Accept':'image/webp,*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'AcceptLanguage':'en-US,en;q=0.5',
            'Connection':'keep-alive',
            'DNT':'1',
            'Host':'click.fanyi.baidu.com',
            'Referer':'https://fanyi.baidu.com',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
            }

    return headers


