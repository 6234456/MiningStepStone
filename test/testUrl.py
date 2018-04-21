import requests
import bs4
from re import compile, MULTILINE
from json import loads

def testUrl(url):

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


    print(info['stadt'])

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
        tempPlz, tempStadt = tmpArray[1].replace(tempLand, "").strip().split(" ", 1)
        tmpReg = compile(",\s*$")
        tempStadt, tempStrasse = [ tmpReg.sub("", i) for i in [tempStadt, tmpArray[2]]]

        info['plz'],info['stadt'],info['strasse'] = tempPlz, tempStadt, tempStrasse


if __name__ == '__main__':
    testUrl("https://www.stepstone.de/stellenangebote--Finance-Manager-m-w-Ismaning-bei-Muenchen-Byton-GmbH--4932556-inline.html?suid=4f2f972f-838f-4e22-b01a-f011da2bd6ad&rltr=120_20_25_dynrl_m_0_0")