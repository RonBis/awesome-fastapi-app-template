#! /usr/bin/env bash

set -e
set -x

export PYTHONPATH=.

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py

# Start object storage service (minio) if running locally (TODO: Introduce an env variable)
# sudo docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001" &>/dev/null
