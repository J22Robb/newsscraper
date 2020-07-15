import requests
from bs4 import BeautifulSoup
import html5lib
import json
import re
import schedule
import time

bbc_url = "https://www.bbc.com/news/technology.html"
cnn_url = "https://www.cnn.com/business/tech"
cnbc_url = "https://www.cnbc.com/technology"
reuters_url = "https://www.reuters.com/news/technology"

def get_page_content(url):
    headers = {'Accept': 'text/html'}
    response_text = requests.get(url, headers=headers)
    return BeautifulSoup(response_text.content,'html.parser')


def scrape_bbc(bbc_url):
    bbc_soup = get_page_content(bbc_url)
    bbc_titles = bbc_soup.find_all(attrs={'class':'faux-block-link__overlay-link'})
    middle = [i['href'] for i in bbc_titles][0]
    top = "https://www.bbc.com"
    bbc = top + [i['href'] for i in bbc_titles][0]
    bbc_headline = [i.text for i in bbc_titles][0]
    return bbc, bbc_headline


def scrape_cnn(cnn_url):
    cnn_soup = get_page_content(cnn_url)
    cnn_titles = cnn_soup.find_all(attrs={'class': 'cd__headline'})
    middle = [i['href'] for i in cnn_titles[0]]
    top = "https://www.cnn.com"
    cnn = top + str(middle).strip("[]").strip("''")
    cnn_headline = [i.text for i in cnn_titles][0]
    return cnn, cnn_headline


def scrape_cnbc(cnbc_url):
    cnbc_soup = get_page_content(cnbc_url)
    titles = cnbc_soup.find_all(attrs={'class':'Card-title'})
    cnbc = [i['href'] for i in titles][0]
    cnbc_headline = [i.text for i in titles][0]
    return cnbc, cnbc_headline


def scrape_reuters(reuters_url):
    reuters_soup = get_page_content(reuters_url)
    reuters_titles = reuters_soup.find_all(name='a')
    top = "https://www.reuters.com"
    middle = middle = [i['href'] for i in reuters_titles][90]
    reuters = top + str(middle).replace("[]", "")
    reuters_headline = [i.text for i in reuters_titles][90].replace("\n", "").replace("\t", "")
    return reuters, reuters_headline


def scrape_all(bbc_url, cnn_url, cnbc_url, reuters_url):
    bbc, bbc_headline = scrape_bbc(bbc_url)
    cnn, cnn_headline = scrape_cnn(cnn_url)
    cnbc, cnbc_headline = scrape_cnbc(cnbc_url)
    reuters, reuters_headline = scrape_reuters(reuters_url)
    return bbc, bbc_headline, cnn, cnn_headline, cnbc, cnbc_headline, reuters, reuters_headline


def post_message_to_slack(slack_token, 
                          slack_channel, 
                          slack_icon_url, 
                          slack_user_name, 
                          text, 
                          blocks = None):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': slack_channel,
        'text': text,
        'icon_url': slack_icon_url,
        'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()



def job():

    bbc, bbc_headline, cnn, cnn_headline, cnbc, cnbc_headline, reuters, reuters_headline = scrape_all(bbc_url,cnn_url, cnbc_url, reuters_url)

    blocks = [
        {
        "type": "section",
        "text": {
        "type": "mrkdwn",
        "text": "*Here are this morning's top technology news headlines from BBC, CNBC, CNN, and Reuters.*"}
        },
        {
        "type": "section",
        "text": {
        "type": "mrkdwn",
        "text": """• BBC: <{}|{}> \n • CNBC: <{}|{}> \n • CNN: <{}|{}> \n • Reuters: <{}|{}>""".format(
            bbc, bbc_headline, cnn, cnn_headline, cnbc, cnbc_headline, reuters, reuters_headline)
        }}]

    slack_token = 'xoxb-your-bot-token'
    slack_channel = '#test'
    slack_icon_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuGqps7ZafuzUsViFGIremEL2a3NR0KO0s0RTCMXmzmREJd5m4MA&s'
    slack_user_name = 'News Bot'


    return post_message_to_slack(slack_token, 
                         slack_channel, 
                         slack_icon_url, 
                         slack_user_name,
                           "Your daily news report is ready.",
                           blocks)

if __name__ == "__main__":

    schedule.every().day.at("9:00").do(job)
    while True:

        schedule.run_pending()
        time.sleep(1)


