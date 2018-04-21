# -*- coding: <utf-8> -*-

# author:    Qiou Yang
# email:     yang@qiou.eu
# desc:      to extract all the relevant information from a stepstone page for the job application

import bs4
import requests
from json import loads
from re import compile, IGNORECASE, MULTILINE

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

    # step 1
    # store the js-object to obj-dict, key is the variables defined in script-tags
    varReg = compile(r"var\s+(\S+)\s+=(.*);", MULTILINE)
    obj = {j.group(1): loads(j.group(2)) for j in
            [varReg.match(i.text.strip()) for i in soup.select("script")]
            if j}


    # dict to hold the info
    info = {"jobID":obj['utag_data']['listing__listing_id'] ,
            "url": url,
            "job":obj['utag_data']['listing__title'],
            "istDurchEmail": obj['utag_data']['listing__apply_dbtype'] == "internal_email",
            "agID":obj['utag_data']['listing__company_id'] }

    # for the big publisher like PwC, there is no separate locationData but they have companycard__card
    md2 = soup.select_one(".company-card__wrapper .company-card__title a")
    if md2:
        info["arbeitgeber"] = md2.text.strip()
    else:
        info["arbeitgeber"] = obj['locationData']['MAPDATA']['LOCATION']['COMPANYDATA']['NAME'] if 'locationData' in obj and obj['locationData'] else None


    info['email'], info['strasse'], info['plz'], info['stadt']= None, None, None, None


    if 'locationData' in obj and 'MAPDATA' in obj['locationData'] :
        info['strasse'] = obj['locationData']['MAPDATA']['LOCATION']['COMPANYDATA']['STREET'].strip()
        info['stadt'] = obj['locationData']['MAPDATA']['LOCATION']['COMPANYDATA']['CITY'].strip()
        info['plz'] = obj['locationData']['MAPDATA']['LOCATION']['COMPANYDATA']['POSTALCODE']


    # the url of content frame
    # http://www.stepstone.de/?event=OfferView.dspOfferViewHtml&offerId={jobID}
    url_iframe = "http://www.stepstone.de/?event=OfferView.dspOfferViewHtml&offerId={0}".format(info['jobID'])
    url_main = ""

    if soup.select_one("iframe"):
        url_main = soup.select_one("iframe")['src']

    if not ("www.stepstone.de" in url_main):
        url_main = url_iframe


    # step 1.5
    # http://www.stepstone.de/stellenangebote-des-unternehmens--{name_mit_bindstrich}--{id}.html
    tmpl = r"https://www.stepstone.de/cmp/de/{0}-{1}/jobs.html".format("-".join(info["arbeitgeber"].split(" ")), info["agID"])
    content = requests.post(tmpl, headers=headers)
    soup = bs4.BeautifulSoup(content.content.decode('utf-8'), "lxml")

    # street-address
    # the address of the headquarter, sometimes differs from the address on the advertisement
    tempLand, tempStadt, tempStrasse, tempPlz = "", "", "", ""
    tmpArray = [j.text.strip() for j in [soup.select_one(i) for i in (
        ".at-cqi_country", ".at-cqi_postcode", ".at-cqi_adress")] if j]

    if len(tmpArray) == 3:
        tempPlz, tempStadt = tmpArray[1].replace(tmpArray[0], "").strip().split(" ", 1)
        tmpReg = compile(",\s*$")
        tempStadt, tempStrasse = [tmpReg.sub("", i) for i in [tempStadt, tmpArray[2]]]
        info['plz'], info['stadt'], info['strasse'] = tempPlz, tempStadt, tempStrasse


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

    if strasse.search(string) and not info['strasse']:
        info['strasse'] = strasse.findall(string)[0][0].strip()

    if plzstadt.search(string):
        pos['plz'] = i
        info['plz'] = plzstadt.findall(string)[0][1].strip() if not info['plz'] else info['plz']
        info['stadt'] = plzstadt.findall(string)[0][2].strip() if not info['stadt'] else info['stadt']
