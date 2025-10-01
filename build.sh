#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create media directories and copy existing files
mkdir -p /opt/render/project/src/media/{avatars,project,certificates,qr_code,leader_documents}

# Copy media files if they exist in the repo
if [ -d "media" ]; then
    cp -r media/* /opt/render/project/src/media/ || true
fi

chmod -R 755 /opt/render/project/src/media

echo "Build completed successfully!"
