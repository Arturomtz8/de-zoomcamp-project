import io
from pathlib import Path
from typing import Union

import pandas as pd
from prefect.filesystems import GCS
from prefect_gcp.cloud_storage import GcsBucket

gcs_block: GCS = GCS.load("ghost-stories-bucket-path")


def read_posts() -> pd.DataFrame:
    """
    Read parquet posts from google cloud storage and return df
    """
    posts_content = gcs_block.read_path("posts_ghosts_stories.parquet")
    df = pd.read_parquet((io.BytesIO(posts_content)))
    return df


def read_comments() -> pd.DataFrame:
    """
    Read parquet comments from google cloud storage and return df
    """
    comments_content = gcs_block.read_path("comments_ghosts_stories.parquet")
    df = pd.read_parquet((io.BytesIO(comments_content)))
    return df


def write_to_gcs(
    local_path: Union[Path, str], gcs_bucket_path: Union[Path, str]
) -> None:
    gcs_bucket_block = GcsBucket.load("bucket-zoomcamp")
    gcs_bucket_block.upload_from_path(from_path=local_path, to_path=gcs_bucket_path)
    print(f"succesfully uploaded to {gcs_bucket_path}")
