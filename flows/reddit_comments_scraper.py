from pathlib import Path

import pandas as pd
import praw
import prawcore
from gc_funcs.reader_writer import (
    get_comments_from_gcs,
    get_posts_from_gcs,
    write_to_gcs,
)
from praw.models import MoreComments
from prefect import flow, task
from prefect.blocks.system import Secret


@task(tags="extract reddit comments", log_prints=True)
def extract_comments(
    df_posts_from_bucket: pd.DataFrame, df_comments_from_bucket: pd.DataFrame
) -> pd.DataFrame:
    comment_id_from_comments = set(df_comments_from_bucket["comment_id"].to_list())
    df_comments_from_bucket = df_comments_from_bucket.loc[
        df_comments_from_bucket["post_url"].notnull()
    ]
    posts_url_from_comments = set(df_comments_from_bucket["post_url"].to_list())
    posts_url_from_posts = set(df_posts_from_bucket["post_url"].to_list())
    # print(len(posts_url_from_comments_list_in_gcs))
    # print(len(df_posts_from_bucket["post_url"]))
    all_comments_list = list()
    reddit_client_id = Secret.load("reddit-client-id")
    reddit_client_secret = Secret.load("reddit-client-secret")
    reddit_user_agent = Secret.load("reddit-user-agent")
    reddit_username = Secret.load("reddit-username")
    reddit = praw.Reddit(
        client_id=reddit_client_id.get(),
        client_secret=reddit_client_secret.get(),
        user_agent=reddit_user_agent.get(),
        username=reddit_username.get(),
    )
    for post_url in posts_url_from_posts:
        if post_url not in posts_url_from_comments:
            try:
                submission = reddit.submission(url=post_url)
                for top_level_comment in submission.comments:
                    # some posts urls are deleted, so it is not enough to check
                    # post_url
                    if (
                        isinstance(top_level_comment, MoreComments)
                        or top_level_comment.id in comment_id_from_comments
                    ):
                        print(
                            "comment already in dataset or comment with more comments structure"  # noqa: E501
                        )
                        continue
                    print("new comments found")
                    author = top_level_comment.author
                    comment_id = top_level_comment.id
                    submission_url = top_level_comment.submission.url
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
                        "post_url": str(submission_url),
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
                print(e)
                continue

    df_comments_raw = pd.DataFrame(all_comments_list)
    if df_comments_raw.empty:
        raise Exception("no new data available")
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
def write_local_and_to_gcs(df: pd.DataFrame) -> None:
    local_path = Path("data/ghost_stories/comments_ghosts_stories.parquet")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(local_path, compression="gzip")
    write_to_gcs(local_path=local_path, gcs_bucket_path=local_path)


@flow(log_prints=True)
def scrape_reddit_comments() -> None:
    df_posts_from_bucket = get_posts_from_gcs()
    df_comments_from_bucket = get_comments_from_gcs()
    df_raw = extract_comments(df_posts_from_bucket, df_comments_from_bucket)
    new_df = clean_df(df_raw)
    concatenated_df = concat_df(new_df, df_comments_from_bucket)
    # keep the last comment
    concatenated_df.drop_duplicates(
        subset=["author", "body", "created_at", "comment_id", "post_id"],
        keep="last",
        inplace=True,
    )
    write_local_and_to_gcs(concatenated_df)


if __name__ == "__main__":
    scrape_reddit_comments()
