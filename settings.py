import os
from dotenv import load_dotenv
from api.functions import try_int, csv_list

load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')
DEFAULT_PAGE_LIMIT = try_int(os.getenv('DEFAULT_PAGE_LIMIT'), 20)
CORS_ORIGINS = csv_list(os.getenv('CORS_ORIGINS', ''))
HIDDEN_ACTIONS = csv_list(os.getenv('HIDDEN_ACTIONS', ''))
