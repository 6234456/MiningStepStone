# -*- coding: <utf-8> -*-

import bs4
from urllib.request import urlopen
from json import dumps
from re import compile, IGNORECASE


def mining(url):
    '''
    :param url: the url of web page which contains the info of employer and description of the job
    :return: json-string contains the information, which can be stored directly to MongoDB or process by auto-bewerber
    '''

    # read the html
    s = urlopen(url).read()

    # reg to filter the info

    # exclude two consecutive blanks, e.g. can match Frankfurt am Main
    stadt = compile(r"\d{5}\s+[A-ZÄÖÜ]\S+\s?\w*")
    adresse = compile(r"([\w-]+\s?(Platz|Str\.|Straße|Allee|Weg|Ring)\s+\d+)", IGNORECASE)
    entity = compile(r"\s+(AG|GmbH|KG|Group|GbR|SE)$")

    # dict to store the info
    d = dict()
    d['addresse'] = None
    d['arbeitgeber'] = None
    d['stadt'] = None

    # print(s)

    soup = bs4.BeautifulSoup(s,"lxml")
    print(soup.prettify())
    # print(soup.find("div", id="jobOfferWrapper"))

    targStr = repr(soup.select_one("#jobOfferWrapper")).split("\n")
    title = soup.select_one("title")

    if title:
        d['job'] = title.string.split("−")[0].strip()

    for i in range(len(targStr)):
        if d['stadt'] is None and stadt.search(targStr[i]):
            d['stadt'] = stadt.findall(targStr[i])[0].strip()

        if d['arbeitgeber'] is None and entity.search(targStr[i]):
            d['arbeitgeber'] = entity.findall(targStr[i])[0].strip()

        if d['addresse'] is None and adresse.search(targStr[i]):
            d['addresse'] = adresse.findall(targStr[i])[0][0]

    return dumps(d, ensure_ascii=False)


if __name__ == "__main__":
    url = r"http://www.stepstone.de/stellenangebote--Referent-m-w-des-Geschaeftsfuehrers-Schwerpunkt-China-Ditzingen-bei-Stuttgart-TRUMPF-GmbH-Co-KG--3623427-inline.html"
    print(mining(url))