import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/bots/")

from speech-to-text-bot import app as application
application.secret_key = 'placeyourbotsecretkey'
