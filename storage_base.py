from typing import List
from typing import Optional


class StorageBase:
    """ Abstract data handling class """

    def create_data_diff(
        self, subreddit: str, timestamp_previous: str, timestamp_current: str, data: dict,
    ):
        raise NotImplementedError

    def get_data(self, subreddit: str, timestamp: str) -> Optional[List[dict]]:
        raise NotImplementedError

    def get_latest_data_lookup(self) -> dict:
        raise NotImplementedError

    def update_data(self, subreddit: str, timestamp: str, data: List[dict]):
        raise NotImplementedError

    def update_latest_data_lookup(self, data: List[dict]):
        raise NotImplementedError
