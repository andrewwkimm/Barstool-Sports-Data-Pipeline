"""The Barstool Sports Data Pipeline."""

__version__ = "0.1.0"

from .gcs_file_reader import read_gcs_file
from .html_reader import read_html_file
from .jsonl_reader import read_jsonl_file
from .s3_file_reader import read_s3_file
from .upload_data_to_bigquery import upload_data_to_bigquery

all = [
    read_gcs_file,
    read_html_file,
    read_jsonl_file,
    read_s3_file,
    upload_data_to_bigquery,
]
