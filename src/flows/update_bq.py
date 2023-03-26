import pandas as pd
from gc_funcs.reader_writer import read_comments, read_posts
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect_gcp import GcpCredentials


@task(log_prints=True)
def write_bq(df_from_gcs: pd.DataFrame) -> None:
    bq_table = "reddit_data.raw_posts_ghosts"
    google_project_id = Secret.load("google-project-id")
    gcp_credentials = GcpCredentials.load("gcp-credentials-zoomcamp")

    df_from_gcs.to_gbq(
        destination_table=bq_table,
        project_id=google_project_id.get(),
        credentials=gcp_credentials.get_credentials_from_service_account(),
        if_exists="replace",
    )
    print("successfully uploaded")


@flow()
def update_posts_and_comments_in_bq():
    df_posts_from_gcs = read_posts()
    write_bq(df_posts_from_gcs) 


if __name__ == "__main__":
    update_posts_and_comments_in_bq()
