import io
import sys
from pathlib import Path
from typing import List

import pandas as pd
import praw
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect_gcp.cloud_storage import GcsBucket


@task(log_prints=True)
def read_from_gcs(gcs_path: str) -> pd.DataFrame:
    gcs_block = GcsBucket.load("bucket-zoomcamp")
    contents = gcs_block.read_path(gcs_path)
    df = pd.read_parquet((io.BytesIO(contents)))
    print(df.shape)
    # df.to_csv("test.csv")
    return df




@task(tags="extract reddit posts")
def extract_posts(subreddit_name: str, df_from_bucket: pd.DataFrame) -> pd.DataFrame:
    all_posts_list = list()
    post_ids_list_in_gcs = df_from_bucket["post_id"].tolist()
    REDDIT_CLIENT_ID = Secret.load("reddit-client-id")
    REDDIT_CLIENT_SECRET = Secret.load("reddit-client-secret")
    REDDIT_USER_AGENT = Secret.load("reddit-user-agent")
    REDDIT_USERNAME = Secret.load("reddit-username")
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID.get(),
        client_secret=REDDIT_CLIENT_SECRET.get(),
        user_agent=REDDIT_USER_AGENT.get(),
        username=REDDIT_USERNAME.get(),
    )

    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.top(time_filter="day", limit=20):
        if str(submission.id) not in post_ids_list_in_gcs:
            print("found new posts")
            author = submission.author
            author_flair_text = submission.author_flair_text
            clicked = submission.clicked
            distinguished = submission.distinguished
            edited = submission.edited
            post_id = submission.id
            is_original_content = submission.is_original_content
            locked = submission.locked
            name = submission.name
            title = submission.title
            text = submission.selftext
            num_comments = submission.num_comments
            score = submission.score
            url = submission.url
            saved = submission.saved
            created_at = submission.created_utc
            num_comments = submission.num_comments
            over_18 = submission.over_18
            spoiler = submission.spoiler
            stickied = submission.stickied
            upvote_ratio = submission.upvote_ratio
            dict_poll_data = dict()
            try:
                poll_data = submission.poll_data
                poll_total_vote_count = poll_data.total_vote_count
                poll_voting_end_timestamp = poll_data.voting_end_timestamp
                for option in poll_data.options:
                    dict_poll_data[f"poll_option_{option.text}"] = int(
                        option.vote_count
                    )
                dict_poll_data["total_vote_count"] = int(poll_total_vote_count)
                dict_poll_data["voting_end_timestamp"] = float(
                    poll_voting_end_timestamp
                )
                print(dict_poll_data)
            except AttributeError:
                pass

            dict_post_preview = {
                "author": str(author),
                "author_flair_text": str(author_flair_text),
                "clicked": bool(clicked),
                "distinguished": bool(distinguished),
                "edited": bool(edited),
                "post_id": str(post_id),
                "is_original_content": bool(is_original_content),
                "locked": bool(locked),
                "post_fullname": str(name),
                "post_title": str(title),
                "post_text": str(text),
                "num_comments": int(num_comments),
                "post_score": float(score),
                "post_url": str(url),
                "saved": bool(saved),
                "created_at": float(created_at),
                "num_comments": str(num_comments),
                "over_18": bool(over_18),
                "spoiler": bool(spoiler),
                "stickied": bool(stickied),
                "upvote_ratio": float(upvote_ratio),
            }
            if dict_poll_data:
                dict_post_preview.update(dict_poll_data)

            all_posts_list.append(dict_post_preview)

    df_raw = pd.DataFrame(all_posts_list)
    if df_raw.empty:
        print("no new data available")
        raise Exception("no new data available")

    return df_raw


@task(log_prints=True)
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df["created_at"] = pd.to_datetime(df["created_at"], unit="s")
    try:
        df["voting_end_timestamp"] = pd.to_datetime(
            df["voting_end_timestamp"], unit="ms"
        )
    except KeyError:
        pass
    return df


@task(log_prints=True)
def concat_df(new_df: pd.DataFrame, df_from_bucket: pd.DataFrame) -> pd.DataFrame:
    concatenated_df = pd.concat([df_from_bucket, new_df])
    return concatenated_df


@task(log_prints=True)
def write_local(df: pd.DataFrame) -> Path:
    local_path = Path(f"data/ghost_stories/posts_ghosts_stories.parquet")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    print(df.shape)
    df.to_parquet(local_path, compression="gzip")
    return local_path


@task(log_prints=True)
def write_to_gcs(local_path: Path, gcs_bucket_path: str) -> None:
    gcs_block = GcsBucket.load("bucket-zoomcamp")
    gcs_block.upload_from_path(from_path=local_path, to_path=gcs_bucket_path)


@flow()
def scrape_reddit():
    gcs_bucket_path = Secret.load("bucket-zoomcamp-path")
    gcs_bucket_path = gcs_bucket_path.get()
    df_from_bucket = read_from_gcs(gcs_bucket_path)
    df_raw = extract_posts("Ghoststories", df_from_bucket)
    new_df = clean_df(df_raw)
    concatenated_df = concat_df(new_df, df_from_bucket)
    local_path = write_local(concatenated_df)
    write_to_gcs(local_path, gcs_bucket_path)


if __name__ == "__main__":
    scrape_reddit()
