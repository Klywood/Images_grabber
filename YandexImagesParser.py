import concurrent.futures
import json
import os
import time
from urllib.request import urlretrieve

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

#  name of folder to save folders with images
MAIN_FOLDER = 'saved_images'


def create_browser(decorated_method):
    """Decorator to create selenium browser"""

    def wrapper(self, *args, **kwargs):
        #  configure browser options
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.headless = True  # disable the visual display of the browser
        #  creating browser
        with webdriver.Chrome(options=chrome_options) as browser:
            #  call the main function
            decorated_method(self, browser, *args, **kwargs)

    return wrapper


class YandexImagesGrabber:
    """Class that provides methods to get and store images from Yandex.Images"""

    def __init__(self):
        """Initialization method"""
        # query string
        self.query = ''
        #  list of html-elements with images
        self._elements = []
        #  list with links to images
        self._links_to_images = []
        #  count of uploads
        self._uploads = 0
        #  count of iterations without uploads
        self._iter_count = 0
        #  saved images count
        self.count = 0
        self.session = requests.Session()

    @create_browser
    def _find_image_elements(self, browser, query, img_limit=100, img_size='medium', max_iterations=15):
        """Getting html-elements with images from yandex images search

        :param browser: selenium browser - get from decorator
        :param query: search query
        :param img_limit: number of images to be found
        :param img_size: size of images (medium as default)
        :param max_iterations: limit on the number of scrolls of the web-page until uploading more images
         (to avoid infinite loop)

        :return: calls method that gets links of images from elements
        """
        self.query = query
        browser.get(f'https://yandex.ru/images/search?text={query}&nomisspell=1&noreask=1&isize={img_size}')
        #  list of elements with images
        self._elements = browser.find_elements(By.CSS_SELECTOR, 'div.serp-item')
        #  number of images
        images_number = len(self._elements)
        while images_number < img_limit:
            try:
                #  scroll the page
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                #  waiting for upload page
                #  the more pictures - the longer the waiting time to have time to load
                time.sleep(1)
                #  recalculating the number of images on page
                self._elements = browser.find_elements(By.CSS_SELECTOR, 'div.serp-item')
                images_number = len(self._elements)
                print(f"Found {images_number} images")
                #  exit the loop when the number of iterations is exceeded (if something gone wrong)
                self._iter_count += 1
                if self._iter_count > max_iterations:
                    break
                #  trying click button to upload more images(going to next page)
                self.__upload_more(browser)
            except Exception as err:
                print(f"Error {err}. Going next")
                continue
        #  get links to images from element
        return self._get_images_links()

    def __upload_more(self, browser):
        """Click on 'upload more images' button if end of page has been reached"""
        try:
            browser.find_element(By.CLASS_NAME, 'more__button').click()
            #  increase uploads counter
            self._uploads += 1
            #  refreshing the iter count
            self._iter_count = 0
            print('Uploading more images...')
        #  if the end of the page hasn't been reached , there is no button - pass this step
        except:
            pass

    def _get_images_links(self):
        """Getting links of images from html-elements

        :return: list of links to images
        """
        s = time.time()
        for element in self._elements:
            #  create dict from attribute
            data = json.loads(element.get_attribute("data-bem"))
            link = data['serp-item']['img_href']
            # print(link)
            self._links_to_images.append(link)
        print('convert', time.time() - s)
        return self._links_to_images

    def _save_image(self, url, dir_to_save=None):
        """Method for saving image by url

        :param url: link to image
        :param dir_to_save: folder name to store images (query string as default)
        """
        folder = self._create_folder(dir_to_save)
        try:
            urlretrieve(url, os.path.join(folder, f"{self.count}.jpg"))
        except Exception as err:
            pass
            # print(f"{url} generated an exception: {err}")
        finally:
            self.count += 1

    def _save_all(self, workers=24, output_folder=None):
        """Saving all images in threads

        :param workers: number of threads
        :param output_folder: folder to save (will be created if not exists)
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            #  creating list of futures
            future_to_url = [executor.submit(self._save_image, url, output_folder) for url in self._links_to_images]
            for future in concurrent.futures.as_completed(future_to_url):
                future.result()
        self.count = 0

    def _save_links(self, file_name=None):
        """Method to save links of images to txt file

        :param file_name: name of txt file ('query_string.txt' as default)
        """
        name = file_name if file_name else self.query
        save_to = os.path.join(MAIN_FOLDER, name)
        with open(f"{save_to}_links.txt", 'w') as file:
            print(*self._links_to_images, sep='\n', file=file)

    def _create_folder(self, name=None):
        """Create folder to store images

        :param name: name of folder to be created

        :return: path to folder
        """
        name = name if name else self.query
        folder = os.path.join(MAIN_FOLDER, name)
        os.makedirs(folder, exist_ok=True)
        return folder

    def find_images(self, query, img_count=100, img_size='medium',
                    iter_limit=15, save_images=True, save_links_to_file=False):
        """Main method to use YandexImageGrabber class"""
        start = time.time()
        #  find elements and links
        self._find_image_elements(query, img_count, img_size, iter_limit)
        step1 = time.time()
        print('getting images', step1 - start)
        #  save links to file
        if save_links_to_file:
            self._save_links()
        # save images to folder
        if save_images:
            self._save_all()
        print('saving', time.time() - step1)
        print('total', time.time()-start)

if __name__ == '__main__':
    """Example of using"""
    a = YandexImagesGrabber()
    a.find_images("Космос", 1200, save_images=True, save_links_to_file=False)

