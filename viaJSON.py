# -*- coding: <utf-8> -*-

import bs4
from urllib.request import urlopen
from json import dumps, loads

# none-browser get different data
def mining(url):
    '''
    :param url: the url of web page which contains the info of employer and description of the job
    :return: json-string contains the information, which can be stored directly to MongoDB or process by auto-bewerber
    '''

    # read the html
    s = urlopen(url).read()

    soup = bs4.BeautifulSoup(s,"lxml")

    targStr = soup.select_one("script").string.strip().split("\n")

    targStr[0] = "{"
    targStr[-1] = "}"

    # print("\n".join(targStr))

    obj = loads("".join(targStr))

    return {"arbeitgeber":obj['stst']['company']['companyname'], "plz": obj['stst']['listing']['zipcode'], "stadt":obj['stst']['listing']['cityname'],"job":obj['stst']['listing']['title'] }

if __name__ == "__main__":
    url = r"http://www.stepstone.de/stellenangebote--Teamassistenz-m-w-Frankfurt-am-Main-WTS-Group-Aktiengesellschaft--3602205-inline.html"
    print(mining(url))