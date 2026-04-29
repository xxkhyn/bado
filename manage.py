#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv
from pathlib import Path

def main():
    """Run administrative tasks."""
    env_file = os.environ.get("DOTENV_FILE", ".env")
    if Path(env_file).exists():
        dotenv.load_dotenv(env_file)
    elif os.environ.get("DJANGO_ENV") == "production" and Path(".env.prod").exists():
        dotenv.load_dotenv(".env.prod")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'circle_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
