from prefect.filesystems import GCS
import pandas as pd
import io


gcs_block: GCS = GCS.load("ghost-stories-bucket-path")

def read_posts():
    posts_content = gcs_block.read_path("posts_ghosts_stories.parquet")
    df = pd.read_parquet((io.BytesIO(posts_content)))
    return df


def read_comments():
    comments_content = gcs_block.read_path("comments_ghosts_stories.parquet")
    df = pd.read_parquet((io.BytesIO(comments_content)))
    return df