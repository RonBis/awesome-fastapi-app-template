#! /usr/bin/env bash

export PYTHONPATH=.

# Run migrations
alembic upgrade head
