def info():
    d = dict()
    # info for Anschreiben
    d['path_template_anschreiben'] = "tmpl/tmpl.docx"
    d['path_template_email_text'] = "tmpl/email.txt"
    d['path_document'] = "common/Bewerbungsmappe_Qiou Yang.pdf"
    d['name_datei_anschreiben'] = "Anschreiben_Qiou Yang.docx"

    # info for direct apply
    d['email_usr'] = "sgfxqw@gmail.com"
    d['email_smtp_server'] = "smtp.gmail.com"
    d['email_smtp_server_port'] = 587
    d['email_pwd'] = ""

    return d