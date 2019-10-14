# coding: utf-8
"""
Description:
    This file allows us to create forms to be used on the website.
    Forms can be created from scratch, linked to models, and wrapped around existing forms.
Classes:
    DynamicTranslationForm: Form to use in a ModelAdmin for any model that has fields to translate.
    LanguageSelection: Generic form for the Language model, with only the ID field
Functions:
    create_translation_fieldname: Generates a unique fieldname based on a given Translation instance
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django import forms

# Third-party

# Local
from .models import Language


# --------------------------------------------------------------------------------
# > Classes
# --------------------------------------------------------------------------------
class DynamicTranslationForm(forms.ModelForm):
    """
    Form to use in a ModelAdmin for any model that has fields to translate.
    It will allow you to display and edit the Translation instances linked to the object.
    Since fields are dynamically generated, you must override the get_fieldsets method in the admin (or else they won't show)
    The "TranslatedAdmin" ModelAdmin natively use this form.
    """

    # ----------------------------------------
    # Core Methods
    # ----------------------------------------
    def __init__(self, *args, **kwargs):
        """Overridden method to dynamically add a new field for each Translation linked with our object"""
        super(DynamicTranslationForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.set_translation_info()
            for translation in self.translations:
                self.fields[translation["fieldname"]] = translation["field"]
                self.initial[translation["fieldname"]] = translation["instance"].text

    def save(self, commit=True):
        """Overridden method to save the updated Translation texts"""
        if self.instance.pk:
            for translation in self.translations:
                obj = translation["instance"]
                fieldname = translation["fieldname"]
                value = self.cleaned_data[fieldname]
                obj.text = value
                obj.save()
        return super(DynamicTranslationForm, self).save(commit=commit)

    # ----------------------------------------
    # Custom Methods
    # ----------------------------------------
    def set_translation_info(self):
        """
        Finds all the Translation instances linked to our object, and stores their info in an attribute
        The attribute is a list of dict, each dict containing the information of one translation
        """
        obj = self.instance
        information = []
        translations = obj.get_translations()
        for translation in translations:
            fieldname = create_translation_fieldname(translation)
            information.append({
                "instance": translation,
                "fieldname": fieldname,
                "field": forms.CharField(required=False, widget=forms.Textarea)
            })
        self.translations = information


class LanguageSelection(forms.Form):
    """
    Generic form for the Language model, with only the ID field
    Can be useful if you need a frontend form where the user choses his language
    """

    # ----------------------------------------
    # Choices
    # ----------------------------------------
    def available_languages():
        """Returns all the available language in the database"""
        languages = Language.objects.all()
        choices = [(language.id, language.name) for language in languages]
        return choices

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    language_id = forms.ChoiceField(
        label="",
        required=True,
        choices=available_languages,
        widget=forms.RadioSelect,
    )

    # ----------------------------------------
    # Custom Validation Methods
    # ----------------------------------------
    def clean_language_id(self):
        """
        Custom validator for the "language_id" field
        Checks if the language exists, or raises an error
        """
        language_id = self.cleaned_data.get("language_id")
        try:
            Language.objects.get(id=language_id)
            return language_id
        except Language.DoesNotExist:
            raise forms.ValidationError("ID Language incorrecte")


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def create_translation_fieldname(translation):
    """
    Description:
        Generates a unique fieldname based on a given Translation instance
    Args:
        translation (Translation): Translation instance from our Translation model
    Returns:
        str: The generated field name
    """
    field = translation.item.field.name
    language = translation.language.name
    fieldname = "{} in {} (id={})".format(field, language, translation.id)
    return fieldname
