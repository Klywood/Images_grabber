import YandexImagesGrabber as yg

#  Input your query HERE:
q = 'Мeч'

#  Number of images to be found:
img_count = 500

if __name__ == '__main__':
    grabber = yg.YandexImagesGrabber()
    grabber.get_images(q, img_count)
