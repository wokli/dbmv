# dbmv

Copy PostgreSQL databases between servers and S3 buckets.

## Dependencies

- Python 3.6+
- PostgreSQL client tools (`pg_dump`, `pg_restore`, `psql`)
- AWS credentials configured (for S3 operations)
- `pg_dump` and `pg_restore` installed

## Install
```bash
pip install git+https://github.com/wokli/dbmv
```

## Usage

```bash
# Copy database between PostgreSQL servers
dbmv \
  --src 'postgresql://user:pass@source-host/dbname' \
  --dst 'postgresql://user:pass@target-host/dbname'

# Backup to S3
dbmv \
  --src 'postgresql://user:pass@source-host/dbname' \
  --dst 's3://my-bucket/backups/dbname.dump'

# Restore from S3
dbmv \
  --src 's3://my-bucket/backups/dbname.dump' \
  --dst 'postgresql://user:pass@target-host/dbname'
```
