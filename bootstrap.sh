#!/bin/sh

set -e

virtualenv --clear --no-site-packages venv

. venv/bin/activate

pip install -r requirements.pip
