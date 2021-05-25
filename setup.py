"""Setup file for the PyPi packaging"""

# Third-party
from setuptools import find_packages, setup

# --------------------------------------------------------------------------------
# > Variables
# --------------------------------------------------------------------------------
VERSION = "1.1.4"
packages = find_packages()
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
setup(
    # General
    name='django_database_translation',
    version=VERSION,
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
    download_url=f'https://github.com/Jordan-Kowal/django_database_translation/archive/{VERSION}.tar.gz',
    # Packages
    packages=packages,
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
