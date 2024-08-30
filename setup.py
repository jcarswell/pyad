import os
import os.path
from setuptools import setup


def read(fname):
    if os.path.exists(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    else:
        return ""


setup(
    name="python-win-ad",
    version="0.6.2",
    author="Zakir Durumeric",
    author_email="zakird@gmail.com",
    maintainer="Josh Carswell",
    maintainer_email="Josh.Carswell@thecarswells.ca",
    url="https://github.com/jcarswell/pyad/",
    description="An Object-Oriented Active Directory management framework built on ADSI",
    license="Apache License, Version 2.0",
    keywords="python microsoft windows active directory AD adsi",
    python_requires=">=3.6",
    obsoletes=["pyad"],
    packages=[
        "pyad",
    ],
    project_urls={
        "Documentation": "https://jcarswell.github.io/pyad/",
        "Issues": "https://github.com/jcarswell/pyad/issues/",
    },
    long_description=read("README.rst"),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=["setuptools", "pywin32"],
)
