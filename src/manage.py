#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    """
    
    TODO add code to look in a defined folder for an .env file - first look for production and then development
    If neither are found, then raise an error and quit
    
    """

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gsicosttool.settings.development")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
