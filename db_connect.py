import re
from collections import defaultdict
from typing import Generator, Iterable
#from locktuah import input_data

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
        if name == "match_info" or name == "match_player":
            print(f"Creating view for {name}")
            con.execute(f"DROP VIEW IF EXISTS {name}")
            con.execute(f"CREATE VIEW {name} AS FROM read_parquet({url})")

if __name__ == "__main__":
    with duckdb.connect() as con:
        setup_views(con)
        print("DuckDB is set up")

        relation = con.query(f"SELECT * FROM match_info WHERE match_outcome='TeamWin' AND match_mode='Ranked' ORDER BY start_time DESC LIMIT 50;")
        
        while res := relation.fetchone(): # for each match we have gathered
            player_relation = con.query(f"SELECT * FROM match_player WHERE match_id={res[0]}") # get player relation
            match_data = {} # make match data dict
            all_players_list = [] # make player list
            for i in range(0, len(relation.columns)-1): # for all matches we want to use
                match_data[relation.columns[i]] = res[i] #connect data from query to dict
                while player_res := player_relation.fetchone(): # for each player in match
                    player_data = {}
                    for j in range(0, len(player_relation.columns)-1): 
                        player_data[player_relation.columns[j]] = player_res[j] # add player data to dict
                    all_players_list.append(player_data)
            #input_data(match_data, all_players_list)
        
        print(relation.show())
