#!/bin/sh

. .venv/bin/activate

bin/alembic upgrade head \
  && python3 -m app.main
