import random
import md5
import base64
import logging
from django.core.mail.message import EmailMessage

digits = '0123456789'
letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def wrap_email(email):
    try:
        email_name, domain_part = email.strip().split('@', 1)
    except ValueError:
        pass
    else:
        email = '@'.join([email_name, domain_part.lower()])
    return email

def generate_valid_string():
    chars = letters + digits
    val_str = ''
    for i in range(32):
        val_str = val_str + random.choice(chars)
    return val_str

def generate_base64_string(input_str):
    hash_str = md5.new()
    hash_str.update(input_str)
    value = hash_str.digest()
    return base64.encodestring(value)

def send_email(html_content, recipient, subject):
    is_success = False
    try:
        err_msg = 'Sending email to %s subject: %s' % (recipient, subject)
        logging.debug(err_msg)
        msg = EmailMessage(subject, html_content, to=[recipient])
        msg.content_subtype = "html" # Main content is now text/html
        msg.send()
        is_success = True
    except Exception, e:
        print e
        err_msg = 'send_email(), email_to: %s,  exception: %s' % (recipient, e)
        logging.error(err_msg)
    return is_success

register_mail_template = '''
    <html>
    <head>
    </head>
        <body>
            <p>

                Welcome to StockTrenz!<br><br>

                To activate your account, simply click on the link below or paste into the url field on your favorite browser:<br><br>

                <a href='%s'>%s</a> <br><br>

                The activation link will only be good for %s days, after that you will have to try again from the beginning. When you visit the above page, input your email and password to login our site.<br><br>

                If you have any questions about the system, feel free to contact us anytime at info@stocktrenz.com.<br><br>

                StockTrenz Team<br>
            </p>
        </body>
    </html>
'''