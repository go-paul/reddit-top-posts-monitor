# Reddit Top Posts Monitor

To run this script for specific subreddits:

```shell
python3 main.py --subreddits="['popular', 'askreddit']"
```

It will create files in `data` directory:

1. `latest_data_lookup.json` - info about latest data version for each subreddit
2. `askreddit_20221101_185256.json` (`SUBREDDIT__YYYYMMDD_HHMMSS.json`) - timestamped data snapshot for each subreddit
3. `askreddit__20221101_180712__20221101_180808.json` (`SUBREDDIT__YYYYMMDD_HHMMSS__YYYYMMDD_HHMMSS.json`) - data diff between two snapshots for each subreddit

## Unittests

To run tests:

```shell
python3 -m unittest tests/test_*
```
