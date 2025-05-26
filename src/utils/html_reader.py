"""The HTML File Reader."""

from pathlib import Path
from typing import BinaryIO, List, Union

from lxml import html
import pyarrow as pa


def read_html_file(html_file: Union[BinaryIO, Path, str]) -> pa.Table:
    """Reads an HTML object and converts it to a PyArrow table."""
    tree = html.parse(html_file)
    rows = parse_html_file(tree)
    table = convert_to_table(rows)
    return table


def parse_html_file(tree: html.HtmlElement) -> List[List[str]]:
    """Parses an HTML file to an array."""
    data = []
    for row in tree.xpath("//table//tr[position()>1]"):
        cells = row.xpath("./td/text()")
        if len(cells) != 4:
            continue
        data.append(cells)
    return data


def convert_to_table(rows: List[List[str]]) -> pa.Table:
    """Converts extracted data to a PyArrow table."""
    table = pa.table(
        {
            "_ID": [str(r[0]) for r in rows],
            "NAME": [r[1] for r in rows],
            "SHORT_NAME": [r[2] for r in rows],
            "TYPE": [r[3] for r in rows],
        }
    )
    return table
