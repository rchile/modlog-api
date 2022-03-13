import os
from dotenv import load_dotenv
from api.functions import try_int

load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')
DEFAULT_PAGE_LIMIT = try_int(os.getenv('DEFAULT_PAGE_LIMIT'), 20)
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')

if CORS_ORIGINS == ['']:
    CORS_ORIGINS = []
