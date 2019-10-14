# coding: utf-8
"""
Description:
    Internal signal callbacks allow:
    --> Field to create Item
    --> Item to create Translation
    --> Language to create Translation
    External signal callbacks allow any declared table to create or delete related "Item" instance
    And those "Item" instances then create "Translation" instances using or internal signal callbacks
Signal Internal Callbacks:
    create_items_from_field: Creates a new Item instance for this field, for every existing object of the model's field
    create_translations_from_item: Creates Translation instances with our item for each available language
    create_translations_from_language: Creates new Translation entry for every unique "item" in Translation
Signal External Callbacks:
    create_translated_items: Creates Item instances everytime an object is created in a translated table
    delete_translated_items: Deletes Item instances everytime an object is deleted in a translated table
Applying the External Callbacks:
    This snippet allows us to get the models within the app that herit from our "TranslationModel"
    And then applies the external callbacks to those applications
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django.apps import apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Third-party

# Local
from .models import Field, Item, Language, Translation


# --------------------------------------------------------------------------------
# > Signal Internal Callbacks
# --------------------------------------------------------------------------------
@receiver(post_save, sender=Field)
def create_items_from_field(sender, instance, created, **kwargs):
    """
    Creates a new Item instance for this field, for every existing object of the model's field
    Technically, this callback does several things:
    - It gets all the existing objects from the model where our Field supposedly comes from
    - For each object, it creates the associated Item (Field + Object)
    - Then it adds the new Item PK as a FK back into the object instance
    Since "bulk_create" cannot be used on Item, so we loop to create them individually
    """
    if created:
        # Get the class model associated with the new Field
        app_name = instance.content_type.app_label
        model_name = instance.content_type.model
        target_model = apps.get_model(app_name, model_name)
        # For each object, creates a new item and adds the FK back into the object instance
        objects = target_model.objects.all()
        for obj in objects:
            item = Item.objects.create(field=instance, object_id=obj.pk, content_type=instance.content_type)
            setattr(obj, instance.name, item)
            obj.save()


@receiver(post_save, sender=Item)
def create_translations_from_item(sender, instance, created, **kwargs):
    """Creates Translation instances in every Language for our new Item"""
    if created:
        languages = Language.objects.all()
        if len(languages) > 0:
            translations = [Translation(item=instance, language=language) for language in languages]
            Translation.objects.bulk_create(translations)


@receiver(post_save, sender=Language)
def create_translations_from_language(sender, instance, created, **kwargs):
    """Creates Translation for our new Language and all existing Item instances"""
    if created:
        items = Item.objects.all()
        if len(items) > 0:
            translations = [Translation(language=instance, item=item) for item in items]
            Translation.objects.bulk_create(translations)


# --------------------------------------------------------------------------------
# > Signal External Callbacks
# --------------------------------------------------------------------------------
def create_translated_items(sender, instance, created, **kwargs):
    """
    Creates Item instances everytime an object is created in a translated table. Note that:
    - "bulk_create" cannot be used on Item, so we use a loop
    - we use "setattr" because we have the field name, not the Field instance
    """
    if created:
        fields = instance.get_translated_fields()
        if len(fields) > 0:
            for field in fields:
                content_type = instance.get_content_type_instance()
                item = Item.objects.create(field=field, object_id=instance.pk, content_type=content_type)
                setattr(instance, field.name, item)
                instance.save()
        else:
            raise RuntimeError("{} has no entry in the Field table".format(sender))


def delete_translated_items(sender, instance, **kwargs):
    """
    Deletes Item instances everytime an object is deleted in a translated table
    Then "Translations" are automatically deleted due to its CASCADE relationship with "Item"
    """
    fields = instance.get_translated_fields()
    if len(fields) > 0:
        # We get the FK towards the Item model and filter the missing key to avoid errors
        items = [getattr(instance, field.name) for field in fields]
        filtered_items = [x for x in items if x is not None]
        if len(filtered_items) > 0:
            # We have Item instances, but only want their "id" attribute
            id_list = map(lambda x: x.id, filtered_items)
            Item.objects.filter(pk__in=id_list).delete()


# --------------------------------------------------------------------------------
# > Applying the External Callbacks
# --------------------------------------------------------------------------------
# Getting the models subjects to translation
translated_models = []
for model in apps.get_models():
    try:
        if model.TRANSLATED:
            translated_models.append(model)
    except AttributeError:
        pass

# Applying our signals to those models:
for model in translated_models:
    receiver(post_save, sender=model)(create_translated_items)
    receiver(post_delete, sender=model)(delete_translated_items)
