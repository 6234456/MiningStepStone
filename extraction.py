# -*- coding: <utf-8> -*-

import bs4
import requests
from json import loads
from re import compile, IGNORECASE
from difflib import SequenceMatcher

# iframe element loads the separate page which contains the critical info
# 1.   fetch the raw page, parse the json string
# 1.5  go to the url of employer to fetch the street
# 2.   get the url of iframe element, mining

def mining(url):
    '''
    :param url: the stepstone-url of web page which contains the info of employer and description of the job and the content of the web page should be in the German language
    :return: dict contains the information, which can be stored directly to MongoDB or process by auto-bewerber
    '''

    # to mimic the behavior of browser
    headers = {
        'Host':  'www.stepstone.de',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'
    }

    content = requests.post(url, headers=headers)

    soup = bs4.BeautifulSoup(content.content.decode('utf-8'), "lxml")
    # print(soup.prettify())


    # step 1
    targStr = soup.select_one("script").string.strip().split("\n")

    targStr[0] = "{"
    targStr[-1] = "}"

    obj = loads("".join(targStr))

    # dict to hold the info
    info = {"jobID":obj['stst']['listing']['listingid'] , "url": url, "arbeitgeber":obj['stst']['company']['companyname'].strip(), "plz": obj['stst']['listing']['zipcode'].strip(), "stadt":obj['stst']['listing']['cityname'].strip() or obj['stst']['listing']['locationname'].strip()
        ,"job":obj['stst']['listing']['title'].strip(), "istDurchEmail": obj['stst']['listing']['applyform']['type'] == "email", "agID":obj['stst']['company']['companyid'] }

    info['email'] = None
    info['strasse'] = None
    url_main = soup.select_one("iframe")['src']

    # step 1.5
    # http://www.stepstone.de/stellenangebote-des-unternehmens--{name_mit_bindstrich}--{id}.html
    tmpl = r"http://www.stepstone.de/stellenangebote-des-unternehmens--{0}--{1}.html".format("-".join(info["arbeitgeber"].split(" ")), info["agID"])
    content = requests.post(tmpl, headers=headers)
    soup = bs4.BeautifulSoup(content.content.decode('utf-8'), "lxml")

    # street-address
    # the address of the headquarter, sometimes differs from the address on the advertisement
    tempStrasse = soup.select_one(".street-address")
    if tempStrasse:
        tempStrasse = tempStrasse.string.strip()

    # step2
    content = requests.post(url_main, headers=headers)
    soup = bs4.BeautifulSoup(content.content.decode('utf-8'), "lxml")

    # TODO there might be rare cases that strasse can not match for example Zur Aue 2
    # TODO match the Ansprechpartner, maybe based on the position
    strasse = compile(r"([\w-]+\s?(Platz|Str\.|Straße|Allee|Weg|Ring)\s+\d+)", IGNORECASE)
    email = compile(r"[\w.-]+@[\w.-]+")
    # in some rare cases plz missing
    plzstadt = compile(r"(D-|d-)?(\d{5})\s+[A-ZÄÖÜ][a-zA-ZöäüÖÄÜ\s]+\b")

    # first kind of template contains id "company-continfo"
    continfo = soup.select_one("#company-continfo")

    if continfo:
        for string in continfo.stripped_strings:
            __processStr(string, info, email, strasse, plzstadt)
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

            __processStr(elems[i], info, email, strasse, plzstadt)

    # search for Gehaltsvorstellung and Eintrittstermin/Kündigungsfrist
    info['gehaltsvorstellung'] = False
    info['eintrittstermin'] = False
    eintrittstermin = compile(r"Eintrittstermin|Kündigungsfrist", IGNORECASE)
    gehaltsvorstellung = compile(r"Gehaltsvorstellung", IGNORECASE)

    elems = list(soup.select_one("body").stripped_strings)
    for i in range(len(elems)-1, -1, -1):
        if info['gehaltsvorstellung'] and info['eintrittstermin']:
            break

        if not info['gehaltsvorstellung'] and gehaltsvorstellung.search(elems[i]):
            info['gehaltsvorstellung'] = True

        if not info['eintrittstermin'] and eintrittstermin.search(elems[i]):
            info['eintrittstermin'] = True


    if info['strasse'] is None:
        info['strasse'] = tempStrasse
    elif SequenceMatcher(None, info['strasse'], tempStrasse).ratio() > 0.8:
        info['strasse'] = tempStrasse

    return info


def __processStr(string, info, email, strasse, plzstadt):
    if info['istDurchEmail'] and "@" in string:
        info["email"] = email.findall(string)[0].strip()

    if strasse.search(string):
        info['strasse'] = strasse.findall(string)[0][0].strip()

    if not info['plz'] and plzstadt.search(string):
        info['plz'] = plzstadt.findall(string)[0][1].strip()

if __name__ == "__main__":
    url = r"http://www.stepstone.de/stellenangebote--Sales-Coordinator-BMW-m-w-Eislingen-Fils-Continental-AG--3631616-inline.html"
    print(mining(url))