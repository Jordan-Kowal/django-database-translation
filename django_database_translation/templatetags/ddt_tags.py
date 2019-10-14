# coding: utf-8
"""
Description:
    This file contains custom filters that can be used in templates
Filters:
    db_trans: Returns the translated text from the database, based on the current user's language
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django import template
from django.utils.translation import LANGUAGE_SESSION_KEY

# Third-party

# Local
from django_database_translation.models import Item, Language, Translation


# --------------------------------------------------------------------------------
# > Setup
# --------------------------------------------------------------------------------
register = template.Library()


# --------------------------------------------------------------------------------
# > Filters
# --------------------------------------------------------------------------------
@register.simple_tag(name="db_trans", takes_context=True)
def db_trans(context, field):
    """
    Description:
        Returns the translated text from the database, based on the current user's language
        If the field cannot be translated, return the original data
    Args:
        context (dict): Template's context, automatically passed as 1st argument
        field (Item): Should be an Item instance. If not, the function won't do anything
    Returns:
        str: Will return the translated text of the Item (or the original data)
    """
    if isinstance(field, Item):
        # Finding the language
        session = context.request.session
        language_name = session[LANGUAGE_SESSION_KEY]
        language = Language.objects.get(django_language_name=language_name)
        # Getting the translated text
        translation = Translation.objects.get(item=field, language=language)
        return translation.text
    else:
        return field
