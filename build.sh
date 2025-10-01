#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create media directories with proper permissions
mkdir -p /opt/render/project/src/media/{avatars,project,certificates,qr_code,leader_documents}
chmod -R 755 /opt/render/project/src/media

echo "Build completed successfully!"
