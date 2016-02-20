# -*- coding: <utf-8> -*-

# author:    Qiou Yang
# email:     sgfxqw@gmail.com
# desc:      to extract all the relevant information from a stepstone page for the job application

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
    info = {"jobID":obj['stst']['listing']['listingid'] , "url": url, "arbeitgeber":obj['stst']['company']['companyname'].strip()
        ,"job":obj['stst']['listing']['title'].strip(), "istDurchEmail": obj['stst']['listing']['applyform']['type'] == "email", "agID":obj['stst']['company']['companyid'] }

    info['email'] = None
    info['strasse'] = None
    info['stadt'] = None
    info['plz'] = None

    tempPlz = obj['stst']['listing']['zipcode'].strip()
    tempStadt = obj['stst']['listing']['locationname'].strip() or obj['stst']['listing']['cityname'].strip()

    # the url of content frame
    # http://www.stepstone.de/?event=OfferView.dspOfferViewHtml&offerId={jobID}
    url_iframe = "http://www.stepstone.de/?event=OfferView.dspOfferViewHtml&offerId={0}".format(info['jobID'])
    url_main = soup.select_one("iframe")['src']
    if not ("www.stepstone.de" in url_main):
        url_main = url_iframe


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
    # TODO match the Ansprechpartner ohne Anrede
    strasse = compile(r"([\w-]+\s?(Platz|Str\.|Straße|Allee|Weg|Ring)\s+\d+)", IGNORECASE)
    email = compile(r"[\w.-]+@[\w.-]+")
    # in some rare cases plz missing
    plzstadt = compile(r"(D-|d-)?(\d{5})\s+([A-ZÄÖÜ][a-zöäü]+)")

    # first kind of template contains id "company-continfo" -> not reliable
    # continfo = soup.select_one("#company-continfo")

    # loop through the whole dom, but in reversed order -> contact info always at the bottom

    # to record the index position of email
    pos = {"email": None, "plz": None}

    elems = list(soup.select_one("body").stripped_strings)

    for i in range(len(elems)-1, -1, -1):
        if info['istDurchEmail']:
            if info['email'] and info['strasse'] and info['plz']:
                break
        else:
            if info['strasse'] and info['plz']:
                break

        __processStr(elems[i], info, email, strasse, plzstadt, pos, i)

    # search for Gehaltsvorstellung and Eintrittstermin/Kündigungsfrist
    info['gehaltsvorstellung'] = False
    info['eintrittstermin'] = False
    eintrittstermin = compile(r"Eintrittstermin|Kündigungsfrist|Einstiegsdatum", IGNORECASE)
    gehaltsvorstellung = compile(r"Gehaltsvorstellung", IGNORECASE)

    for i in range(len(elems)-1, -1, -1):
        if info['gehaltsvorstellung'] and info['eintrittstermin']:
            break

        if not info['gehaltsvorstellung'] and gehaltsvorstellung.search(elems[i]):
            info['gehaltsvorstellung'] = True

        if not info['eintrittstermin'] and eintrittstermin.search(elems[i]):
            info['eintrittstermin'] = True

    # if the stree not found, use the one registered on the employer info
    if info['strasse'] is None:
        info['strasse'] = tempStrasse
    # if the stree exists, but resembles to the one on the registration, change to the latter
    elif tempStrasse and SequenceMatcher(None, info['strasse'], tempStrasse).ratio() > 0.8:
        info['strasse'] = tempStrasse

    if info['plz'] is None:
        info['plz'] = tempPlz
        info['stadt'] = tempStadt
    elif tempStadt and SequenceMatcher(None, info['stadt'], tempStadt).ratio() > 0.7:
        info['stadt'] = tempStadt

    # search for ansprechpartner
    info['anrede'] = None
    info['ansprechpartner'] = None
    info['ansp_vor'] = None
    info['ansp_nach'] = None

    ansp = compile("((Herr|Herrn|Frau)\s)(([A-ZÄÖÜ][a-zöäü]+\s)?(von\s)?[A-ZÄÖÜ][a-zöäü]+)")


    search_start = pos['plz'] or pos['email'] or len(elems)-1

    for i in range(search_start, -1, -1):
        if ansp.search(elems[i]):
            tmp = ansp.findall(elems[i])[0]

            info['ansprechpartner'] = tmp[2]


            if not (" " in tmp[2]):
                info['ansp_vor'], info['ansp_nach'] = "", tmp[2]
            else:
                info['ansp_vor'], info['ansp_nach'] = tmp[2].split(" ")

            if tmp[1]:
                if tmp[1] == "Frau":
                    info['anrede'] = "F"
                else:
                    info['anrede'] = "M"
            break


    return info


def __processStr(string, info, email, strasse, plzstadt, pos, i):
    if info['istDurchEmail'] and "@" in string:
        info["email"] = email.findall(string)[0].strip()
        pos['email'] = i

    if strasse.search(string):
        info['strasse'] = strasse.findall(string)[0][0].strip()

    if not info['plz'] and plzstadt.search(string):
        pos['plz'] = i
        info['plz'] = plzstadt.findall(string)[0][1].strip()
        info['stadt'] = plzstadt.findall(string)[0][2].strip()

if __name__ == "__main__":
    url = r"http://www.stepstone.de/stellenangebote--Business-Partner-Functional-Controlling-w-m-Dortmund-WILO-SE--3663586-inline.html"
    print(mining(url))