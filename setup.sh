#!/bin/bash

if [ ! -e .ve ]; then
    virtualenv --no-site-packages .ve
fi

source .ve/bin/activate
export STATIC_DEPS=true
pip install -r requirements.txt
