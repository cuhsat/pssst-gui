#!/bin/bash
set -o errexit

if [ ! -d bower ]; then
    bower install
fi

python pssst-html.py $*
