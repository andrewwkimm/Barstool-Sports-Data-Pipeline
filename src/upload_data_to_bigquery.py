"""Setup to upload PyArrow tables to BigQuery."""

import os

from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, SourceFormat, WriteDisposition
import pyarrow as pa

from utils import table_to_parquet_buffer


def upload_data_to_bigquery(
    data: pa.Table,
    dataset: str,
    project_id: str,
    table_id: str,
    if_exists: str = "append",
) -> None:
    """Uploads a Parquet buffer to BigQuery, creating the table if it doesn't exist."""
    load_dotenv()
    SERVICE_ACCOUNT_KEY = os.getenv("SERVICE_ACCOUNT_KEY")

    client = bigquery.Client.from_service_account_json(
        SERVICE_ACCOUNT_KEY,
        project=project_id,
    )

    full_table_id = f"{project_id}.{dataset}.{table_id}"

    write_disposition = {
        # "append": WriteDisposition.WRITE_APPEND,
        "replace": WriteDisposition.WRITE_TRUNCATE,
        # "fail": WriteDisposition.WRITE_EMPTY,
    }[if_exists]

    job_config = LoadJobConfig(
        source_format=SourceFormat.PARQUET,
        write_disposition=write_disposition,
        autodetect=True,
    )

    buffer = table_to_parquet_buffer(data)

    job = client.load_table_from_file(
        file_obj=buffer,
        destination=full_table_id,
        job_config=job_config,
    )
    job.result()
    print(f"Loaded to {full_table_id} with write_disposition={write_disposition}")
