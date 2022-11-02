from typing import Any

import settings


def shorten_string(value: Any, length: int = settings.MAX_DATA_LOG_LENGTH):
    value = str(value)
    if len(value) > length:
        value = value[:length] + '...'
    return value
