# Django Database Translation

## **Description**
Natively, Django only handles hardcoded text translation and cannot translate your database. This package aims to assist you in translating the entries of your database. It is fairly easy to setup and use, as demonstrated below.

The three main actions of the program are:
- Automatically generates database entries for any field that must be translated
- Allows you to access the translations directly from your model's admin
- Provides a custom tag for translating in HTML

**Please note, this does not TRANSLATE for you. It creates the entry in the database for your translation, which you have to fill**. Here's how it works in practice:

- I have registered 3 languages: French, English, Italian
- I have registered the "Project" model and said it must be translated
- I have registered 2 fields within the Project model, "name" and "description", as field that will require translations
- Whenever I create a new project, 6 new translation entries will be create: "name" in 3 languages, and "description" in 3 languages.
- If I go in my "Project" admin, I will be able to directly edit those 6 translations
- The translations can then be called in templating using our custom tag

## **What it contains**
Here's a quick recap of what this package contains:

- 4 new database tables:
  - `Field` (ddt_fields)
  - `Item` (ddt_items)
  - `Language` (ddt_languages)
  - `Translation` (ddt_translations)
- A few class extenders:
  - `TranslatedAdmin` to extend your admins
  - `TranslatedModel` to extend your models (also provides many useful methods)
- Some utility:
  - `LanguageSelection`, a form that can be used in the frontend to pick a language
  - `update_user_language`, a function that updates the user language for both django and our app
  - `get_translation_from_item`, useful if you need to translate an item BEFORE sending it as JSON

It contains other elements, but this is what you will be using 99% of the time.

## **Basic setup and usage**

### **1. Installation**
First, we must install the package:

- Install the package with `pip install django-database-translation`
- In `settings.py`, in your `INSTALLED_APPS`, add `"django_database_translation"` (note that we are using **underscores** this time)
- Then run the `python manage.py migrate` command to create the 4 new tables

### **2. Updating your models**
The point here is to "flag" which models have fields that must be translated. As a result, we will **extend** the models, and **change** the fields:

- Extend a model using `TranslatedModel` for any model that contains TranslatedFields
- Change any field that will be translated to a `TranslatedField` (it is a ForeignKey to our Item model)

Here's an example of code:

```python
from datetime import datetime
from django.db import models
from django_database_translation.fields import TranslatedField
from django_database_translation.models import TranslatedModel

class Project(TranslatedModel):  # <-- Extended class
    title = TranslatedField(  # <-- Field changed
        related_name="portfolio_project_title",
        verbose_name="Title"
    )
    description = TranslatedField(  # <-- Field changed
        related_name="portfolio_project_description",
        verbose_name="Description"
    )
    date_posted = models.DateField(
        db_index=True,
        default=datetime.now,
        help_text="Date displayed on the frontend",
        null=False,
        verbose_name="Posted on",
    )
    image = models.ImageField(
        help_text="Must be a square. Will be automatically resized to 200x200.",
        null=False,
        upload_to="portfolio/projects/",
    )
```

### **3. Updating your admins**
Now that our models have been updated, we can update their admins. Note that you must only update the admins of models that have been extended with `TranslatedModel`.

Simply extend your admin using the `TranslatedAdmin` class:

```python
from django_database_translation.admin import TranslatedAdmin

class ProjectAdmin(TranslatedAdmin):  # <-- Extended class
    # Your code, no changes here
```

Now you will be able to edit translations directly from your admins.

### **4. Setting up the database**
Now we need to manually create a few entries in both our `Language` and `Field` models. Do not worry about `Item` and `Translation`, their content will be generated automatically.

#### **--> Language**
In this table, simply create all the languages available on your website. Make sure that the `django_language_name` matches an entry in `LANGUAGES` from `settings.py`.

```python
# If settings.py is like this:
LANGUAGES = (
    ("fr-fr", "Français"),
    ("en-us", "English"),
)
# Make sure your "django_language_name" is either "fr-fr" or "en-us"
```

#### **--> Field**
Here you must simply register all the fields you've changed to `TranslatedField`. Make sure their name matches the actual name of the field.

#### **--> Sidenote**
If you already had database entries in your models, you'll notice that the `Translation` model already has a bunch of entry. Technically, an entry has been created for each of your model entry, in each language, and for each field.

### **5. Translate your entries**
Now that everthing is setup, you can go in your admin and go in any of your database entry. If it is a model that uses `TranslatedModel` and its admin is `TranslatedAdmin`, you'll be able to see the translations directly in its admin. Go ahead and translate anything that must be translated.

### **6. Displaying translations**
There are two ways of displaying translations for your users:
- If you're using a templating system (HTML), then you can simply load our custom tag `{% load ddt_tags %}` and then use `{% db_trans item %}` where "item" is your `TranslatedField`
- However, if you're using AJAX/JSON, you need to handle the translation beforehand. To do so, you can use the `get_translation_from_item` function from `django_database_translation.utils`

Here's the code of the function:

```python
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
```

## **Addtionnal information**

### **Model.objects.bulk_create()**
If a model is extended using `TranslatedModel`, it will not be able to use its `.bulk_create()` method. We are forced deactivate it as our program uses **signals** to work, and `.bulk_create()` does not trigger signals.

### **Choosing a language**

As you've seen, Django uses `LANGUAGES` in the settings to figure out which language you have. But our app uses the `Language` database/model. To make it easier, we've created:
- A form that allows user to pick a language in the frontend
- A function that updates both Django and our app "current language"

If you wish to use it:
- Form: `from django_database_translation.forms import LanguageSelection`
- Function : `from django_database_translation.utils import update_user_language`
- The function takes the "request" and the language ID as argument. Call it when the form is valid.

Here's the definition:

```python
from django.utils.translation import activate, LANGUAGE_SESSION_KEY

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
```
