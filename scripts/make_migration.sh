#!/usr/bin/env bash

export PYTHONPATH=.

echo -n "Enter migration comment: "
read comment

# Check if comment is empty
if [ -z "$comment" ]; then
  echo "Migration comment cannot be empty."
  exit 1
fi

# Make migration
alembic revision --autogenerate -m "$comment"
