# coding: utf-8
"""
Description:
    This file allows us to personalize the admin interface.
    We can change the way tables and fields are displayed.
Helpers:
    ApplicationFilter: Allows filtering using the application name, on Field, Item, and Translation
    ContentTypeDropdown: Allows us to override how Content Type are displayed in a dropdown
Inlines:
    TranslationInline: Displays and allows editing of existing translations of an Item
Abstract Admins:
    TranslatedAdmin: ModelAdmin to use as parent for any model that has fields to translate
Admins:
    FieldAdmin: Customizes the Field model in the administration interface
    ItemAdmin: Customizes the Item model in the administration interface
    LanguageAdmin: Customizes the Language model in the administration interface
    TranslationAdmin: Customizes the Translation model in the administration interface
"""


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in

# Django
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelChoiceField

# Third-party

# Local
from .forms import DynamicTranslationForm, create_translation_fieldname
from .models import Field, Item, Language, Translation
from .signals import translated_models


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class ApplicationFilter(admin.SimpleListFilter):
    """Allows filtering using the application name on Field, Item, and Translation"""

    title = 'Application'
    parameter_name = 'Application'

    def lookups(self, request, model_admin):
        """Returns a list of tuples (value, label) that will be the filter options"""
        fields = Field.objects.all()
        results = {field.get_app_name() for field in fields}
        results = [(value, value.capitalize()) for value in results]
        return results

    def queryset(self, request, queryset):
        """Defines the results of the filter query"""
        # Getting the model name from URL
        url = request.build_absolute_uri("?")
        if url[-1] == "/":
            url = url[:-1]
        model_name = url.split("/")[-1]
        # Changing the query based on our model
        if self.value() is not None:
            if model_name in {"field", "item"}:
                return queryset.filter(content_type__app_label=self.value())
            elif model_name == "translation":
                return queryset.filter(item__content_type__app_label=self.value())
        else:
            return queryset


class ContentTypeDropdown(ModelChoiceField):
    """Allows us to override how Content Type are displayed in a dropdown"""

    def label_from_instance(self, obj):
        """Returns a string that specifies both the APP and the MODEL name"""
        app = obj.app_label.upper()
        model = obj.model.upper()
        return "({}) {}".format(app, model)


# --------------------------------------------------------------------------------
# > Inlines
# --------------------------------------------------------------------------------
class TranslationInline(admin.TabularInline):
    """Inline model to display the Translation instances on an Item (update) form"""

    # ----------------------------------------
    # Config
    # ----------------------------------------
    model = Translation
    can_delete = False
    extra = 0
    max_num = 0

    # ----------------------------------------
    # Fields
    # ----------------------------------------
    readonly_fields = ("language",)
    fieldsets = (
        [
            "",
            {
                "fields": [
                    "language",
                    "text"
                ]
            },
        ],
    )


# --------------------------------------------------------------------------------
# > Abstract Admins
# --------------------------------------------------------------------------------
class TranslatedAdmin(admin.ModelAdmin):
    """
    ModelAdmin to use as parent for any model that has fields to translate
    It comes with the "DynamicTranslationForm" and custom methods to display its fields
    """

    # ----------------------------------------
    # Config
    # ----------------------------------------
    form = DynamicTranslationForm

    # ----------------------------------------
    # Detail View
    # ----------------------------------------
    fieldsets = []

    # ----------------------------------------
    # Custom Methods
    # ----------------------------------------
    def get_form(self, request, obj=None, **kwargs):
        """Required for get_fieldsets"""
        kwargs['fields'] = flatten_fieldsets(self.fieldsets)
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        """
        Allows us to display the field dynamically created by "DynamicTranslationForm"
        The fieldnames in "DynamicTranslationForm" and this function must be identical
        In other words:
        - "DynamicTranslationForm" creates the fields
        - This function adds fields with the same name to the fieldsets
        - As a result, the fields now appear on the form
        """
        fieldsets = self.fieldsets.copy()
        # Get current Item
        url = request.build_absolute_uri("?")
        if url.endswith("/change/"):
            url = url[:-8]
            object_id = url.split("/")[-1]
            obj = self.model.objects.get(pk=object_id)
            # Create a field for each translation associated with our object
            fields = []
            translations = obj.get_translations_all_languages()
            for translation in translations:
                fieldname = create_translation_fieldname(translation)
                fields.append(fieldname)
            # Add a fieldset with our fields
            fieldsets.append(['TRANSLATIONS', {'fields': fields}])
        return fieldsets


# --------------------------------------------------------------------------------
# > Admins
# --------------------------------------------------------------------------------
@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    """Customizes the Field model in the administration interface"""

    # ----------------------------------------
    # List view
    # ----------------------------------------
    list_display = [
        "id",
        "get_app_name",
        "content_type",
        "name",
        "count_items",
        "count_missing_translations"
    ]
    list_display_links = [
        "id",
        "name",
    ]
    list_editable = []
    list_filter = [
        ApplicationFilter,
        ("content_type", admin.RelatedOnlyFieldListFilter)
    ]
    ordering = ["-id"]
    search_fields = ["name"]
    sortable_by = [
        "id",
        "content_type",
        "name",
    ]

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    autocomplete_fields = []
    readonly_fields = [
        "id",
        "count_items",
        "count_missing_translations",
    ]
    radio_fields = {}
    raw_id_fields = []
    fieldsets = [
        [
            "CORE INFORMATION", {
                "fields": ["id"],
            }
        ],
        [
            "DYNAMIC STATISTICS", {
                "fields": [
                    "count_items",
                    "count_missing_translations"
                ],
            }
        ],
        [
            "CONTENT", {
                "fields": [
                    "content_type",
                    "name"
                ],
            }
        ],
    ]

    # ----------------------------------------
    # Custom Methods
    # ----------------------------------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Allows us to override how Content Type are displayed in a dropdown"""
        if db_field.name == "content_type":
            types = [ContentType.objects.get_for_model(model).pk for model in translated_models]
            kwargs['queryset'] = ContentType.objects.filter(pk__in=types)
            return ContentTypeDropdown(**kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Customizes the Item model in the administration interface
    You should not create, delete, nor edit instances from the admin
    This table is entirely generated/updated through 'signals.py' and CASCADE relationships
    """

    # ----------------------------------------
    # List view
    # ----------------------------------------
    list_display = [
        "id",
        "field",
        "object_id",
        "count_missing_translations"
    ]
    list_display_links = None
    list_editable = []
    list_filter = [
        ApplicationFilter,
        ("content_type", admin.RelatedOnlyFieldListFilter),
        "field"
    ]
    ordering = ["-id"]
    search_fields = ["object_id"]
    sortable_by = [
        "id",
        "field",
        "object_id",
    ]

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    autocomplete_fields = []
    readonly_fields = [  # All fields are read-only, so no edit possible
        "id",
        "field",
        "object_id",
        "count_missing_translations",
    ]
    radio_fields = {}
    raw_id_fields = []
    fieldsets = [
        [
            "CORE INFORMATION", {
                "fields": [
                    "id",
                    "field",
                    "object_id",
                ],
            }
        ],
        [
            "DYNAMIC STATISTICS", {
                "fields": ["count_missing_translations"],
            }
        ],
    ]
    inlines = [TranslationInline]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Customizes the Language model in the administration interface"""

    # ----------------------------------------
    # List view
    # ----------------------------------------
    list_display = [
        "id",
        "name",
        "iso2",
        "iso3",
        "django_language_name",
        "count_missing_translations"
    ]
    list_display_links = [
        "id",
        "name",
    ]
    list_editable = []
    list_filter = []
    ordering = ["-id"]
    search_fields = [
        "name",
        "iso2",
        "iso3"
        "django_language_name",
    ]
    sortable_by = [
        "id",
        "name",
        "iso2",
        "iso3",
        "django_language_name",
    ]

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    autocomplete_fields = []
    readonly_fields = [
        "id",
        "count_missing_translations",
    ]
    radio_fields = {}
    raw_id_fields = []
    fieldsets = [
        [
            "CORE INFORMATION", {
                "fields": ["id"],
            }
        ],
        [
            "DYNAMIC STATISTICS", {
                "fields": ["count_missing_translations"],
            }
        ],
        [
            "CONTENT", {
                "fields": [
                    "name",
                    "iso2",
                    "iso3",
                    "django_language_name",
                ],
            }
        ],
    ]


# Remove the comment below to access Item within the admin
# Only for debugging purposes
@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    """
    Customizes the Translation model in the administration interface
    Instances sould not be created nor deleted through the admin interface
    Creation and deletion are entirely handled by 'signals.py' and CASCADE relationships
    It is however possible to edit the "text" field through the detail view
    """

    # ----------------------------------------
    # List view
    # ----------------------------------------
    # actions = None
    list_display = [
        "id",
        "language",
        "item",
        "truncated_text"
    ]
    list_display_links = ["id", "truncated_text"]
    list_editable = []
    list_filter = [
        ApplicationFilter,
        ("item__content_type", admin.RelatedOnlyFieldListFilter),
        "item__field",
        "item",
        "language",
    ]
    ordering = ["-id"]
    search_fields = ["truncated_text"]
    sortable_by = [
        "id",
        "language",
        "item",
    ]

    # ----------------------------------------
    # Detail view
    # ----------------------------------------
    autocomplete_fields = []
    readonly_fields = [
        "id",
        "language",
        "item",
    ]
    radio_fields = {}
    raw_id_fields = []
    fieldsets = [
        [
            "CORE INFORMATION", {
                "fields": [
                    "id",
                    "language",
                    "item",
                ],
            }
        ],
        [
            "CONTENT", {
                "fields": ["text"],
            }
        ],
    ]
