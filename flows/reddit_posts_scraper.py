from pathlib import Path

import pandas as pd
import praw
from gc_funcs.reader_writer import get_posts_from_gcs, write_to_gcs
from prefect import flow, task
from prefect.blocks.system import Secret


@task(tags="extract reddit posts", log_prints=True)
def extract_posts(subreddit_name: str, df_from_bucket: pd.DataFrame) -> pd.DataFrame:
    all_posts_list = list()
    post_ids_list_in_gcs = df_from_bucket["post_id"].tolist()
    post_urls_list_in_gcs = df_from_bucket["post_url"].tolist()
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

    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.top(time_filter="day", limit=50):
        # id is not enough, also must take into account post_url
        if (
            str(submission.id) not in post_ids_list_in_gcs
            or str(submission.url) not in post_urls_list_in_gcs
        ):
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
            over_18 = submission.over_18
            spoiler = submission.spoiler
            stickied = submission.stickied
            upvote_ratio = submission.upvote_ratio

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
                "num_comments": str(num_comments),
                "post_score": float(score),
                "post_url": str(url),
                "saved": bool(saved),
                "created_at": float(created_at),
                "over_18": bool(over_18),
                "spoiler": bool(spoiler),
                "stickied": bool(stickied),
                "upvote_ratio": float(upvote_ratio),
            }

            all_posts_list.append(dict_post_preview)

    df_raw = pd.DataFrame(all_posts_list)
    if df_raw.empty:
        print("no new data available")
        raise Exception("no new data available")

    return df_raw


@task(log_prints=True)
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df["created_at"] = pd.to_datetime(df["created_at"], unit="s")
    return df


@task(log_prints=True)
def concat_df(new_df: pd.DataFrame, df_posts_from_bucket: pd.DataFrame) -> pd.DataFrame:
    concatenated_df = pd.concat([df_posts_from_bucket, new_df])
    return concatenated_df


@task(log_prints=True)
def write_local_and_to_gcs(df: pd.DataFrame) -> None:
    local_path = Path("data/ghost_stories/posts_ghosts_stories.parquet")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(local_path, compression="gzip")
    write_to_gcs(local_path=local_path, gcs_bucket_path=local_path)


@flow()
def scrape_reddit() -> None:
    df_posts_from_bucket = get_posts_from_gcs()
    df_raw = extract_posts(
        subreddit_name="Ghoststories+Ghosts+Paranormal+ParanormalEncounters",
        df_from_bucket=df_posts_from_bucket,
    )
    new_df = clean_df(df_raw)
    concatenated_df = concat_df(new_df, df_posts_from_bucket)
    # delete dups because column "post_url" is being problematic
    concatenated_df.drop_duplicates(subset=["post_url"], keep="last", inplace=True)
    write_local_and_to_gcs(concatenated_df)


if __name__ == "__main__":
    scrape_reddit()
