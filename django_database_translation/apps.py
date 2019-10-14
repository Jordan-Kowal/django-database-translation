# coding: utf-8
"""
This file allows us to change the config of our app.
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django.apps import AppConfig

# Third-party

# Local


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
class DjangoDatabaseTranslationConfig(AppConfig):
    name = 'django_database_translation'

    def ready(self):
        """Allows us to intercept and use signals"""
        import django_database_translation.signals
