# Configuration settings

# Server settings
HOST = "0.0.0.0"
PORT = 8000

# Frontend URL for CORS
FRONTEND_URL = "http://localhost:8001"

# Scraping settings
SCRAPER_TIMEOUT = 60  # seconds
SCRAPER_MAX_RETRIES = 3
SCRAPER_RETRY_DELAY = 2  # seconds
BATCH_SIZE = 100  # reviews per batch

# Output settings
OUTPUT_DIR = "output"

# Rate limiting
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 60  # seconds

# Validation
MIN_URL_LENGTH = 20
MAX_HINT_LENGTH = 100
MAX_DATE_RANGE = 365  # days

# Logging
LOG_LEVEL = "INFO"
