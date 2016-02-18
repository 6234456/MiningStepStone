# -*- coding: <utf-8> -*-

import bs4
import requests
from json import loads
from re import compile, IGNORECASE

# iframe element loads the separate page which contains the critical info
# 1. fetch the raw page, parse the json string
# 2. get the url of iframe element, mining

def mining(url):
    '''
    :param url: the url of web page which contains the info of employer and description of the job
    :return: json-string contains the information, which can be stored directly to MongoDB or process by auto-bewerber
    '''

    # to mimic the behavior of browser
    headers = {
        'Host':  'www.stepstone.de',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'
    }

    content = requests.post(url, headers=headers)

    soup = bs4.BeautifulSoup(content.content.decode('utf-8'), "lxml")

    # step 1
    targStr = soup.select_one("script").string.strip().split("\n")

    targStr[0] = "{"
    targStr[-1] = "}"

    obj = loads("".join(targStr))

    # dict to hold the info
    info = {"arbeitgeber":obj['stst']['company']['companyname'], "plz": obj['stst']['listing']['zipcode'], "stadt":obj['stst']['listing']['cityname'],"job":obj['stst']['listing']['title'], "istDurchEmail": obj['stst']['listing']['applyform']['type'] == "email" }

    info['email'] = None
    info['strasse'] = None

    # step2
    url_main = soup.select_one("iframe")['src']

    content = requests.post(url_main, headers=headers)
    soup = bs4.BeautifulSoup(content.content.decode('utf-8'), "lxml")

    strasse = compile(r"([\w-]+\s?(Platz|Str\.|Straße|Allee|Weg|Ring)\s+\d+)", IGNORECASE)
    email = compile(r"[\w.-]+@[\w.-]+")

    # first kind of template contains id "company-continfo"
    continfo = soup.select_one("#company-continfo")

    if continfo:
        for string in continfo.stripped_strings:
            __processStr(string, info, email, strasse)
    else:
        # loop through the whole dom, but in reversed order -> contact info always at the bottom
        elems = list(soup.select_one("body").stripped_strings)

        for i in range(len(elems)-1, -1, -1):
            if info['istDurchEmail']:
                if info['email'] and info['strasse']:
                    break
            else:
                if info['strasse']:
                    break

            __processStr(elems[i], info, email, strasse)

    return info


def __processStr(string, info, email, strasse):
    if info['istDurchEmail'] and "@" in string:
        info["email"] = email.findall(string)[0].strip()

    if strasse.search(string):
        info['strasse'] = strasse.findall(string)[0][0].strip()

if __name__ == "__main__":
    url = r"http://www.stepstone.de/stellenangebote--Business-Analyst-m-w-Hannover-BG-Phoenics-GmbH--3662048-inline.html"
    print(mining(url))