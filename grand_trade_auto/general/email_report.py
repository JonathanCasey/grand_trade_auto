#!/usr/bin/env python3
"""
Report email functionality.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from email import charset
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from grand_trade_auto.general import config
from grand_trade_auto.general.exceptions import *   # pylint: disable=wildcard-import, unused-wildcard-import



def load_email_conf():
    """
    Loads the email sender and recipient information from config files.

    Returns:
      data ({str:str/int/[str]}): Dict containing email configuration details
        loaded from config.
    """
    fake_section = 'secrets'
    secrets_cp = config.read_conf_file_fake_header('.secrets.env',
            fake_section=fake_section)
    gta_cp = config.read_conf_file('gta.conf')

    data = {}
    data['server'] = secrets_cp.get(fake_section, 'EMAIL_SERVER_HOST')
    data['port'] = secrets_cp.get(fake_section, 'EMAIL_SERVER_PORT')
    data['sender'] = secrets_cp.get(fake_section, 'EMAIL_USERNAME')
    data['password'] = secrets_cp.get(fake_section, 'EMAIL_PASSWORD')
    data['sender_name'] = secrets_cp.get(fake_section, 'EMAIL_SEND_NAME')

    for k, v in data.items():
        data[k] = v.strip('\'"')

    data['recipients'] = config.parse_list_from_conf_string(
            gta_cp.get('email', 'recipients'), config.CastType.STRING,
            strip_quotes=True)

    return data



def send_email(subject, body):
    """
    Sends an email to the configured recipients via the configured
    sender/server.

    Args:
      subject (str): The subject of the email.
      body (str): The HTML-formatted body of the email.

    Raises:
      (EmailConnectionError): The email could not be sent due to a server
        connection failure.
    """
    try:
        email_conf = load_email_conf()
    except Exception as ex:
        raise EmailConfigError('Email config load failed.') from ex

    recipient = ', '.join(email_conf['recipients'])

    # Default encoding mode set to Quoted Printable (instead of base64)
    # Acts globally!
    charset.add_charset('utf-8', charset.QP, charset.QP, 'utf-8')

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = email_conf['sender_name']

    html_part = MIMEText(body.encode('utf-8'), 'html', 'UTF-8')
    msg.attach(html_part)

    try:
        session = smtplib.SMTP(email_conf['server'], email_conf['port'])

        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(email_conf['sender'], email_conf['password'])

        session.sendmail(email_conf['sender_name'], recipient, msg.as_string())
        session.quit()
    except Exception as ex:
        raise EmailConnectionError('Email send connection error.') from ex



if __name__ == '__main__':
    """
    Call this module to run a quick manual test to confirm email sending works.

    As with anything else, must still be called from repo root, i.e.
    `python3 ./grand_trade_auto/general/email_report.py`
    """
    send_email('Test GTA subject', 'Test grand_trade_auto body.')
