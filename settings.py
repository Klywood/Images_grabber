""""Contains main settings for YandexImagesGrabber"""
# hide/show web browser during work (True-hide)
HIDE_BROWSER = True

#  logger settings
LOG_NAME = 'Img_grabber'
LOG_FOLDER = 'logs'
LOG_LEVEL = 'DEBUG'  # logger level
FH_level = 'DEBUG'  # to file
SH_level = 'INFO'  # to console

# main settings
LIMIT = 100  # num of images to found
SIZE = 'medium'  # size of images
ITER = 10  # max iterations without getting new images
#  delay in seconds for uploading new images between scrolling
DELAY = 0.1
#  name(path) of folder to save folders with images
MAIN_FOLDER = 'saved_images'
