# local_path = Path("data/ghost_stories/posts_ghosts_stories.parquet")


def test_df_posts_is_not_empty(fixture_posts_from_gcs) -> bool:
    assert len(fixture_posts_from_gcs) > 1000


def test_df_comments_is_not_empty(fixture_comments_from_gcs) -> bool:
    assert len(fixture_comments_from_gcs) > 1000


def test_secret_reddit_client_id(fixture_get_secret):
    secret = fixture_get_secret("reddit-client-id")
    assert len(secret) > 7


def test_secret_reddit_client_secret(fixture_get_secret):
    secret = fixture_get_secret("reddit-client-secret")
    assert len(secret) > 7


def test_secret_reddit_user_agent(fixture_get_secret):
    secret = fixture_get_secret("reddit-user-agent")
    assert len(secret) > 7


def test_secret_reddit_username(fixture_get_secret):
    secret = fixture_get_secret("reddit-username")
    assert len(secret) > 7


def test_reddit_client(fixture_client_reddit):
    subreddit = fixture_client_reddit.subreddit("AccidentalRenaissance")
    for submission in subreddit.top(time_filter="day", limit=10):
        print(submission.id)
        assert type(submission.id) == str


# def test_write_local(df: pd.DataFrame, parquet_files_dir: Path) -> bool:
#     df.to_parquet(parquet_files_dir, compression="gzip")
