import io
import pickle
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import praw
import prawcore
from praw.models import MoreComments
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect.filesystems import GCS
from prefect_gcp.cloud_storage import GcsBucket


@task(log_prints=True)
def convert_bytes_to_df(
    posts_content: bytes, comments_content: bytes
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_posts = pd.read_parquet((io.BytesIO(posts_content)))
    df_comments = pd.read_parquet((io.BytesIO(comments_content)))
    # print(df_comments)

    return df_posts, df_comments


@task(tags="extract reddit comments", log_prints=True)
def extract_comments(
    df_posts_from_bucket: pd.DataFrame, df_comments_from_bucket: pd.DataFrame
) -> pd.DataFrame:
    comments_ids_list_in_gcs = df_comments_from_bucket["comment_id"].to_list()
    all_comments_list = list()
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
    for post_url in df_posts_from_bucket["post_url"]:
        try:
            submission = reddit.submission(url=post_url)
            for top_level_comment in submission.comments:
                if (
                    isinstance(top_level_comment, MoreComments)
                    or top_level_comment.id in comments_ids_list_in_gcs
                ):
                    continue

                author = top_level_comment.author
                comment_id = top_level_comment.id
                body = top_level_comment.body
                created_at = top_level_comment.created_utc
                distinguished = top_level_comment.distinguished
                edited = top_level_comment.edited
                is_submitter = top_level_comment.is_submitter
                post_id = top_level_comment.link_id
                link_comment = top_level_comment.permalink
                score = top_level_comment.score

                dict_post_preview = {
                    "author": str(author),
                    "comment_id": str(comment_id),
                    "body": str(body),
                    "created_at": float(created_at),
                    "distinguished": bool(distinguished),
                    "edited": bool(edited),
                    "is_author_submitter": bool(is_submitter),
                    "post_id": str(post_id),
                    "link_comment": str(link_comment),
                    "comment_score": float(score),
                }

                all_comments_list.append(dict_post_preview)
        except (praw.exceptions.InvalidURL, prawcore.exceptions.NotFound) as e:
            """
            Some url posts are images, or gifs or maybe the post was deleted
            """
            continue

    df_comments_raw = pd.DataFrame(all_comments_list)
    if df_comments_raw.empty:
        print("no new data available")
        raise Exception("no new data available")
    # df_comments_raw.to_csv("test.csv")
    return df_comments_raw


@task(log_prints=True)
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df["created_at"] = pd.to_datetime(df["created_at"], unit="s")
    return df


@task(log_prints=True)
def concat_df(
    new_df: pd.DataFrame, df_comments_from_bucket: pd.DataFrame
) -> pd.DataFrame:
    concatenated_df = pd.concat([df_comments_from_bucket, new_df])
    return concatenated_df


@task(log_prints=True)
def write_local(df: pd.DataFrame) -> Path:
    local_path = Path(f"data/ghost_stories/comments_ghosts_stories.parquet")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(local_path, compression="gzip")
    return local_path


@task(log_prints=True)
def write_to_gcs(local_path: Path, gcs_bucket_path: str) -> None:
    gcs_block = GcsBucket.load("bucket-zoomcamp")
    gcs_block.upload_from_path(from_path=local_path, to_path=gcs_bucket_path)


@flow()
def scrape_reddit_comments():

    gcs_block: GCS = GCS.load("ghost-stories-bucket-path")
    posts_content = gcs_block.read_path("posts_ghosts_stories.parquet")
    comments_content = gcs_block.read_path("comments_ghosts_stories.parquet")
    df_posts_from_bucket, df_comments_from_bucket = convert_bytes_to_df(
        posts_content, comments_content
    )
    df_raw = extract_comments(df_posts_from_bucket, df_comments_from_bucket)
    new_df = clean_df(df_raw)
    concatenated_df = concat_df(new_df, df_comments_from_bucket)
    local_path = write_local(concatenated_df)
    write_to_gcs(local_path=local_path, gcs_bucket_path=local_path)


if __name__ == "__main__":
    scrape_reddit_comments()
