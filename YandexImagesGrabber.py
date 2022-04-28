import concurrent.futures
import json
import os
import sys
import logging
import time
from urllib.request import urlretrieve
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from settings import *


def create_browser(decorated_method):
    """Decorator to create selenium browser"""

    def wrapper(self, *args, **kwargs):
        #  configure browser options
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.headless = HIDE_BROWSER  # disable the visual display of the browser
        #  creating browser
        with webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=chrome_options) as browser:
            #  call the main function
            decorated_method(self, browser, *args, **kwargs)

    return wrapper


class YandexImagesGrabber:
    """Class that provides methods to get and store images from Yandex.Images"""

    def __init__(self):
        """Initialization method"""
        # time of work
        self.start_time = time.time()
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
        #  total and saved images count
        self.count = 0
        self.saved = 0
        #  create logger
        self._logger = self.create_logger()

    @staticmethod
    def create_logger(folder_name=LOG_FOLDER):
        """Creates logger

        :param folder_name: folder name or path to the folder to store log-file

        :return: logger with settings and handlers
        """
        #  create folder
        os.makedirs(folder_name, exist_ok=True)
        #  creating full path to log-file
        full_name = os.path.join(folder_name, 'Yndx_img_grabber.log')
        #  creating new logger
        logger = logging.getLogger(LOG_NAME)
        #  set the logger level, messages which are less severe than level will be ignored
        logger.setLevel(LOG_LEVEL)
        #  create handlers
        #  to file
        filehandler = logging.FileHandler(full_name, 'a')
        filehandler.setLevel(FH_level)
        # set format of messages
        format = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s',
                              "%Y-%m-%d %H:%M:%S")
        filehandler.setFormatter(format)
        #  to console
        streamhandler = logging.StreamHandler(stream=sys.stdout)
        streamhandler.setLevel(SH_level)
        streamhandler.setFormatter(format)
        #  add handlers to logger
        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)
        #  first message in new logger
        logger.debug('Created logger')

        return logger

    @create_browser
    def _find_image_elements(self, browser, query, img_limit, img_size, max_iterations):
        """Getting html-elements with images from yandex images search

        :param browser: selenium browser - get from decorator
        :param query: search query
        :param img_limit: number of images to be found
        :param img_size: size of images (medium as default)
        :param max_iterations: limit on the number of scrolls of the web-page without getting new images
        (to avoid infinite loop)

        :return: calls method that gets links of images from elements
        """
        self.query = query
        browser.get(f'https://yandex.ru/images/search?text={query}&nomisspell=1&noreask=1&isize={img_size}')
        self._logger.info(f"Image search for '{query}'")
        #  list of elements with images
        self._elements = browser.find_elements(By.CSS_SELECTOR, 'div.serp-item')
        #  number of images
        images_number = len(self._elements)
        while images_number < img_limit:
            try:
                #  scroll the page
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                #  waiting for upload images
                time.sleep(DELAY)
                #  recalculating the number of images on page
                self._elements = browser.find_elements(By.CSS_SELECTOR, 'div.serp-item')
                new_img_number = len(self._elements)
                #  if no new images found
                if new_img_number == images_number:
                    #  increase iter_count
                    self._iter_count += 1
                else:
                    #  refresh iter_count
                    self._iter_count = 0
                    self._logger.info(f"Found {images_number} images")
                #  update current images number
                images_number = new_img_number
                #  exit the loop when the number of iterations is exceeded (if something gone wrong)
                if self._iter_count > max_iterations:
                    break
                #  trying click button to upload more images(going to next page)
                self.__upload_more(browser)
            except Exception as err:
                self._logger.error(f"Error {err}. Going next")
                continue
        self._logger.info(f"Done! {images_number} images found")
        #  get links to images from element
        return self._find_images_links()

    def __upload_more(self, browser):
        """Click on 'upload more images' button if end of page has been reached"""
        try:
            browser.find_element(By.CLASS_NAME, 'more__button').click()
            #  increase uploads counter
            self._uploads += 1
            #  refreshing the iter count
            self._iter_count = 0
            self._logger.debug('Uploading more images...')
        #  if the end of the page hasn't been reached or there is no button - pass this step
        except:
            pass

    def _find_images_links(self):
        """Getting links of images from html-elements

        :return: list of links to images
        """
        self._logger.info("Creating links to images...")
        self._links_to_images = [json.loads(element.get_attribute("data-bem"))['serp-item']['img_href']
                                 for element in self._elements]
        return self._links_to_images

    def _save_image(self, url, dir_to_save=None):
        """Method for saving image by url

        :param url: link to image
        :param dir_to_save: folder name to store images (query string as default)
        """

        folder = self._create_folder(dir_to_save)
        try:
            urlretrieve(url, os.path.join(folder, f"{self.count}.jpg"))
            self._logger.debug(f"Img from: {url} successfully saved!")
            self.saved += 1
        except Exception as err:
            self._logger.debug(f"Can't save img from: {url}\ngenerated an exception: {err}")
            pass
        finally:
            self.count += 1

    def _save_all(self, workers=24, output_folder=None):
        """Saving all images in threads

        :param workers: number of threads
        :param output_folder: folder to save (will be created if not exists)
        """
        self._logger.info(f"Saving images to folder...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            #  creating list of futures
            future_to_url = [executor.submit(self._save_image, url, output_folder) for url in self._links_to_images]
            for future in concurrent.futures.as_completed(future_to_url):
                future.result()
        self._logger.info(f"{self.saved} of {self.count} images was saved")
        self.count = 0

    def _save_links(self, file_name=None):
        """Method to save links of images to txt file

        :param file_name: name of txt file ('query_string.txt' as default)
        """
        self._logger.info(f"Saving links to images...")
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

    def get_images(self, query, img_count=LIMIT, img_size=SIZE,
                    iter_limit=ITER, save_images=True, save_links_to_file=False):
        """Main method to use YandexImageGrabber class"""
        #  find elements and links
        self._find_image_elements(query, img_count, img_size, iter_limit)
        find_time = time.time()
        self._logger.info(f"Image search time: "
                          f"{str(datetime.timedelta(seconds=round(find_time - self.start_time)))}")
        # save images to folder
        if save_images:
            self._save_all()
            self._logger.info(f"Saving time: "
                              f"{str(datetime.timedelta(seconds=round(time.time() - find_time)))}")
        #  save links to file
        if save_links_to_file:
            self._save_links()

        self._logger.info(f"Total work time: "
                          f"{str(datetime.timedelta(seconds=round(time.time() - self.start_time)))}")


if __name__ == '__main__':
    """Example of using"""

    a = YandexImagesGrabber()
    a.get_images("Cat", 200)
