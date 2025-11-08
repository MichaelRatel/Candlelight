import re
from collections import defaultdict
from typing import Generator, Iterable

import boto3
import duckdb
from botocore import UNSIGNED
from botocore.config import Config

S3_URL = "https://s3-cache.deadlock-api.com"
BUCKET_URL = f"{S3_URL}/db-snapshot"


def list_parquet_files() -> Generator[str, None, None]:
    s3 = boto3.client(
        "s3", config=Config(signature_version=UNSIGNED), endpoint_url=S3_URL
    )
    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket="db-snapshot", Prefix="public/")
    for page in page_iterator:
        for obj in page["Contents"]:
            key = obj["Key"]
            if not key.endswith(".parquet"):
                continue
            yield f"{BUCKET_URL}/{key}"


def group_parquet_files_by_table(file_urls: Iterable[str]) -> dict[str, list[str]]:
    table_files = defaultdict(list)
    indexed_file_pattern = re.compile(r"(.+)_(\d+)\.parquet$")
    simple_file_pattern = re.compile(r"(.+)\.parquet$")

    for url in file_urls:
        filename = url.split("/")[-1]
        if match_indexed := indexed_file_pattern.match(filename):
            table_name = match_indexed.group(1)
        else:
            match_simple = simple_file_pattern.match(filename)
            table_name = match_simple.group(1) if match_simple else filename
        table_files[table_name].append(url)
    return table_files


def get_tables() -> dict[str, list[str]]:
    return group_parquet_files_by_table(list_parquet_files())


def setup_views(con):
    tables = get_tables()
    for name, url in tables.items():
        print(f"Creating view for {name}")
        con.execute(f"DROP VIEW IF EXISTS {name}")
        con.execute(f"CREATE VIEW {name} AS FROM read_parquet({url})")

if __name__ == "__main__":
    with duckdb.connect() as con:
        setup_views(con)
        print("DuckDB is set up")

        con.sql("SELECT * FROM match_info WHERE ")
        # Put your queries here
