""""Contains main settings for YandexImagesGrabber"""
import logging
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


#
# class CustomFormatter(logging.Formatter):
#
#     grey = "\x1b[38;20m"
#     yellow = "\x1b[33;20m"
#     red = "\x1b[31;20m"
#     bold_red = "\x1b[31;1m"
#     reset = "\x1b[0m"
#     format = '%(asctime)s: %(levelname)s: %(name)s: %(message)s'
#
#     FORMATS = {
#         logging.DEBUG: grey + format + reset,
#         logging.INFO: grey + format + reset,
#         logging.WARNING: yellow + format + reset,
#         logging.ERROR: red + format + reset,
#         logging.CRITICAL: bold_red + format + reset
#     }
#
#     def format(self, record):
#         log_fmt = self.FORMATS.get(record.levelno)
#         formatter = logging.Formatter(log_fmt)
#         return formatter.format(record)
#