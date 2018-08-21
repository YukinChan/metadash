#!/usr/bin/env python
# Pack it as a package for some rare case usage
# Be sure to install only in a virtualenv
# It is not supposed to be install as a common package at all

import glob
from setuptools import setup, find_packages
from manager import do_initialize


STATIC_INSTALLATION = [
    "alembic==0.9.1",
    "amqp==2.2.1",
    "aniso8601==1.2.0",
    "appdirs==1.4.3",
    "astroid==1.4.9",
    "billiard==3.5.0.3",
    "celery==4.1.0",
    "kombu==4.1.0",
    "dogpile.cache==0.6.3",
    "flake8==3.3.0",
    "Flask==0.12.1",
    "Flask-Migrate==2.0.3",
    "Flask-RESTful==0.3.5",
    "Flask-Script==2.0.5",
    "Flask-Session==0.3.1",
    "Flask-SQLAlchemy==2.2",
    "Flask-WTF==0.14.2",
    "kerberos==1.2.5",
    "ldap3==2.2.4",
    "pytz==2017.2",
    "redis==2.10.5",
    "requests==2.13.0",
    "SQLAlchemy==1.1.9",
    "coloredlogs==7.3.1",
    "Sphinx==1.7.1",
    "psycopg2-binary==2.7.4",
    "gunicorn==19.9.0",
]


def read_file(file_name):
    with open(file_name) as file:
        return file.read()


def find_all_requirements(develop=False):
    requirements = set(STATIC_INSTALLATION)
    if develop:
        requirements.update(read_file('requirements.dev.txt').splitlines())
    for filename in glob.glob('metadash/plugins/*/requirements.txt'):
        requirements.update(read_file(filename).splitlines())
        if develop:
            for filename in glob.glob('metadash/plugins/*/requirements.dev.txt'):
                requirements.update(read_file(filename).splitlines())
    return requirements


setup_params = dict(
    name='metadash',
    version='1.0',
    author='Kairui Song',
    author_email='ryncsn@gmail.com',
    license='GPLv3',
    python_requires='>=3.5',
    install_requires=find_all_requirements(),
    packages=find_packages(),
    package_data={
        '': [
            'config/*',
            'dist/*',
            'dist/*/*',
            'dist/*/*/*',
            'plugins/*/*.json',
        ],
    },
    scripts=[
        'bin/md-manager',
    ],
)


if __name__ == '__main__':
    do_initialize(dev=False, inst_py_dep=False, inst_node_dep=True, build_assert=True)
    setup(**setup_params)
