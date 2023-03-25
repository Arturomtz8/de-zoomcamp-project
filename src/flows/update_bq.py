import pandas as pd
from gc_funcs.reader_writer import read_comments, read_posts
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect_gcp import GcpCredentials


@task(log_prints=True)
def write_bq(bq_table: str, df: pd.DataFrame, color: str) -> None:
    """Write DataFrame to BiqQuery"""

    gcp_credentials = GcpCredentials.load("gcp-credentials-zoomcamp")
    google_project_id = Secret.load("google-project-id")

    df.to_gbq(
        destination_table=bq_table,
        project_id=google_project_id.get(),
        credentials=gcp_credentials.get_credentials_from_service_account(),
        if_exists="replace",
    )


@flow()
def main():
    df_comments_from_bucket = read_comments()
    df_posts_from_bucket = read_posts()
    write_bq()
