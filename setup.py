import os
import re

from setuptools import find_namespace_packages, setup

name = 'drf-spectacular-jsonapi'
package = 'drf_spectacular_jsonapi'
description = 'open api 3 schema generator for drf-json-api package based on drf-spectacular package.'
url = 'https://github.com/jokiefer/drf-spectecular-json-api'
author = 'Jonas Kiefer'
author_email = 'jonas.kiefer@live.com'
license = 'BSD'


with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements/base.txt') as fh:
    requirements = [r for r in fh.read().split('\n') if not r.startswith('#')]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]",
                     init_py, re.MULTILINE).group(1)


version = get_version(package)

setup(
    name=name,
    version=version,
    url=url,
    license=license,
    description=description,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author=author,
    author_email=author_email,
    packages=[p for p in find_namespace_packages(
        exclude=('tests*',)) if p.startswith(package)],
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Documentation',
        'Topic :: Software Development :: Code Generators',
    ],
    python_requires='>=3.7',
)
