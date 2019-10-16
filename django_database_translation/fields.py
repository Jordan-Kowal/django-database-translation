# coding: utf-8
"""
Description:
    Contains helper functions and classes for models.Field instances
Fields:
    ForeignKeyCascade: ForeignKey set up for CASCADE 'on delete' with index
    NotEmptyCharField: Charfield that cannot be null nor an empty string
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
def ForeignKeyCascade(to, *args, **kwargs):
    """ForeignKey set up for CASCADE 'on delete' with index"""
    kwargs['db_index'] = True
    kwargs['on_delete'] = models.CASCADE
    kwargs['null'] = False
    return models.ForeignKey(to, *args, **kwargs)


def NotEmptyCharField(*args, **kwargs):
    """Charfield that cannot be null nor an empty string"""
    kwargs['blank'] = False
    kwargs['null'] = False
    return models.CharField(*args, **kwargs)


def TranslatedField(*args, **kwargs):
    """Field to use if your field must be translated. It will set a ForeignKey to our "Item" model."""
    kwargs['blank'] = True
    kwargs['db_index'] = True
    kwargs['default'] = ""
    kwargs['help_text'] = "The key will be automatically provided when the object is created"
    kwargs['on_delete'] = models.SET_DEFAULT
    kwargs['null'] = True
    return models.ForeignKey("django_database_translation.Item", *args, **kwargs)
