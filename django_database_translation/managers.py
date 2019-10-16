# coding: utf-8
"""
Description:
    Contains custom managers to help with our models
Managers:
    NoBulkManager: Prevents the use of the bulk_create method
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
# > Model Managers
# --------------------------------------------------------------------------------
class NoBulkCreateManager(models.Manager):
    """Prevents the use of the bulk_create method"""
    def bulk_create(self, objs, **kwargs):
        raise NotImplementedError("Cannot use bulk_create on this model")
