import os
import os.path
from setuptools import setup

def read(fname):
    if os.path.exists(fname):
    	return open(os.path.join(os.path.dirname(__file__), fname)).read()
    else:
        return ''

setup(
    name = "pyad",
    version = "0.5.15",
    author = "Zakir Durumeric",
    author_email = "zakird@gmail.com",
    maintainer = "Zakir Durumeric",
    maintainer_email = "zakird@gmail.com",
    download_url = "https://github.com/jcarswell/pyad/",
    description = "An Object-Oriented Active Directory management framework built on ADSI",
    license = "Apache License, Version 2.0",
    keywords = "python microsoft windows active directory AD adsi",
    python_requires='>=3.6',
    packages=[
        'pyad'
    ],
    long_description = read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP"
    ],
    install_requires=[
        'setuptools',
        'pywin32'
    ]
)
