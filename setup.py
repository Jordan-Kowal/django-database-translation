# coding: utf8


# --------------------------------------------------------------------------------
# > Imports
# --------------------------------------------------------------------------------
# Built-in
from setuptools import setup

# Third-party

# Local


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    # General
    name='django_database_translation',
    version='1.0.0',
    license='MIT',
    # Description
    description='Package to handle database translation in your Django apps',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Author
    author='Jordan Kowal',
    author_email='kowaljordan@gmail.com',
    # URLs
    url='https://github.com/Jordan-Kowal/django_database_translation',
    download_url='https://github.com/Jordan-Kowal/django_database_translation/archive/v1.0.0.tar.gz',
    # Packages
    packages=['django_database_translation'],
    install_requires=[],
    # Other info
    keywords=["django", "database", "db", "translation", "translate", "backend"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
