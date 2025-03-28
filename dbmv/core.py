import os
import tempfile
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import click
import boto3
from botocore.exceptions import ClientError

def parse_db_uri(uri: str) -> tuple[str, str, str, str]:
    parsed = urlparse(uri)
    
    if parsed.scheme != 'postgresql':
        raise click.BadParameter(f'Invalid URI scheme: {parsed.scheme}. Must be postgresql://')
    
    if not all([parsed.hostname, parsed.username, parsed.password, parsed.path]):
        raise click.BadParameter(f'Invalid URI: {uri}. Must include host, username, password, and database name')
    
    return (
        parsed.hostname,
        parsed.username,
        parsed.password,
        parsed.path.lstrip('/')
    )

def parse_s3_uri(uri: str) -> tuple[str, str]:

    parsed = urlparse(uri)
    
    if parsed.scheme != 's3':
        raise click.BadParameter(f'Invalid URI scheme: {parsed.scheme}. Must be s3://')
    
    if not parsed.netloc:
        raise click.BadParameter(f'Invalid URI: {uri}. Must include bucket name')
    
    return (parsed.netloc, parsed.path.lstrip('/'))

def upload_to_s3(dump_file: Path, bucket: str, key: str) -> bool:
    """Upload a dump file to S3."""
    print(f"Uploading dump to s3://{bucket}/{key}...")
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(str(dump_file), bucket, key)
        print("Upload completed successfully!")
        return True
    except ClientError as e:
        print(f"Error uploading to S3: {str(e)}")
        return False

def download_from_s3(dump_file: Path, bucket: str, key: str) -> bool:
    """Download a dump file from S3."""
    print(f"Downloading dump from s3://{bucket}/{key}...")
    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(bucket, key, str(dump_file))
        print("Download completed successfully!")
        return True
    except ClientError as e:
        print(f"Error downloading from S3: {str(e)}")
        return False

def dump_database(host: str, user: str, password: str, database: str, dump_file: Path) -> bool:
    print("Dumping from source server...")
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    try:
        subprocess.run([
            "pg_dump",
            "-h", host,
            "-U", user,
            "-d", database,
            "-Fc",
            "-f", str(dump_file)
        ], env=env, check=True)
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to dump database from source server")
        return False

def restore_database(host: str, user: str, password: str, database: str, dump_file: Path) -> bool:
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    print("Recreating database on target server...")
    try:
        # Drop database if exists
        subprocess.run([
            "psql",
            "-h", host,
            "-U", user,
            "-d", "postgres",
            "-c", f'DROP DATABASE IF EXISTS "{database}";'
        ], env=env, check=True)
        
        # Create new database
        subprocess.run([
            "psql",
            "-h", host,
            "-U", user,
            "-d", "postgres",
            "-c", f'CREATE DATABASE "{database}" OWNER {user};'
        ], env=env, check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to recreate database on target server")
        return False
    
    print("Restoring to target server...")
    try:
        subprocess.run([
            "pg_restore",
            "-h", host,
            "-U", user,
            "-d", database,
            "--no-owner",
            "--no-privileges",
            str(dump_file)
        ], env=env, check=True)
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to restore database to target server")
        return False

def copy_db(source_uri: str, target_uri: str) -> bool:
    source_scheme = urlparse(source_uri).scheme
    target_scheme = urlparse(target_uri).scheme
    
    with tempfile.TemporaryDirectory() as dump_dir:
        dump_file = Path(dump_dir) / "database.dump"
        
        # PostgreSQL to S3
        if source_scheme == 'postgresql' and target_scheme == 's3':
            source_host, source_user, source_pass, database_name = parse_db_uri(source_uri)
            s3_bucket, s3_key = parse_s3_uri(target_uri)
            
            print(f"Copying database from {source_host} to s3://{s3_bucket}/{s3_key}")
            
            if not dump_database(source_host, source_user, source_pass, database_name, dump_file):
                return False
            
            return upload_to_s3(dump_file, s3_bucket, s3_key)
            
        # S3 to PostgreSQL
        elif source_scheme == 's3' and target_scheme == 'postgresql':
            s3_bucket, s3_key = parse_s3_uri(source_uri)
            target_host, target_user, target_pass, database_name = parse_db_uri(target_uri)
            
            print(f"Copying database from s3://{s3_bucket}/{s3_key} to {target_host}")
            
            if not download_from_s3(dump_file, s3_bucket, s3_key):
                return False
            
            return restore_database(target_host, target_user, target_pass, database_name, dump_file)
            
        else:
            print("Error: Source and target URIs must be either postgresql:// or s3:// schemes")
            return False
