from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities #Amazon requires certain user-agents
from bs4 import BeautifulSoup

import os, re

import requests
from StringIO import StringIO
from PIL import Image
from pytesseract import image_to_string

from collections import defaultdict

from time import sleep

def get_amazon_data(amazon_login_email, amazon_login_password):
    print 'running get_amazon_data'
    phantomjs_executable = ''
    if os.name=='nt': phantomjs_executable = "phantomjs.exe"
    else: phantomjs_executable = "phantomjs"
    phantomjs = os.path.realpath(os.path.join(os.getcwd(), phantomjs_executable))

    user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    )

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent

    browser = webdriver.PhantomJS(phantomjs,desired_capabilities=dcap)
    #browser = webdriver.Firefox()

    try:
        amazon_login_url = "https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyour-account%2Forder-history%3Fie%3DUTF8%26ref_%3Dya_orders_ap&pageId=webcs-yourorder&showRmrMe=1"

        browser.get(amazon_login_url)

        username = browser.find_element_by_name('email')
        username.send_keys(amazon_login_email)
        password = browser.find_element_by_name('password')
        password.send_keys(amazon_login_password)
        form = browser.find_element_by_name('signIn')
        form.submit()

        response = browser.page_source
        soup = BeautifulSoup(response)

        login_errors = soup.findAll("span", {"class": "a-list-item"}, text=re.compile("Your email or password was incorrect. Please try again."))
        if login_errors:
            return "Login Error"
        # login_errors = soup.findAll("h4", {"class": "a-alert-heading"}, text=re.compile("There was a problem"))
        # if login_errors:
        #     return "There was a problem"

        captcha_element = soup.find('img', id='auth-captcha-image')
        refreshtimes = 0
        captcha_guess = ''
        if captcha_element:
            while refreshtimes<15:
                captcha_element = soup.find('img', id='auth-captcha-image')
                captcha_img_url = captcha_element['src']

                print captcha_img_url
                captcha_response = requests.get(captcha_img_url)

                img = Image.open(StringIO(captcha_response.content))
                captcha_guess = image_to_string(img)
                print 'guess: '+captcha_guess

                if (' ' in captcha_guess) == True or captcha_guess == '':
                    refreshcap = browser.find_element_by_id("auth-captcha-refresh-link")
                    refreshcap.click()
                else:
                    break
                refreshtimes += 1

            if refreshtimes == 14:
                raise ValueError('Could not automatically solve captcha.')

            print 'chosen guess: '+captcha_guess

            password = browser.find_element_by_name('password')
            password.send_keys(amazon_login_password)
            guess = browser.find_element_by_name('guess')
            guess.send_keys(captcha_guess)
            form = browser.find_element_by_name('signIn')
            form.submit()

        response = browser.page_source
        track_package = []
        soup = BeautifulSoup(response)

        login_errors = soup.findAll("span", {"class": "a-list-item"}, text=re.compile("Your email or password was incorrect. Please try again."))
        if login_errors:
            return "Login Error"
        # login_errors = soup.findAll("h4", {"class": "a-alert-heading"}, text=re.compile("There was a problem"))
        # if login_errors:
        #     return "There was a problem"

        for link in soup.findAll('a', text=re.compile("Track package")):
            track_package.append('http://amazon.com'+link['href'])

        TBA_dict = defaultdict(list)

        if track_package:
            for url in track_package:
                browser.get(url)
                response = browser.page_source

                soup = BeautifulSoup(response)
                search = "Tracking #:"

                order_url = soup.findAll('a', text=re.compile("Order Details"))[0]['href']

                for div in soup.findAll('div', text=re.compile(search)):
                    TBA_dict[div.string[div.string.index(search) + len(search):].strip()].append(order_url)

            with open("amazon_orders.txt", 'w+') as ama:
                for TBAkey in TBA_dict.keys():
                    for value in TBA_dict[TBAkey]:
                        ama.write(TBAkey+"|"+value+"\n")

            print 'Successfully gathered Amazon products\' tracking numbers.'
        # browser.quit()
        return 'Success'

    except ValueError as e:
        # browser.quit()
        print e
        return ValueError

#print get_amazon_data(amazon_login_email, amazon_login_password)