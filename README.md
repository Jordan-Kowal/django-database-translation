# Django Database Translation

## **DESCRIPTION**
Natively, Django only handles hardcoded text translation. This package aims to assist you in translating the entries of your database. It is fairly easy to setup and use, as demonstrated below.

The three main actions of the program are:
- Automatically generates database entries for any field that must be translated
- Allows you to access the translations directly from your model's admin
- Easily translate your instances before pushing them in your template/context/json

**Please note, this does not TRANSLATE for you**. It creates the entries in the database for your translations, which you have to fill. Here's how it works in practice:

- I have registered 3 languages: French, English, Italian
- I have registered the "Project" model and said it must be translated
- I have registered 2 fields within the Project model, "name" and "description", as field that will require translations
- Whenever I create a new project, 6 new translation entries will be create: "name" in 3 languages, and "description" in 3 languages.
- If I go in my "Project" admin, I will be able to directly edit those 6 translations
- To use translations in the frontend, simply translate your object using our utils functions before pushing them in your context/template/JSON

**Note that this package works RETROACTIVELY**. Translation entries will be generated for all existing instances when deploying this app

## **WHAT IT CONTAINS**
Here's a quick recap of what this package contains:

- 4 new database tables:
  - `Field` (ddt_fields)
  - `Item` (ddt_items)
  - `Language` (ddt_languages)
  - `Translation` (ddt_translations)
- A few class extenders/templates:
  - `TranslatedField` which is a Field that will be used for any field that must be translated
  - `TranslatedModel` to extend any model that has at least one `TranslatedField`
  - `TranslatedAdmin` to extend any admin whose model inherits from `TranslatedModel`
- A few tools for language selection:
  - `LanguageSelection`, a form that can be used in the frontend to pick a language
  - `update_user_language`, a function that updates the user language for both django and our app
- A few tools for getting translations
  - `all_instances_as_translated_dict`: Applies 'instance_as_translated_dict' to the iterable of instances
  - `get_language_from_session`: Returns the Language instance used by our user, or "False" if none is found
  - `instance_as_translated_dict`: Returns a model instance into a dict containing all of its fields

It contains other elements, but this is what you will be using 99% of the time.

## **SETUP**

### **1. Installation**
First, we must install the package:

- Install the package with `pip install django-database-translation`
- In `settings.py`, in your `INSTALLED_APPS`, add `"django_database_translation"` (note that we are using **underscores** this time)
- Then run the `python manage.py makemigrations django_database_translation` command
- Then run the `python manage.py migrate django_database_translation` command to create the 4 new tables

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
```

Once you're all done, run the `makemigrations` and `migrate` commands to update your own database with your new changes.

### **3. Updating your admins**
Now that our models have been updated, we can update their admins. Note that you must only update the admins of models that have been extended with `TranslatedModel`.

Simply extend your admin using the `TranslatedAdmin` class:

```python
from django.contrib import admin
from django_database_translation.admin import TranslatedAdmin
from .models import Project

@admin.register(Project)
class ProjectAdmin(TranslatedAdmin):  # <-- Extended class
    # Your code here
```

Now you will be able to edit translations directly from your admins.

### **4. Manually fill Language and Field in the admin**
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

## **SHOWING TRANSLATIONS**
### **1. Updating the user language**
Since you're translating your database, you are probably also translating all of your HTML/Python texts, meaning you are using django built-in `i18n` and `translation` modules (gettext, etc.). To make life easier, we created the `update_user_language` function. It will update both django and our module current language for this user. Here's how it works:
- Have a form where the user can choose its language
- Make sure to use our `Language` entries as available choices
- When the users POST the form (and `form.is_valid()`), call this function with the request object and the chosen Language id.
- The session will be updated using your Language `instance.django_language_name`

Example:

```python
# We call this when the form is valid
def form_valid(self, form):
    # (...)
    language_id = form.cleaned_data['language_id']
    update_user_language(self.request, language_id=language_id)
    # (...)
```

To gain some time, you can use the `LanguageSelection` form as your form for the language selection. It is a form with:
- Only one field: the language id
- This field is a ChoiceField
- The available choices are the Language entries
- Uses either a RADIO for the form rendering

Here is a full example of a view that is accessible everywhere on a website:

```python
from django.shortcuts import redirecte
from django.views.generic import View
from django_database_translation.forms import LanguageSelection
from django_database_translation.utils import update_user_language

class UpdateLanguageSelection(View):
    """
    View only reachable through POST that allows you to select your language
    A form sending a POST request to this view is available on every page:
    - The form is in our context_processor
    - The main.html renders the form
    """

    # ----------------------------------------
    # Settings
    # ----------------------------------------
    form_class = LanguageSelection

    # ----------------------------------------
    # Core Methods
    # ----------------------------------------
    def get(self, request, *args, **kwargs):
        """
        Defines how to handle a GET request.
        In this case, they are not allowed and will be redirected
        """
        return self.redirect_to_current_page()

    def post(self, request, *args, **kwargs):
        """
        Defines how to handle a POST request.
        It will update the user session language.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            response = self.form_valid(form)
        else:
            response = self.form_invalid(form)
        return response

    # ----------------------------------------
    # Helper Methods
    # ----------------------------------------
    def form_invalid(self, form):
        """Simply redirects to the current page"""
        return self.redirect_to_current_page()

    def form_valid(self, form):
        """
        Called if the form is valid and data has been cleaned
        Updates the user current language then redirects him to the current page
        """
        language_id = form.cleaned_data['language_id']
        update_user_language(self.request, language_id=language_id)
        return self.redirect_to_current_page()

    def redirect_to_current_page(self):
        """Reloads the current page or redirects you to the homepage"""
        current_page = self.request.META['HTTP_REFERER']
        if not current_page:
            current_page = "home"
        return redirect(current_page)
```

### **2. Displaying the translations**
The last thing left to do is to display the translations. Our instances have keys to `Item`, which then have keys to `Translation`. To get the translations, we need to pair an `Item` with a `Language`.

First off, get the language using our `get_language_from_session`. This will return the user's current `Language` instance.

Then, before sending your object(s) in the template/context/JSON, translate them using `instance_as_translated_dict` or `all_instances_as_translated_dict`. Your instances will become dictionaries, and your `Item` keys will automatically be replaced with your translated text. Those two functions can either be given a `language`, or guess it themselves by using the `request` arg. If you're going to make several translations in the same functions, get the `language` first. This will avoid making a new database request each time to guess the language.

You'll find below an example with a Project model and a Job model, where we:
- Translate projects by overriding the `get_queryset` method
- Get and translate jobs by overriding the `get_context_data` method
- In one case, we get the language THEN translate
- In the other case, we simply push the request, and the function will guess the language
- (This is done only as a showcase)

```python
from django.utils.translation import gettext
from django.views.generic import ListView
from django_database_translation.utils import all_instances_as_translated_dict, get_language_from_session
from .models import Job, Project

class ProjectList(ListView):
    # ----------------------------------------
    # Settings
    # ----------------------------------------
    model = Project
    template_name = "portfolio/pages/portfolio.html"
    context_object_name = "projects"
    ordering = ["-date_posted"]

    # ----------------------------------------
    # Overridden Methods
    # ----------------------------------------
    def get_context_data(self, **kwargs):
        """
        The method was overridden to do the following:
            - Add the 'meta_title' to the context
            - Add the active 'jobs' to the context and translating their data
        """
        # Get the Job instances and translate them using the request
        all_jobs = Job.objects.all()
        jobs = filter(lambda x: x.count_projects(), all_jobs)
        jobs = all_instances_as_translated_dict(jobs, depth=True, request=self.request)
        # Update the context
        context = super(ProjectList, self).get_context_data(**kwargs)
        context.update({
            "meta_title": gettext("portoflio_meta_title"),
            "jobs": jobs,
        })
        return context

    def get_queryset(self):
        # We get the language first, then use it for our translation
        language = get_language_from_session(self.request)
        query = Project.objects.filter(active=True)
        query = all_instances_as_translated_dict(query, depth=True, language=language)
        return query
```

## **ADDTIONAL INFORMATION**

### **Translate with depth**
In the example above, with Project and Job, you'll notice we translated them using `depth=True`. It means that if our `TranslatedModel` has foreign keys to other models, those models will also be translated. In this case, if `Project` has a FK to `Job`, we can acces `Job.name` by:
- Using `project["job"]["name"]` in python (*fields are now keys, not attributes*)
- Using `project.job.name` in html/templates (*same syntax as normal instances*)

### **How to translate a form that uses the database**
Sometimes, your form will have `ChoiceField` generated from your database. If the table used is a `TranslatedModel`, you'll need to get the right language for your form. Since a form doesn't have access to the `request` object, you need to pass either the `language` or the `request` in your form init method. Here's an example on how to do it:

```python
# In your FORM, override the __init__ method like so:
def __init__(self, *args, **kwargs):
    self.language = kwargs.pop("language", None)
    super(YourFormName, self).__init__(*args, **kwargs)

# In your VIEW, call the form like so:
def function_inside_your_view(self):
    # (...)
    request = self.request
    language = get_language_from_session(request)
    form = self.form_class(request.GET, language=language) # (or .POST, etc.)
    # (...)
```

### **Model.objects.bulk_create()**
If a model inherits from `TranslatedModel`, it will not be able to use its `.bulk_create()` method. We are forced deactivate it as our program uses **signals** to work, and `.bulk_create()` does not trigger signals.

### **More info on the utils functions**
Here's a closer look on the utils functions:

```python
# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
from django.db import models
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.utils.translation import activate, LANGUAGE_SESSION_KEY
from .models import Item, Language, Translation


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def all_instances_as_translated_dict(instances, depth=True, language=None, request=None):
    """
    Description:
        Applies 'instance_as_translated_dict' to the iterable of instances
        Returns a list of dicts which contains the fields of all your instances
        Check the 'instance_as_translated_dict' for more info
    Args:
        instances (iterable): An iterable of your model instances
        depth (bool, optional): Determines if FK will also be transformed into dicts. Defaults to True.
        language (Language, optional): A Language instance from this app. Defaults to None.
        request (HttpRequest, option): HttpRequest from Django. Defaults to None.
    Returns:
        list: A list of dicts, where each dict contains the fields/values of the initial instances
    """
    # Checking arguments
    if language is None and request is None:
        raise TypeError("You must provide either 'language' or 'request'")
    # Get the language from the session
    if language is None:
        language = get_language_from_session(request)
    # Loop over instances
    results = []
    for instance in instances:
        result = instance_as_translated_dict(instance, depth=depth, language=language)
        results.append(result)
    return results


def get_language_from_session(request):
    """
    Description:
        Returns the Language instance used by our user, or "False" if none is found
    Args:
        request (HttpRequest): HttpRequest from Django
    Returns:
        Language: The currently used language from our app's Language model
    """
    language_name = request.session.get(LANGUAGE_SESSION_KEY, False)
    if language_name:
        try:
            language = Language.objects.get(django_language_name=language_name)
            return language
        except Language.DoesNotExist:
            return False
    return False


def instance_as_translated_dict(instance, depth=True, language=None, request=None):
    """
    Description:
        Returns a model instance into a dict containing all of its fields
        Language can be given as an argument, or guess through the user of "request"
        With "depth" set to True, ForeignKey will also be transformed into sub-dict
        Files and images are replaced by a subdict with 'path', 'url', and 'name' keys
        Meaning you will be able to manipulate the dict in an HTML template much like an instance
    Args:
        instance (Model): An instance from any of your models
        depth (bool, optional): Determines if FK will also be transformed into dicts. Defaults to True.
        language (Language, optional): A Language instance from this app. Defaults to None.
        request (HttpRequest, option): HttpRequest from Django. Defaults to None.
    Returns:
        dict: A dict with all of the instance's fields and values
    """
    # Checking arguments
    if language is None and request is None:
        raise TypeError("You must provide either 'language' or 'request'")
    # Get the language from the session
    if language is None:
        language = get_language_from_session(request)
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
                    new_value = instance_as_translated_dict(value, depth=True, language=language)
                else:
                    new_value = value
            # Case 3:
            elif value_type in {ImageFieldFile, FieldFile}:
                if value:
                    new_value = {
                        "name": getattr(value, "name", ""),
                        "url": getattr(value, "url", ""),
                        "path": getattr(value, "path", ""),
                    }
                else:
                    new_value = ""
            # Case 4: Keep the value as it is
            else:
                new_value = value
            translated_dict[field.name] = new_value
    return translated_dict


def update_user_language(request, language=None, language_id=None):
    """
    Description:
        Updates the user current language following Django guildelines
        This will allow for both "Django" frontend translations and "our app" database translation
        The new language must be passed either through a Language instance or an ID
    Args:
        request (HttpRequest): Request object from Django, used to get to the session
        language (Language, optional): A Language instance from this app. Defaults to None.
        language_id (id, optional): ID of the language in our database. Defaults to None.
    """
    # Checking arguments
    if language is None and language_id is None:
        raise TypeError("You must provide either 'language' or 'language_id'")
    # Get the language from the session
    if language is None:
        language = Language.objects.get(id=language_id)
    # Update the user's language
    activate(language.django_language_name)
    request.session[LANGUAGE_SESSION_KEY] = language.django_language_name

```
