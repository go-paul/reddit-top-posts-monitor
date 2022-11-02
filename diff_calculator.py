import json
import logging
import urllib.request
from datetime import datetime
from typing import List
from typing import Optional

import settings
from storage_base import StorageBase
from utils import shorten_string

logger = logging.getLogger(__name__)


class DiffCalculator:

    PREFIX = '[DiffCalculator] '


    def __init__(self, subreddit: str, storage: StorageBase, latest_data_lookup: List[dict]):
        self.storage = storage
        self.subreddit = subreddit
        self.latest_data_lookup = latest_data_lookup


    def calc(self) -> dict:
        current_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        error = None
        current_data = []
        try:
            current_data = self._get_current_data()
        except Exception as e:
            error = str(e)

        self.storage.update_data(self.subreddit, current_timestamp, current_data)

        lookup = self._get_latest_data_lookup()
        if lookup:
            previous_timestamp = lookup['timestamp']
            previous_data = self._get_previous_data(previous_timestamp)

            diff_record = {
                'timestamp_current': current_timestamp,
                'timestamp_previous': previous_timestamp,
            }
            if not error and previous_data:
                try:
                    diff = self._calc_diff(previous_data, current_data)
                    diff_record.update({
                        'diff': diff,
                    })
                except Exception as e:
                    error = str(e)

            if error:
                diff_record.update({
                    'error': error,
                })

            self.storage.create_data_diff(
                self.subreddit, previous_timestamp, current_timestamp, diff_record,
            )

        return {
            'subreddit': self.subreddit,
            'timestamp': current_timestamp,
            'data_file': f'{self.subreddit}__{current_timestamp}.json',
        }


    def _calc_diff(self, previous_data: List[dict], current_data: List[dict]) -> dict:
        previous_data_by_ids = {p['id']: p for p in previous_data}

        # Select new data
        new_data = [p for p in current_data if p['id'] not in previous_data_by_ids]

        # Select demoted posts IDs
        old_top_posts_ids = [p['id'] for p in previous_data[:settings.MONITORED_TOP_POSTS]]
        new_top_posts_ids = [p['id'] for p in current_data[:settings.MONITORED_TOP_POSTS]]
        demoted_post_ids = [i for i in old_top_posts_ids if i not in new_top_posts_ids]

        # Select posts with changed vote count
        vote_changes = []
        for new_post in current_data:
            new_post_id = new_post['id']
            old_post = previous_data_by_ids.get(new_post_id)
            if old_post:
                old_post_score = old_post['score']
                new_post_score = new_post['score']
                if new_post_score != old_post_score:
                    vote_changes.append({
                        'id': new_post_id,
                        'vote_change': new_post_score - old_post_score,
                    })

        diff = {
            'new_posts': new_data,
            'demoted_post_ids': demoted_post_ids,
            'vote_changes': vote_changes,
        }

        logger.debug(f'{self.PREFIX}Calculated data diff: {shorten_string(diff)}')
        return diff


    def _get_current_data(self) -> List[dict]:
        url = settings.API_URL_PATTERN.format(subreddit=self.subreddit)
        url = f'{url}?limit={settings.REQUEST_LIMIT}'

        try:
            response = urllib.request.urlopen(url)
            deserialized_response = json.loads(response.read().decode('utf-8'))
        except Exception:
            logger.exception('Could not receive data from Reddit API')
            raise

        children = deserialized_response.get('data', {}).get('children', [])
        posts_data = [p['data'] for p in children]
        if not posts_data:
            raise Exception('Received empty data from Reddit API')

        logger.debug(f'{self.PREFIX}Current data: {shorten_string(posts_data)}')
        return posts_data


    def _get_latest_data_lookup(self):
        if not self.latest_data_lookup:
            return

        for lookup in self.latest_data_lookup:
            if lookup['subreddit'] == self.subreddit:
                return lookup


    def _get_previous_data(self, timestamp: str) -> Optional[List[dict]]:
        previous_data = None
        try:
            previous_data = self.storage.get_data(
                self.subreddit, timestamp,
            )
            logger.debug(f'{self.PREFIX}Previous data: {shorten_string(previous_data)}')
        except Exception:
            logger.exception(f'{self.PREFIX}Could not read previous subreddit data')

        return previous_data
