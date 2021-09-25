import smtplib, ssl
from load_config import *

config = load_config('config.yml')

def send_notification(coin):

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sent_from = config['EMAIL_ADDRESS']
    to = [config['EMAIL_ADDRESS']]
    subject = f'Binance will list {coin}, deposit some funds to be able to short it when listed'
    body = f'Read more at https://www.binance.com/en/support/announcement/c-48 or do a Google search https://www.google.com/search?q={coin}+token&oq={coin}+token&aqs=chrome.0.0i131i433i512l2j0i512l6j0i131i433i512j0i20i263i512.1732j0j4&sourceid=chrome&ie=UTF-8'
    message = 'Subject: {}\n\n{}'.format(subject, body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sent_from, config['EMAIL_PASSWORD'])
            server.sendmail(sent_from, to, message)

    except Exception as e:
        print(e)
