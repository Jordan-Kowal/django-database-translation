# coding: utf-8
"""
Description:
    This model is used to store translations. To do so, we built the following structure:
    - Field --> Item --> Translation <-- Language
    - Field and Language instances must be inserted manually
    - Item and Translation instances are both created and deleted automatically, using "signals.py" and "CASCADE"
    A few things to note are:
        - We can traceback a Translation to its application and model (using ContentType)
        - If a model creates other model instances with signals, we block its "bulk_create" method with a custom manager
        - As a reminder, bulk_create does not return PK, so we can only use it on the "last" table of any chain reaction
Abstract Models:
    TranslatedModel: Abstract model to be used as parent for any model that requires translation
Models:
    Field: Lookup table that contains the list of fields eligible for translation.
    Item: Content table that stores the actual item that must be translated (object + field).
    Language: Lookup table that contains the list of available languages.
    Translation: Content table that stores all the available translations
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator
from django.db import models

# Third-party

# Local
from .fields import ForeignKeyCascade, NotEmptyCharField
from .managers import NoBulkCreateManager


# --------------------------------------------------------------------------------
# > Abstract Models
# --------------------------------------------------------------------------------
class TranslatedModel(models.Model):
    """
    Abstract model used as a template for any model that requires translation. It provides:
        - A basic "meta_info" field
        - A manager that prevents the "objects.bulk_create" method
        - A basic "__str__" method
        - methods to easily get translation info from the instance
    """
    # ----------------------------------------
    # Constants
    # ----------------------------------------
    TRANSLATED = True

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    meta_info = models.CharField(
        blank=False,
        help_text="Information on the instance (not visible in the frontend)",
        max_length=100,
        null=False,
        verbose_name="Meta Information",
    )

    # ----------------------------------------
    # Custom Managers
    # ----------------------------------------
    objects = NoBulkCreateManager()

    # ----------------------------------------
    # META, str, save, get_absolute_url
    # ----------------------------------------
    class Meta:
        """Metadata to configure our model in the database"""
        abstract = True

    def __str__(self):
        """Returns the meta information"""
        return self.meta_info

    # ----------------------------------------
    # Custom Methods
    # ----------------------------------------
    def get_content_type_instance(self):
        """Returns the ContentType instance of our object"""
        app_label = self._meta.app_label
        model = self.__class__.__name__.lower()
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        return content_type

    def get_translated_fields(self):
        """Returns a QuerySet of all the Field instances associated with the Model of our instance"""
        content_type = self.get_content_type_instance()
        fields = Field.objects.filter(content_type=content_type)
        return fields

    def get_translated_items(self):
        """Returns a QuerySet of all the Item instances associated with our instance"""
        fields = self.get_translated_fields()
        items = Item.objects.filter(object_id=self.id, field__in=fields)
        return items

    def get_translations(self):
        """Returns a QuerySet of all the Translation instances associated with our instance"""
        items = self.get_translated_items()
        translations = Translation.objects.filter(item__in=items)
        return translations


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class Field(models.Model):
    """
    Lookup table that contains the list of fields eligible for translation.
    Each Field is linked to a ContentType (ie an application's model).
    Field sends a signal on create that generates "Item" instances.
    """

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    content_type = ForeignKeyCascade(
        ContentType,
        verbose_name="Content Type"
    )
    name = NotEmptyCharField(
        max_length=100,
        verbose_name="Field name"
    )

    # ----------------------------------------
    # Custom Managers
    # ----------------------------------------
    objects = NoBulkCreateManager()

    # ----------------------------------------
    # META, str, save, get_absolute_url
    # ----------------------------------------
    class Meta:
        """Metadata to configure our model in the database"""
        db_table = "ddt_fields"
        indexes = []
        ordering = [
            "content_type",
            "name"
        ]
        unique_together = [
            ['content_type', 'name'],
        ]
        verbose_name = "Field"
        verbose_name_plural = "Fields"

    def __str__(self):
        """Returns 'application.model.field' as a string"""
        app = self.content_type.app_label
        model = self.content_type
        return "{}.{}.{}".format(app, model, self.name)

    # ----------------------------------------
    # Custom Properties
    # ----------------------------------------
    def count_items(self):
        """Returns the amount of Item instances attached to this field"""
        return Item.objects.filter(field=self).count()
    count_items.short_description = "Items"

    def count_missing_translations(self):
        """Returns the amount of empty Translation instances attached to this field"""
        return Translation.objects.filter(item__field=self).filter(text="").count()
    count_missing_translations.short_description = "Missing Translations"

    def get_app_name(self):
        """Returns the application name as a string"""
        return self.content_type.app_label
    get_app_name.short_description = "Application"


class Item(models.Model):
    """
    Content table that stores the actual item that must be translated (object + field).
    Since it contains ID from different tables, we used a GenericForeignKey.
    Item sends a signal on create that generates "Translation" instances.
    """

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    field = ForeignKeyCascade(
        "Field",
        verbose_name="Field"
    )
    object_id = models.PositiveIntegerField(
        null=False,
        db_index=True,
        verbose_name="Object ID"
    )
    content_type = ForeignKeyCascade(
        ContentType,
        verbose_name="Content Type"
    )
    of = GenericForeignKey('content_type', 'object_id')

    # ----------------------------------------
    # Custom Managers
    # ----------------------------------------
    objects = NoBulkCreateManager()

    # ----------------------------------------
    # META, str, save, get_absolute_url
    # ----------------------------------------
    class Meta:
        """Metadata to configure our model in the database"""
        db_table = "ddt_items"
        indexes = []
        ordering = []
        unique_together = [
            ['field', 'object_id'],
        ]
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self):
        """Returns the 'application.model.field.object_id' as a string"""
        return "{}.{}".format(self.field, self.object_id)

    # ----------------------------------------
    # Custom Properties
    # ----------------------------------------
    def count_missing_translations(self):
        """Returns the amount of empty Translation instances attached to this item"""
        return Translation.objects.filter(item=self).filter(text="").count()
    count_missing_translations.short_description = "Missing Translations"


class Language(models.Model):
    """
    Lookup table that contains the list of available languages.
    Used for translating the database and the frontend.
    Language sends a signal on create that generates "Translation" instances.
    """

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    name = NotEmptyCharField(
        max_length=100,
        unique=True,
        verbose_name="Name"
    )
    iso2 = NotEmptyCharField(
        max_length=2,
        unique=True,
        validators=[MinLengthValidator(2)],
        verbose_name="ISO2"
    )
    iso3 = NotEmptyCharField(
        max_length=3,
        unique=True,
        validators=[MinLengthValidator(3)],
        verbose_name="ISO3"
    )
    django_language_name = NotEmptyCharField(
        help_text="Should match a value from settings.LANGUAGES, such as 'fr-FR' or 'en-US'",
        max_length=5,
        unique=True,
        verbose_name="Django language name"
    )

    # ----------------------------------------
    # Custom Managers
    # ----------------------------------------
    objects = NoBulkCreateManager()

    # ----------------------------------------
    # META, str, save, get_absolute_url
    # ----------------------------------------
    class Meta:
        """Metadata to configure our model in the database"""
        db_table = "ddt_languages"
        indexes = []
        ordering = ["name"]
        unique_together = []
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        """Returns the language name"""
        return self.name

    def save(self, *args, **kwargs):
        """Overrides the save method to 'upper' ISO2 and ISO3"""
        self.iso2 = self.iso2.upper()
        self.iso3 = self.iso3.upper()
        super().save(*args, **kwargs)

    # ----------------------------------------
    # Custom Methods
    # ----------------------------------------
    def count_missing_translations(self):
        """Returns the amount of empty Translation instances attached to this language"""
        return Translation.objects.filter(language=self).filter(text="").count()
    count_missing_translations.short_description = "Missing Translations"


class Translation(models.Model):
    """
    Content table that stores all the available translations.
    Each entry contains a language and an item (both ForeignKey).
    """

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    language = ForeignKeyCascade(
        "Language",
        verbose_name="Language"
    )
    item = ForeignKeyCascade(
        "Item",
        verbose_name="Item"
    )
    text = models.TextField(
        default="",
        null=False,
        verbose_name="Translated text"
    )

    # ----------------------------------------
    # META, str, save, get_absolute_url
    # ----------------------------------------
    class Meta:
        db_table = "ddt_translations"
        indexes = [
            models.Index(
                fields=["item", "language"],
                name="idx_item_lang",
            )
        ]
        ordering = []
        unique_together = [
            ["language", "item"],
        ]
        verbose_name = "Translation"
        verbose_name_plural = "Translations"

    def __str__(self):
        """Returns a string with the 'item' and the 'language'"""
        return "{} ({})".format(self.item, self.language)

    # ----------------------------------------
    # Custom Properties
    # ----------------------------------------
    def truncated_text(self):
        """Returns the first 20 characters from self.text"""
        try:
            return self.text[:20]
        except IndexError:
            return self.text
    truncated_text.short_description = "Translated Text"
