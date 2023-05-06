# local_path = Path("data/ghost_stories/posts_ghosts_stories.parquet")
from typing import Union

import pytest

min_len_df = 1000
min_len_secret = 7


def test_df_posts_is_not_empty(
    fixture_posts_from_gcs: pytest.fixture,
) -> Union[ValueError, bool]:
    if len(fixture_posts_from_gcs) < min_len_df:
        raise ValueError("Posts dataframe wasn't loaded")


def test_df_comments_is_not_empty(
    fixture_comments_from_gcs: pytest.fixture,
) -> Union[ValueError, bool]:
    if len(fixture_comments_from_gcs) < min_len_df:
        raise ValueError("Comments dataframe wasn't loaded")


def test_secret_reddit_client_id(
    fixture_get_secret: pytest.fixture,
) -> Union[ValueError, bool]:
    secret = fixture_get_secret("reddit-client-id")
    if len(secret) < min_len_secret:
        raise ValueError("Secret wasn't loaded")


def test_secret_reddit_client_secret(
    fixture_get_secret: pytest.fixture,
) -> Union[ValueError, bool]:
    secret = fixture_get_secret("reddit-client-secret")
    if len(secret) < min_len_secret:
        raise ValueError("Secret wasn't loaded")


def test_secret_reddit_user_agent(
    fixture_get_secret: pytest.fixture,
) -> Union[ValueError, bool]:
    secret = fixture_get_secret("reddit-user-agent")
    if len(secret) < min_len_secret:
        raise ValueError("Secret wasn't loaded")


def test_secret_reddit_username(
    fixture_get_secret: pytest.fixture,
) -> Union[ValueError, bool]:
    secret = fixture_get_secret("reddit-username")
    if len(secret) < min_len_secret:
        raise ValueError("Secret wasn't loaded")


def test_reddit_client(fixture_client_reddit: pytest.fixture) -> Union[TypeError, bool]:
    subreddit = fixture_client_reddit.subreddit("AccidentalRenaissance")
    for submission in subreddit.top(time_filter="day", limit=10):
        print(submission.id)
        if type(submission.id) != str:
            raise TypeError("Submission id is not present")


# def test_write_local(df: pd.DataFrame, parquet_files_dir: Path) -> bool:
#     df.to_parquet(parquet_files_dir, compression="gzip")
