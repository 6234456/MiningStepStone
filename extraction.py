# -*- coding: <utf-8> -*-

# author:    Qiou Yang
# email:     yang@qiou.eu
# desc:      to extract all the relevant information from a stepstone page for the job application

import json
import urllib


def mining(url):
    print(url)
    return json.loads(url)

