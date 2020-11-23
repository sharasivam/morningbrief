"""
Created on Sun, Nov 15 11:27:5 2020

@author: sharasivam

This script will scrape a selection of posts and news from given web pages
and create an html file that will be used as the content of an email being
sent to the given receivers. Watch a news summary, learn the word of the 
day, and start the day with a smile thanks to a wholesome meme. 
In short, brew a cup of coffee, drink and get briefed.
"""
import re # pattern finding
import smtplib, ssl # email server connection
import time # for delay

from bs4 import BeautifulSoup # web scraping
from urllib.request import Request, urlopen # opening URL
from email.mime.text import MIMEText # email content
from email.mime.multipart import MIMEMultipart # multipart email
from datetime import datetime # date and time
from random import choice # random choice

# my selection of news content:
tagesschau_100sek = "https://www.tagesschau.de/100sekunden/" # short video summary of current news
word_otd = "https://www.dictionary.com/e/word-of-the-day/" # english word of the day
wholesome_meme = "https://www.reddit.com/r/wholesomememes/top/"
wp_3 = ""

# additional variables in use
filename = datetime.now().strftime("%Y%m%d_%H%M%S") # creates a formatted filename 'YYYYMMDD_hhmmss'
greeting_list = [ # list of greetings to choose from for the email subject 
    "Rise and shine!",
    "Wakey, wakey, eggs and bakey.",
    "Look alive!",
    "What’s shakin’ bacon?",
    "Hiya!",
    "Let’s get this bread.",
    "Howdy!",
    "Pleasant morning we’re having.",
    "Good morning.",
    "Morning!",
    "Good day, mate.",
    "Top of the morning to you.",
    "The early bird catches the worm.",
    "Good day to you.",
    # ATTENTION, GREETINGS COPIED FROM https://tosaylib.com/different-ways-to-say-good-morning/
]

# <----------all HTML related functions---------->
# function to get the source code of an url
def parseSourceCode(my_url):
    hdr = {'User-Agent': 'Mozilla/5.0'} # header parameters
    req = Request(my_url,headers=hdr) # request url using given header parameters
    uClient = urlopen(req) # open requested url
    page_html = uClient.read() # read content of page
    uClient.close()
    soup = slurp(page_html) # parse content using an HTML parser
    return soup

def slurp(soup):
    soup = BeautifulSoup(soup, "html.parser")
    return soup 

# remove two levels of tag attributes
def cleanHTML(soup):
    all_att = ["class", "id", "style"] # the names of attr to be removed
    for attribute in all_att: 
        del soup[attribute] # del first/outer level attr
    for tag in soup(): 
        for attribute in all_att:
            del tag[attribute] # del second/inner level attr
    return str(soup)

# create todays HTML file in directory /archive
def createHTML():
    template = open('template.html').read() # open template containing structure and styling
    newBrief = open("archive/" + filename + ".html", "x") # create new HTML file
    newBrief.write(template.format(**content)) # paste todays news content using format
    newBrief.close()
    print("done")
    return None    

# <----------content specific functions---------->
# <----------tagesschau in 100sek---------->
# sourcing the current 100sek Tagesschau video ID to insert into an iframe str
def tagesschau():
    tagesschau_source = str(parseSourceCode(tagesschau_100sek)) # getting source code and turning into str
    tagesschau_strPattern = "^var sophoraID = 'video-[0-9]*" # pattern by which the str containing the ID can be found
    tagesschau_str = re.findall(tagesschau_strPattern, tagesschau_source, re.M) # using pattern to find substring containing ID
    tagesschau_ID = re.findall("[0-9]*$", tagesschau_str[0]) # filtering the ID
    # putting the ID into an HTML iframe (ATTENTION, IFRAME PROVIDED BY tagesschau)
    tagesschau_frame = "<iframe src=\"https://www.tagesschau.de/multimedia/video/video-" + tagesschau_ID[0] + "~player_branded-true.html\" frameborder=\"0\" webkitAllowFullScreen mozallowfullscreen allowFullScreen width=\"640px\" height=\"360px\" style=\"border-radius:8px;\"></iframe>"
    return tagesschau_frame

# <----------english word of the day---------->
# getting relevant parts from the word of the day from dictionary.com 
def wotd():
    word_source = parseSourceCode(word_otd)
    word_word = word_source.find("div", {"class": "otd-item-headword__word"})
    word_pronunciation = word_source.find("div", {"class": "otd-item-headword__pronunciation"})
    word_definition = word_source.find("div", {"class": "otd-item-headword__pos-blocks"})
    word_origin = word_source.find("div", {"class": "wotd-item-origin__content wotd-item-origin__content-full"})
    word_example = word_source.find("div", {"class": "wotd-item-examples wotd-item-examples--last"})

    word_box = ( # combining the parts after removing all tag attr using cleanHTML
        cleanHTML(word_word) +
        str(word_pronunciation) +
        cleanHTML(word_definition) +
        cleanHTML(word_origin) +
        cleanHTML(word_example)
    )
    return word_box

# <----------top wholesome meme from reddit---------->
# grab todays top post off of reddit.com/r/wholesomememes
def wholesome():
    while True:
        try:
            wholesome_source = parseSourceCode(wholesome_meme)
    #time.sleep(5) # delay needed
            wholesome_title = wholesome_source.find("h3")
            wholesome_title.name = "h1" # replace h3 with h1 to fit the rest
            break
        except AttributeError:
            print("Trying to get the title again.")
    wholesome_pic = wholesome_source.find("img", {"alt": "Post image"})
    wholesome_frame = cleanHTML(wholesome_title) + cleanHTML(wholesome_pic) # removing tag attr using cleanHTML
    return wholesome_frame

content = { # dict containing todays news content ready for HTML
    "tagesschau": tagesschau(),
    "wotd": wotd(),
    "wholesome": wholesome(),
}

# <----------everything email related---------->
# ATTENTION: THIS CODE IS COPIED AND MODIFIED FROM https://realpython.com/python-send-email/
def sendmail():
    # login details and receiver email
    sender_email = input("What's your gmail?")
    receiver_email = input("Who should receive it?")
    password = input("What is your password?")
    # message details
    message = MIMEMultipart("alternative")
    message["Subject"] =  datetime.now().strftime("%d.%m.%Y") + " - " + choice(greeting_list)
    message["From"] = sender_email
    message["To"] = receiver_email

    # create HTML body and plain text alternative
    text = """\
    Hi,
    if you can't see the content of this email properly, please let me know at wds20a@sharasivam.de
    Thanks!
    """
    html = open("archive/" + filename + ".html").read() # open created HTML file

    # parse parts according to their inteded use
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # attach parts to the message body, last part will be tried and rended first
    message.attach(part1)
    message.attach(part2)

    # create secure connection with server and send email
    session = smtplib.SMTP('smtp.gmail.com', 587) # using strato port in this case
    session.starttls() # enable secure connection
    session.login(sender_email, password) # login with sender_email and password
    text = message.as_string() # translate message into string
    session.sendmail(sender_email, receiver_email, text) # send email as wished
    session.quit() # quit started session
    print("Mail sent!")

createHTML() # create todays HTML file
sendmail() # send todays briefing using the created HTML file as email body