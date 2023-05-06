from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import praw
import pytest
from prefect.blocks.system import Secret

from flows.gc_funcs.reader_writer import get_comments_from_gcs  # noqa: E402
from flows.gc_funcs.reader_writer import get_posts_from_gcs


@pytest.fixture()
def parquet_files_dir() -> Path:
    with TemporaryDirectory() as parquet_dir:
        dir_path = Path(parquet_dir)
        yield dir_path


@pytest.fixture(scope="module")
def fixture_posts_from_gcs() -> pd.DataFrame:
    df = get_posts_from_gcs()
    return df


@pytest.fixture(scope="module")
def fixture_comments_from_gcs() -> pd.DataFrame:
    df = get_comments_from_gcs()
    return df


@pytest.fixture(scope="function")
def fixture_get_secret() -> str:
    def get_secret(secret_name: str):
        top_secret = Secret.load(secret_name)
        return top_secret.get()

    return get_secret


@pytest.fixture(scope="function")
def fixture_client_reddit(fixture_get_secret) -> praw.Reddit:
    reddit_client_id = fixture_get_secret("reddit-client-id")
    reddit_client_secret = fixture_get_secret("reddit-client-secret")
    reddit_user_agent = fixture_get_secret("reddit-user-agent")
    reddit_username = fixture_get_secret("reddit-username")
    reddit = praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=reddit_user_agent,
        username=reddit_username,
    )
    return reddit
