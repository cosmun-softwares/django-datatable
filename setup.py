#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages


setup(
    name='django-datatable',
    version='0.3.4',
    author='cosmun softwares',
    author_email='contato@cosmunsoftwares.com.br',
    url='https://github.com/cosmunsoftwares/django-datatable',
    description='A simple Django app to origanize data in tabular form.',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['test*', 'example*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=["django==2.1.3"],
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
)
