#!/bin/sh

set -e

virtualenv --clear --no-site-packages env

. env/bin/activate

pip install -r requirements.pip
