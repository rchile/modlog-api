import os
from dotenv import load_dotenv
from api.functions import try_int

load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')
DEFAULT_PAGE_LIMIT = try_int(os.getenv('DEFAULT_PAGE_LIMIT'), 20)
CORS_ORIGINS = [x for x in os.getenv('CORS_ORIGINS', '').split(',') if x]
HIDDEN_ACTIONS = [x for x in os.getenv('HIDDEN_ACTIONS', '').split(',') if x]
