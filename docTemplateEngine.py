# -*- coding: <utf-8> -*-

from docx import Document
from jinja2 import Template

def render(d, tmpl, saveAs):
    '''
    :param d:  the obj which holds the info, just lke jinja2
    :param tmpl: the template docx file in jinja2 pattern
    :param saveAs: the file generated
    :return: None
    '''

    document = Document(tmpl)

    for p in document.paragraphs:
        for r in p.runs:
            r.text = Template(r.text).render(d)

    document.save(saveAs)


def parseText(d, txtFile):
    '''
    :param d: the obj which holds the info, just like in jinja2
    :param txtFile: the template file in jinja2 pattern
    :return: parseString
    '''
    f = open(txtFile)
    s = f.read()
    f.close()
    return Template(s).render(d)


if __name__ == '__main__':
    parseText(None, "README")
