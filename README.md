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
- A few class extenders/templates:
  - `TranslatedField` which is a Field that will be used for any field that must be translated
  - `TranslatedModel` to extend any model that has at least one `TranslatedField`
  - `TranslatedAdmin` to extend any admin whose model uses `TranslatedModel`
- A few tools for language selection:
  - `LanguageSelection`, a form that can be used in the frontend to pick a language
  - `update_user_language`, a function that updates the user language for both django and our app
- A few tools for getting translations
  - `all_instances_as_translated_dict`, returns all given instances as a dict, with all of their translatable-fields translated
  - `get_translation_from_item`, returns a translated value for a specific field
  - `instance_as_translated_dict`, returns an instance as a dict with all of its translatable-fields translated

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

Once you're all done, run the `makemigrations` and `migrate` commands to update your own database with your new changes.

### **3. Updating your admins**
Now that our models have been updated, we can update their admins. Note that you must only update the admins of models that have been extended with `TranslatedModel`.

Simply extend your admin using the `TranslatedAdmin` class:

```python
from django_database_translation.admin import TranslatedAdmin

class ProjectAdmin(TranslatedAdmin):  # <-- Extended class
    # Your code, no changes here
```

Now you will be able to edit translations directly from your admins.

### **4. Manually fills Language and Field in the admin**
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

### **5. Translate your entries**
Now that everything is setup, you can go in your admin and go in any of your database entry. If it is a model that uses `TranslatedModel` and its admin is `TranslatedAdmin`, you'll be able to see the translations directly in its admin. Go ahead and translate anything that must be translated.

### **6. Displaying translations**
There are going to be two cases for handling your translations. Whether you are using django views and rendering templates, or using AJAX views and pushing JSON data, your translation process is going to be fairly similar. You can use either of the following 3 functions from `django_database_translation.utils`:

**1)** If you ever need to get the current Language instance associated with your user, you can use `get_language_from_session(request)` (which returns the Language instance).

**2)** For translating ONE instance, use `instance_as_translated_dict(request, instance, depth=True, language=None)`, where:
- `request` is a HttpRequest item from Django
- `instance` is your model instance
- `depth` is a bool
- `language` is the current Language instance. If not provided, the function will automatically call `get_language_from_session`

It will return your instance as a dictionnary, with all of its fields/values using the following logic:
- Any `TranslatedField` will be translated
- Any `ForeignKey` field will either contains the ID or a sub-dictionnary (based on `depth`)
- Any `ImageField` will be turned into a subdict with its `path`, `url`, and `name`
- Any other field will simply have its original value.

Using `depth`, it will also apply the function to any foreign key that is found. So if you have a `Project` model with a foreign key to a `Category` model, you will still be able to do `project.category.name` in your templating system.

**3)** `all_instances_as_translated_dict(request, instances, depth=True, language=None)` is the same as `instance_as_translated_dict` except that:
- It takes a ITERABLE of instances instead of 1 instance
- It returns a LIST of dicts, one for each instance

It is basically a shortcut to apply `instance_as_translated_dict` to several instances.


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
