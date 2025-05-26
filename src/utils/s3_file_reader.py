"""The S3 File Reader."""

import io
from typing import BinaryIO

import boto3


def read_s3_file(bucket: str, key: str) -> BinaryIO:
    """Reads a file from S3 and returns it as a binary stream."""
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read()
    data = io.BytesIO(content)
    return data
