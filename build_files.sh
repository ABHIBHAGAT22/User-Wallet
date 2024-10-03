#!/bin/bash

# Ensure pip is installed
echo "Checking for pip..."
python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip

# Build the project
echo "Building the project..."
python3.9 -m pip install -r requirements.txt

echo "Make Migration..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

echo "Collect Static..."
python3.9 manage.py collectstatic --noinput --clear
