import json
import logging
import os
from typing import List
from typing import Optional
from typing import Union

from storage_base import StorageBase
from utils import shorten_string

logger = logging.getLogger(__name__)


class StorageFile(StorageBase):
    """ Data handling based on file system """

    PREFIX = '[FileStorage] '
    LATEST_DATA_LOOKUP_FILENAME = 'latest_data_lookup.json'


    def __init__(self, data_dir: str):
        super().__init__()
        self.data_dir = data_dir
        self.latest_data_lookup_path = self._make_path(self.LATEST_DATA_LOOKUP_FILENAME)


    def create_data_diff(
        self, subreddit: str, timestamp_previous: str, timestamp_current: str, data: dict,
    ):
        file_path = self._make_path(f'{subreddit}__{timestamp_previous}__{timestamp_current}.json')
        logger.debug(f'{self.PREFIX}Saving diff into file {file_path} - {shorten_string(data)}')
        self._write_file(file_path, data)


    def get_data(self, subreddit: str, timestamp: str) -> Optional[dict]:
        file_path = self._make_path(f'{subreddit}__{timestamp}.json')
        return self._read_file(file_path)


    def get_latest_data_lookup(self) -> Optional[List[dict]]:
        return self._read_file(self.latest_data_lookup_path)


    def _make_path(self, name: str):
        return os.path.join(self.data_dir, name)


    def _read_file(self, file_path: str) -> Optional[dict]:
        logger.debug(f'{self.PREFIX}Reading file {file_path}')

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    file_data = json.loads(f.read())
                    logger.debug(f'{self.PREFIX}File data: {shorten_string(file_data)}')
                    return file_data
            except Exception:
                logger.exception(f'{self.PREFIX}Could not read file {file_path}')
                raise

        return


    def update_data(self, subreddit: str, timestamp: str, data: List[dict]):
        file_path = self._make_path(f'{subreddit}__{timestamp}.json')
        logger.debug(f'{self.PREFIX}Saving data into file {file_path} - {shorten_string(data)}')
        self._write_file(file_path, data)


    def update_latest_data_lookup(self, data: List[dict]):
        logger.debug(
            f'{self.PREFIX}Updating latest data lookup file {self.latest_data_lookup_path} - '
            f'{shorten_string(data)}'
        )

        old_data = self.get_latest_data_lookup()
        if old_data:
            old_data_by_subreddit = {row['subreddit']: row for row in old_data}
            for row in data:
                old_row = old_data_by_subreddit.get(row['subreddit'])
                if old_row:
                    old_data.remove(old_row)
            data += old_data

        self._write_file(self.latest_data_lookup_path, data)


    def _write_file(self, file_path: str, data: Union[dict, list]):
        with open(file_path, 'w') as f:
            try:
                json.dump(data, f, indent=2, sort_keys=True)
            except Exception:
                logger.exception(
                    f'{self.PREFIX}Could not update file {file_path} with data '
                    f'{shorten_string(data)}'
                )
                raise
