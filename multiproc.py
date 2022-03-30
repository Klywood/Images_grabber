import concurrent.futures
import os
import time

import requests

count = 1

os.makedirs('folder', exist_ok=True)

def save_image_from_url(url, output_folder):
    global count
    image = requests.get(url)
    output_path = os.path.join(output_folder, f'{count}.jpg')
    with open(output_path, "wb") as f:
        f.write(image.content)
    count += 1


def load(urls, output_folder):
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        #  creating dict: {future: url}
        future_to_url = [executor.submit(save_image_from_url, url, output_folder) for url in urls]
        for future in concurrent.futures.as_completed(future_to_url):
            #  get url of current future (for logs)
            # url = future_to_url[future]
            #  trying to execute the result
            try:
                future.result()
            #  if exception occurred -> go to next
            except Exception as exc:
                # print(f"{url} generated an exception: {exc}")
                pass


if __name__ == '__main__':
    with open('1.txt') as f:
        urls = f.read().split()
    print(f"Urls: {len(urls)}")
    start = time.time()
    load(urls, 'folder')

    print(time.time() - start)

    def _get_images_links(self):
        """Getting links of images from html-elements

        :return: list of links to images
        """
        for element in self._elements:
            #  create dict from attribute
            data = json.loads(element.get_attribute("data-bem"))
            link = data['serp-item']['img_href']
            # print(link)
            self._links_to_images.append(link)
        return self._links_to_images





    def get_link(self, element):
        data = json.loads(element.get_attribute("data-bem"))
        return data['serp-item']['img_href']


    def _get_images_links(self):
        """Getting links of images from html-elements

        :return: list of links to images
        """
        s = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            #  creating list of futures
            future_links = [executor.submit(self.get_link, elem) for elem in self._elements]
            for future in concurrent.futures.as_completed(future_links):
                self._links_to_images.append(future.result())
        print('convert', time.time() - s)
        return self._links_to_images