#!/bin/bash

if [ ! -e .ve ]; then
    virtualenv --no-site-packages .ve
fi

source .ve/bin/activate
export STATIC_DEPS=true
pip install -r requirements.txt

pip uninstall -y MySQL-python
easy_install -Z vendors/MySQL-python-1.2.3.zip