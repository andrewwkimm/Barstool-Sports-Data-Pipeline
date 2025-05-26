"""In-memory parquet file buffer."""

import io

import pyarrow as pa
import pyarrow.parquet as pq


def table_to_parquet_buffer(table: pa.Table) -> io.BytesIO:
    """Serializes a PyArrow table to an in-memory Parquet buffer."""
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    return buffer
