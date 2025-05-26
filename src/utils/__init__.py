"""Utilites for the Barstool Sports Data Pipeline."""

from .gcs_file_reader import read_gcs_file
from .html_reader import read_html_file
from .jsonl_reader import read_jsonl_file
from .s3_file_reader import read_s3_file

all = [
    read_gcs_file,
    read_html_file,
    read_jsonl_file,
    read_s3_file,
]
