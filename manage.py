#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "floxy.settings")
    os.environ.setdefault("DJANGO_RUNSERVER_HIDE_WARNING", "true")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Assurez-vous qu'il est installe et "
            "disponible dans votre environnement."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
