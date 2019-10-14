# coding: utf-8
"""
Description:
    Contains helper functions and classes for models.Field instances
Fields:
    TranslatableField: Field to use if your field must be translated. It will set a ForeignKey to our "Item" model.
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django.db import models

# Third-party

# Local


# --------------------------------------------------------------------------------
# > Model Fields
# --------------------------------------------------------------------------------
def TranslatedField(*args, **kwargs):
    """Field to use if your field must be translated. It will set a ForeignKey to our "Item" model."""
    kwargs['blank'] = True
    kwargs['db_index'] = True
    kwargs['default'] = ""
    kwargs['help_text'] = "The key will be automatically provided when the object is created"
    kwargs['on_delete'] = models.SET_DEFAULT
    kwargs['null'] = True
    return models.ForeignKey("django_database_translation.Item", *args, **kwargs)
