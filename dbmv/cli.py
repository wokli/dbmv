#!/usr/bin/env python3

import sys
import click
from .core import copy_db

@click.command()
@click.option('--src', '-s', required=True, help='Source URI (postgresql://user:pass@host/dbname or s3://bucket/key)')
@click.option('--dst', '-d', required=True, help='Destination URI (postgresql://user:pass@host/dbname or s3://bucket/key)')
def main(src: str, dst: str):
    """
    Copy a PostgreSQL database between servers and S3.

    # Copy from PostgreSQL to S3

    dbmv --src 'postgresql://user:pass@db1.example.com/mydb' --dst 's3://my-bucket/backups/mydb.dump'
    
    # Restore from S3 to PostgreSQL

    dbmv --src 's3://my-bucket/backups/mydb.dump' --dst 'postgresql://user:pass@db2.example.com/mydb'
    """
    sys.exit(0 if copy_db(src, dst) else 1)

if __name__ == "__main__":
    main()