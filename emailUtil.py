# -*- coding: <utf-8> -*-


# author:    Qiou Yang
# email:     yang@qiou.eu
# desc:      send email with attachments to the target mailbox

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send(send_from, pwd, send_to, subject, text, files=None):
    send_to = send_to if isinstance(send_to, list) else [send_to]

    msg = MIMEMultipart(
            From=send_from,
            Date=formatdate(localtime=True),
    )
    msg['To']=COMMASPACE.join(send_to)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            msg.attach(MIMEApplication(
                    fil.read(),
                Content_Disposition='attachment; filename="%s"' % os.path.basename(f),
                Name=os.path.basename(f)
            ))


    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(send_from, pwd)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()