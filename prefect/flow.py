"""Pipeline orchestration using Prefect."""

# flake8: noqa
# mypy: ignore-errors

import os
from pathlib import Path

from dotenv import load_dotenv
from prefect import flow, task
from prefect_dbt.cli.commands import DbtCoreOperation
from pyarrow import csv

from src.gcs_file_reader import read_gcs_file
from src.html_reader import read_html_file
from src.jsonl_reader import read_jsonl_file
from src.upload_data_to_bigquery import upload_data_to_bigquery


load_dotenv()

bucket_name = os.getenv("bucket_name") or "barstool_sports"
dataset = os.getenv("dataset") or "barstool_sports_data"
project_id = os.getenv("project_id") or "barstool-sports-461005"


@task
def process_and_upload_csv():
    csv_file = read_gcs_file(bucket_name, "BARSTOOL_PROD_CONTENT_PROD_CONTENTS_3.csv")
    csv_data = csv.read_csv(csv_file)
    upload_data_to_bigquery(csv_data, dataset, project_id, "prod_contents")


@task
def process_and_upload_html():
    html_file = read_gcs_file(bucket_name, "brands-talent-franchise.html")
    html_data = read_html_file(html_file)
    upload_data_to_bigquery(html_data, dataset, project_id, "brands_talent_franchise")


@task
def process_and_upload_jsonl():
    jsonl_file = read_gcs_file(bucket_name, "sampled_data.jsonl")
    jsonl_data = read_jsonl_file(jsonl_file)
    upload_data_to_bigquery(jsonl_data, dataset, project_id, "sample_data")


@flow
def trigger_dbt_flow():
    result = DbtCoreOperation(
        commands=["dbt run"],
        project_dir=Path("dbt"),
        profiles_dir=Path("dbt"),
    ).run()
    return result


@flow(name="Barstool-Sports-Data-Pipeline")
def main():
    process_and_upload_csv()
    process_and_upload_html()
    process_and_upload_jsonl()
    trigger_dbt_flow()


if __name__ == "__main__":
    main()
