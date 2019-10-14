# coding: utf-8
"""
Description:
    Contains helper functions and classes for internal work of the application
Fields:
    ForeignKeyCascade: ForeignKey set up for CASCADE 'on delete' with index
    NotEmptyCharField: Charfield that cannot be null nor an empty string
Functions:
    get_translation_from_item: Returns a Translation object or text when given an Item and a Language
    update_user_language: Updates the user current language following Django guildelines
Managers:
    NoBulkManager: Prevents the use of the bulk_create method
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django.apps import apps
from django.db import models
from django.utils.translation import activate, LANGUAGE_SESSION_KEY

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


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def get_translation_from_item(item=None, item_id=None, language=None, language_id=None, as_text=False):
    """
    Description:
        Returns a Translation object or text when given an Item and a Language
        You must provide either "item" or "item_id"
        You must provide either "language" or "language_id"
    Args:
        item (Item, optional): Item instance from the translation app. Defaults to None.
        item_id (int, optional): ID of the Item instance. Defaults to None.
        language (Language, optional): Language instance from the translation app. Defaults to None.
        language_id (int, optional): ID of the Language instance. Defaults to None.
        as_text (bool, optional): Indicates whether to return the instance or its text. Defaults to False.
    Raises:
        TypeError: must provide either 'item' or 'item_id'
        TypeError: must provide either 'language' or 'language_id'
    Returns:
        Translation/String/None: Either a Translation instance, the Translation's text, or None
    """
    # Checking if we have the right parameters
    if (not item and not item_id) or (item and item_id):
        raise TypeError("You must provide either 'item' or 'item_id'. Not none, nor both.")
    if (not language and not language_id) or (language and language_id):
        raise TypeError("You must provide either 'language' or 'language_id'. Not none, nor both.")
    # Keeping only one of each
    params = {
        "item": item,
        "item_id": item_id,
        "language": language,
        "language_id": language_id,
    }
    params = {key: value for key, value in params.items() if value}
    # Finding the translation instance and returning it
    try:
        translation_model = apps.get_model("django_database_translation", "Translation", True)
        translation = translation_model.objects.get(**params)
        if as_text:
            return translation.text
        else:
            return translation
    except translation_model.DoesNotExist:
        return None


def update_user_language(request, language_id):
    """
    Description:
        Updates the user current language following Django guildelines
        This will allow for both "Django" frontend translations and "our app" database translation
    Args:
        request (HttpRequest): Request object from Django, used to get to the session
        language_id (id/str): ID of the language in our database
    """
    from .models import Language
    language = Language.objects.get(id=language_id)
    activate(language.django_language_name)
    request.session[LANGUAGE_SESSION_KEY] = language.django_language_name


# --------------------------------------------------------------------------------
# > Model Managers
# --------------------------------------------------------------------------------
class NoBulkCreateManager(models.Manager):
    """Prevents the use of the bulk_create method"""
    def bulk_create(self, objs, **kwargs):
        raise NotImplementedError("Cannot use bulk_create on this model")
