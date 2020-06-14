#!/usr/bin/env bash

set +x

git checkout .
git pull

python3 lambda_function.py