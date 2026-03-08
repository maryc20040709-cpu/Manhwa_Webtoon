import os

# Configuration settings

# Environment Variables
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

# Other settings
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Example settings
# Replace with your actual configuration
def load_config():
    return {
        'database_url': DATABASE_URL,
        'secret_key': SECRET_KEY,
        'debug': DEBUG,
        'allowed_hosts': ALLOWED_HOSTS,
    }