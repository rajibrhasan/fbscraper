#imports here
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import wget
import os
import requests
import urllib.request
import imghdr



#code by pythonjar, not me
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)


#get all the image urls from the page
def get_image_urls(page_url, driver):
    page_id = page_url.split('/')[-2]
    driver.get(page_url)
    time.sleep(5)

    #scroll down
    #increase the range to sroll more
    #example: range(0,10) scrolls down 650+ images


    # for j in range(0,20):
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     time.sleep(5)

    SCROLL_PAUSE_TIME = 5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    anchors = set()

    while True:
        # Scroll down to bottom

        temp_anchors = driver.find_elements(By.TAG_NAME, 'a')
        temp_anchors = [a.get_attribute('href') for a in temp_anchors]
        temp_anchors = [a for a in temp_anchors if str(a).startswith("https://www.facebook.com/photo") or str(a).startswith("https://www.facebook.com/"+page_id)]

        for a in temp_anchors:
            anchors.add(a)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


    anchors = list(anchors)

    print(f'Collected {len(anchors)}  anchor elements from the photos.')

    image_urls = set()
    #extract the [0]th image element in each link
    for a in anchors:
        driver.get(a) #navigate to link
        time.sleep(2) #wait a bit
        img = driver.find_elements(By.TAG_NAME, "img")
        image_urls.add(img[0].get_attribute("src")) #may change in future to img[?]

    print('Found ' + str(len(image_urls)) + ' urls to images')
    return list(image_urls)

#download the image given the url and basename
def download_image(url, basename):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError
    extension = imghdr.what(file=None, h=response.content)
    save_path = f"{basename}.{extension}"
    with open(save_path, 'wb') as f:
        f.write(response.content)


def main(page_url):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    #open the webpage
    driver.get("http://www.facebook.com")

    #target username
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

    #enter username and password
    username.clear()
    username.send_keys(os.environ.get('username'))
    password.clear()
    password.send_keys(os.environ.get('password'))

    #target the login button and click it
    button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

    time.sleep(5)

    #We are logged in!
    print('Logged in!!')

    image_urls = get_image_urls(page_url, driver)

    path = os.getcwd()
    path = os.path.join(path, 'Memes', page_url.split('/')[-2])

    if not os.path.exists(path):
        os.makedirs(path)

    counter = 1
    for image_url in image_urls:
        download_image(image_url, os.path.join(path, str(counter)))
        counter+=1

if __name__ == '__main__':
    os.environ['username'] = 'your facebook username'
    os.environ['password'] = 'your password'

    page_url = 'https://www.facebook.com/memebujho420'

    main(page_url+'/photos')