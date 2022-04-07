#https://github.com/sendgrid/sendgrid-python

import json
import datetime
import urllib.parse
import logging

import requests
import sendgrid
from sendgrid.helpers.mail import *

import CSR_service_mesh_map
import CSR_toolkit

#configure logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=CSR_toolkit.logging_level_var)


def send_an_email(SENDGRID_API_KEY, from_address, to_address, subject, message_body):
    logging.critical("send_an_email() called")
    sendgrid_client = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(str(from_address))
    to_email = To(str(to_address))
    subject = str(subject)
    content = Content("text/plain", str(message_body))
    mail = Mail(from_email, to_email, subject, content)

    logging.error(mail)

    sendgrid_response = sendgrid_client.client.mail.send.post(request_body=mail.get())
    logging.error(sendgrid_response.status_code)
    logging.error(sendgrid_response.body)
    logging.error(sendgrid_response.headers)
    if sendgrid_response.status_code >= 200 and sendgrid_response.status_code < 300:
        return "success: mail sent"
    else:
        return "error: mail not sent"


def send_an_http_verification_email(SENDGRID_API_KEY, from_address, to_address, http_verification_link):
    logging.critical("send_an_http_verification_email() called")

    subject_msg = "Please verify your CryptoStacker account"

    html_message = '''
    <html>
    <head>
    </head>
    <body>
        <center>

                <h1>Welcome to CryptoStacker!</h1>

                <p>Thank you for signing up. Please verify your email address by clicking the following link:</p>

                <p><a href="%s">Confirm my account</a></p>

            <p> If your link is broken, please copy and paste the following URL into your browser URL bar: %s </p>

                <p>
                    If you are having any issues with your account, please do not hesitate to contact us by replying to
                    this mail.
                </p>

                <br />
                Thanks!
                <br />

                <strong>CryptoStacker</strong>

                <br /><br />
                    If you did not make this request, please contact us by replying to this mail.
            
        </center>
    </body>
    </html>
    ''' % (http_verification_link, http_verification_link)

    message = Mail(
        from_email=str(from_address),
        to_emails=str(to_address),
        subject=str(subject_msg),
        html_content=html_message)
    
    logging.error(message)
    try:
        sendgrid_client = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        sendgrid_response = sendgrid_client.send(message)
        logging.error(sendgrid_response.status_code)
        logging.error(sendgrid_response.body)
        logging.error(sendgrid_response.headers)
        if sendgrid_response.status_code >= 200 and sendgrid_response.status_code < 300:
            return "success: mail sent"
        else:
            return "error: mail not sent"
    except Exception as e:
        print(e.message)
