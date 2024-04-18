#!/usr/bin/env bash

alembic stamp head
alembic revision -m "init2" --autogenerate

alembic upgrade head

gunicorn --timeout=30 main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000