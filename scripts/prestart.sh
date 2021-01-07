#!/bin/bash

echo "## Run alembic migrations ##"

alembic upgrade head

echo "## Complete update ##"