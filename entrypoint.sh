#!/bin/sh

. .venv/bin/activate

alembic upgrade head \
  && python3 -m app.main
