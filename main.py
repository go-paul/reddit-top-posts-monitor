import logging
import os.path
from argparse import ArgumentParser

from diff_calculator import DiffCalculator
from storage_file import StorageFile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def run():
    args_parser = ArgumentParser()
    args_parser.add_argument('-s', '--subreddits', type=eval, required=True)
    args, _ = args_parser.parse_known_args()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    storage = StorageFile(data_dir=data_dir)

    latest_data_lookup = storage.get_latest_data_lookup()
    latest_data_lookup_new = []

    for subreddit in args.subreddits:
        logger.info(f'*** Processing subreddit "{subreddit}" ***')
        diff_calculator = DiffCalculator(
            subreddit=subreddit,
            storage=storage,
            latest_data_lookup=latest_data_lookup,
        )
        try:
            latest_data_lookup_new.append(
                diff_calculator.calc()
            )
        except Exception:
            logger.exception(f'Error during diff calculation for subreddit "{subreddit}"')

    storage.update_latest_data_lookup(latest_data_lookup_new)


if __name__ == '__main__':
    run()
