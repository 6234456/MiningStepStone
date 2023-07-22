import asyncio

import requests
import httpx
import bs4
from re import compile, MULTILINE
from json import loads

if __name__ == '__main__':
    loads('{"url":"https://www.stepstone.de/stellenangebote--Fachkraft-fuer-Lagerlogistik-m-w-d-Grossostheim-Maag-Germany-GmbH--9775085-inline.html?rltr=83_8_25_seorl_m_0_0_0_0_1_0","job":"Fachkraft & Lagerlogistik (m/w/d)","jobID":"9775085","arbeitgeber":"Maag Germany GmbH","ansprechpartner":null,"email":"jobs@maag.com","plz":"63762","stadt":"Grossostheim","strasse":"Ostring 19","anrede":null,"agID":"93458"}')