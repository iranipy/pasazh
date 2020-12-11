#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import sys
from os import environ, getenv
from dotenv import load_dotenv

load_dotenv(override=True)


def main():
    """Run administrative tasks."""
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    host_port = f"{getenv('HOST')}:{getenv('PORT')}"
    try:
        sys.argv[2] = host_port
    except IndexError:
        sys.argv.append(host_port)

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
