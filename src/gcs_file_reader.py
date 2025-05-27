"""The Google Cloud Storage File Reader."""

# type: ignore

import io
import os
from typing import BinaryIO

from dotenv import load_dotenv
from google.cloud import storage


def read_gcs_file(bucket: str, blob_name: str) -> BinaryIO:
    """Reads a file from Google Cloud Storage and returns it as a binary stream."""
    load_dotenv()
    SERVICE_ACCOUNT_KEY = os.getenv("SERVICE_ACCOUNT_KEY")

    client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_KEY)
    bucket_obj = client.bucket(bucket)
    blob = bucket_obj.blob(blob_name)
    content = blob.download_as_bytes()
    data = io.BytesIO(content)
    return data
