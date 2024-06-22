
import logging

# Create a logger

logger = logging.getLogger("destination-glide")
logger.setLevel(logging.DEBUG)

# Create a file handler
# TODO REMOVE?
handler = logging.FileHandler('destination-glide.log')
handler.setLevel(logging.INFO)
# Create a logging format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Add the handlers to the logger
logger.addHandler(handler)

def getLogger() -> logging.Logger: 
  return logger