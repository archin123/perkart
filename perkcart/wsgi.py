"""
WSGI config for perkcart project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perkcart.settings')

application = get_wsgi_application()
app = application

# Auto-initialize fallback SQLite in /tmp if running in production without external database
from pathlib import Path
is_prod = bool(os.getenv('VERCEL') or os.getenv('VERCEL_ENV') or not (Path(__file__).resolve().parent.parent / '.env').exists())

if is_prod:
    db_url = os.getenv('DATABASE_URL') or os.getenv('Database_url') or ''
    if not db_url or (not db_url.startswith('postgres://') and not db_url.startswith('postgresql://')):
        tmp_db = Path('/tmp') / 'db.sqlite3'
        if not tmp_db.exists() or tmp_db.stat().st_size == 0:
            try:
                from django.core.management import call_command
                call_command('migrate', interactive=False)
                try:
                    call_command('seed_data')
                except Exception:
                    pass
            except Exception as e:
                print(f"Serverless SQLite init notice: {e}")



