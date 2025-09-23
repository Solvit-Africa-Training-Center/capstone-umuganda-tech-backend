#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create media directories for production file uploads
mkdir -p media/avatars
mkdir -p media/project
mkdir -p media/certificates
mkdir -p media/qr_code

echo "Build completed successfully!"