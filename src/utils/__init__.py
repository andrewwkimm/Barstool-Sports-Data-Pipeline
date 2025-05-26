"""Utilites for the Barstool Sports Data Pipeline."""

from .html_reader import read_html
from .s3_file_reader import read_s3_file

all = [
    read_html,
    read_s3_file,
]
