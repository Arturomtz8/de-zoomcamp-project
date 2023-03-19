def import_to_big_query(
    data,
    context,
    dataset="UPDATE_DATASET_HERE",
    table="UPDATE_TABLE_HERE",
    verbose=True,
):
    def vprint(s):
        if verbose:
            print(s)

    vprint(f"Event ID: {context.event_id}")
    vprint(f"Event type: {context.event_type}")
    vprint("Importing required modules.")

    from google.cloud import bigquery

    vprint(f"This is the data: {data}")

    input_bucket_name = data["bucket"]
    source_file = data["name"]
    uri = f"gs://{input_bucket_name}/{source_file}"

    vprint(f'Getting the data from bucket "{uri}"')

    if str(source_file).lower().endswith(".parquet"):

        client = bigquery.Client()
        dataset_ref = client.dataset(dataset)

        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        job_config.schema_update_options = [
            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
        ]

        job_config.source_format = bigquery.SourceFormat.PARQUET

        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

        load_job = client.load_table_from_uri(
            uri, dataset_ref.table(table), job_config=job_config
        )

        vprint(f"Starting job {load_job.job_id}")

        load_job.result()
        vprint("Job finished.")

        destination_table = client.get_table(dataset_ref.table(table))
        vprint(f"Loaded {destination_table.num_rows} rows.")
        vprint("File imported successfully.")
    else:
        vprint("Not an importable file.")
