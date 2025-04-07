from pathlib import Path


# Режимы вывода результатов
PRETTY = 'pretty'
FILE = 'file'


# URL-адреса и пути
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URl = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = 'downloads'
RESULTS_DIR = 'results'


# Форматы даты и времени
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


# Статусы PEP
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}


# Настройки логирования
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOGS_CONST = 'logs'
LOGS_FILE = 'parser.log'
