# coding: utf-8
"""
Description:
    Contains helper functions and classes for internal work of the application
Functions:
    all_instances_as_translated_dict: Transforms an iterable of mode instances into a list of dicts
    get_translation_from_item: Returns a Translation object or text when given an Item and a Language
    instance_as_translated_dict: Transforms (returns) a model instance into a dict containing all of its fields
    update_user_language: Updates the user current language following Django guildelines
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
from .models import Item, Language, Translation


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def all_instances_as_translated_dict(request, instances, depth=True):
    """
    Description:
        Transforms an iterable of mode instances into a list of dicts
        Each model instance will be turned into a dict containing all of its fields/values
        With "depth" set to True, ForeignKey will also be transformed into sub-dict
        Meaning you will be able to manipulate the dict in an HTML template much like an instance
    Args:
        request (HttpRequest): HttpRequest from Django, used to get the user's current language
        instances (iterable): An iterable of your model instances
        depth (bool, optional): Determines if FK will also be transformed into dicts. Defaults to True.
    Returns:
        list: A list of dicts, where each dict contains the fields/values of the initial instances
    """
    results = []
    for instance in instances:
        result = instance_as_translated_dict(request, instance, depth)
        results.append(result)
    return results


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


def instance_as_translated_dict(request, instance, depth=True):
    """
    Description:
        Transforms (returns) a model instance into a dict containing all of its fields
        With "depth" set to True, ForeignKey will also be transformed into sub-dict
        Meaning you will be able to manipulate the dict in an HTML template much like an instance
    Args:
        request (HttpRequest): HttpRequest from Django, used to get the user's current language
        instance (Model): An instance from any of your models
        depth (bool, optional): Determines if FK will also be transformed into dicts. Defaults to True.
    Returns:
        dict: A dict with all of the instance's fields and values
    """
    # Get the language from the session
    language_name = request.session.get(LANGUAGE_SESSION_KEY)
    language = Language.objects.get(django_language_name=language_name)
    # Loop over fields
    translated_dict = {}
    fields = instance._meta.get_fields()
    for field in fields:
        value = getattr(instance, field.name, None)
        if value is not None:
            value_type = type(value)
            # Case 1: Get the translation
            if value_type == Item:
                new_value = Translation.objects.get(item=value, language=language).text
            # Case 2: Go to the linked model and repeat the process (unless depth=False)
            elif issubclass(value_type, models.Model):
                if depth:
                    new_value = instance_as_translated_dict(request, value, depth)
                else:
                    new_value = value
            # Case 3: Keep the value as is
            else:
                new_value = value
            translated_dict[field.name] = new_value
    return translated_dict


def update_user_language(request, language_id):
    """
    Description:
        Updates the user current language following Django guildelines
        This will allow for both "Django" frontend translations and "our app" database translation
    Args:
        request (HttpRequest): Request object from Django, used to get to the session
        language_id (id/str): ID of the language in our database
    """
    language = Language.objects.get(id=language_id)
    activate(language.django_language_name)
    request.session[LANGUAGE_SESSION_KEY] = language.django_language_name
