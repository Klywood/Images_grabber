import json
import os
import time
from urllib.request import urlretrieve

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def fun(query, pages=1, img_size='medium', max_iterations=20):
    """Getting images from yandex images search

    :param query: search query
    :param pages: number of pages to be parsed (1 page ~ 300 pictures)
    :param img_size: size of images (medium as default)
    :param max_iterations: limit on the number of scrolls of the web-page (to avoid infinite loop)

    """
    #  disabling
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")

    with webdriver.Chrome(options=chrome_options) as browser:
        #  get the page
        browser.get(f'https://yandex.ru/images/search?text={query}&nomisspell=1&noreask=1&isize={img_size}')
        #  number of images
        images = browser.find_elements(By.CSS_SELECTOR, 'div.serp-item')
        images_number = len(images)
        #  count of scrolling iterations
        iter_count = 0
        #  current number of saved images
        images_found = 0
        #  go through pages
        for i in range(pages):
            try:
                #  until there are no new pictures
                while images_found != images_number:
                    #  remember current images count
                    images_found = images_number
                    #  scroll the page
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    #  waiting for upload page
                    time.sleep(i+1)
                    #  recalculating the number of images on page
                    images = browser.find_elements(By.CSS_SELECTOR, 'div.serp-item')
                    images_number = len(images)
                    print(f"Found {images_number} images")
                    #  exit the loop when the number of iterations is exceeded
                    iter_count += 1
                    if iter_count > max_iterations:
                        break
                #  click button to upload more images(going to next page)
                browser.find_element(By.CLASS_NAME, 'more__button').click()
                #  refreshing counters and going to next page
                iter_count = 0
                images_found = 0
            except Exception as err:
                # print(f"Error {err} occured\nReturn already found images")
                continue
        return get_images_links(images)


def get_images_links(images):
    """Getting links of images from html-elements
    :param images: list of html-elements
    :return: list of links to images
    """
    links = []
    for image in images:
        #  create dict from attribute
        data = json.loads(image.get_attribute("data-bem"))
        link = data['serp-item']['img_href']
        links.append(link)
    return links


def save_images(links, folder_to_save):
    # h = httplib2.Http('.cache')
    #  create folder to save
    folder = os.path.join('saved_images', folder_to_save)
    os.makedirs(folder, exist_ok=True)
    count = 1
    for img in links:
        img_format = img.split('.')[-1]
        try:
            urlretrieve(img, os.path.join(folder, f"{count}.{img_format}"))
            print(count, 'done')
        except:
            print(count, 'fail')
            continue
        finally:
            count += 1

if __name__ == '__main__':
    start = time.time()
    a = fun('Кошка', 5)
    # with open('cats.txt', 'w') as f:
    #     print(*a, sep='\n', file=f)
    # print(a)
    save_images(a, 'cats')
    print(time.time() - start)
