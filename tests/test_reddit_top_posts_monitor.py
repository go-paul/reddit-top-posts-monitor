import json
import sys
import unittest
from unittest import TestCase
from unittest.mock import ANY
from unittest.mock import Mock
from unittest.mock import patch

from main import run


class TestRedditTopPostsMonitor(TestCase):
    subreddit = "AskReddit"
    reddit_response = {
        "kind": "Listing",
        "data": {
            "after": "t3_yi9yjf",
            "dist": 25,
            "modhash": "",
            "geo_filter": None,
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "subreddit": subreddit,
                        "score": 50000,
                        "id": "yiazab",
                        "author": "test_author_nickname",
                    },
                },
                {
                    "kind": "t3",
                    "data": {
                        "subreddit": subreddit,
                        "score": 1,
                        "id": "new_id",
                        "author": "test_author_nickname",
                    },
                },
            ],
            "before": None,
        },
    }

    previous_posts = [{
        "subreddit": subreddit,
        "score": 50001,
        "id": "yiazab",
        "author": "test_author_nickname",
    }, {
        "subreddit": subreddit,
        "score": 1,
        "id": "demoted_id",
        "author": "test_author_nickname",
    }]

    latest_data_lookup = [{
        "data_file": "AskReddit__20221101_042945.json",
        "subreddit": "AskReddit",
        "timestamp": "20221101_042945",
    }]

    def _get_current_response_json(self):
        return json.dumps(self.reddit_response)

    @patch('storage_file.StorageFile.update_latest_data_lookup')
    @patch('storage_file.StorageFile.create_data_diff')
    @patch('storage_file.StorageFile.update_data')
    @patch('storage_file.StorageFile.get_latest_data_lookup')
    @patch('storage_file.StorageFile.get_data')
    @patch('urllib.request.urlopen')
    def test_check_diff_success(
        self,
        mock_urlopen,
        mock_get_data,
        mock_get_latest_data_lookup,
        mock_update_data,
        mock_create_data_diff,
        mock_update_latest_data_lookup,
    ):
        mock_urlopen_read = Mock()
        mock_urlopen_read.read.side_effect = [self._get_current_response_json().encode('utf-8')]
        mock_urlopen.return_value = mock_urlopen_read
        mock_get_data.return_value = self.previous_posts
        mock_get_latest_data_lookup.return_value = self.latest_data_lookup

        sys.argv = ['main', '--subreddits', '["AskReddit"]']
        run()

        expected_posts = [
            {
                'subreddit': 'AskReddit',
                'score': 50000,
                'id': 'yiazab',
                'author': 'test_author_nickname',
            },
            {
                'subreddit': 'AskReddit',
                'score': 1,
                'id': 'new_id',
                'author': 'test_author_nickname',
            },
        ]
        expected_diff = {
            'timestamp_current': ANY,
            'timestamp_previous': ANY,
            'diff': {
                'new_posts': [{
                    'subreddit': 'AskReddit',
                    'score': 1,
                    'id': 'new_id',
                    'author': 'test_author_nickname',
                }],
                'demoted_post_ids': ['demoted_id'],
                'vote_changes': [{
                    'id': 'yiazab',
                    'vote_change': -1,
                }],
            },
        }
        expected_latest_data_lookup = [
            {
                "data_file": ANY,
                "subreddit": "AskReddit",
                "timestamp": ANY
            }
        ]

        mock_update_data.assert_called_once_with(self.subreddit, ANY, expected_posts)
        mock_create_data_diff.assert_called_once_with(self.subreddit, ANY, ANY, expected_diff)
        mock_update_latest_data_lookup.assert_called_once_with(expected_latest_data_lookup)


if __name__ == '__main__':
    unittest.main()
