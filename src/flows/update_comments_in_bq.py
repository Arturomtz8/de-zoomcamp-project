import pandas as pd
from gc_funcs.reader_writer import get_comments_from_gcs
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect_gcp import GcpCredentials


@task(log_prints=True)
def write_bq(
    bq_table: str,
    df_from_gcs: pd.DataFrame,
) -> None:
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
def update_comments_table_in_bq():
    df_comments_from_gcs = get_comments_from_gcs()
    write_bq("reddit_data.raw_comments_ghosts", df_comments_from_gcs)


if __name__ == "__main__":
    update_comments_table_in_bq()
