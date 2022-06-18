.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :align: center
    :target: https://github.com/psf/black
    :alt: code style: black

Introduction
------------

pyad is a Python library designed to provide a simple, Pythonic interface to Active Directory
through ADSI on the Windows platform. Complete documentation can be found at
http://jcarswell.github.io/pyad/. Code is maintained at https://github.com/jcarswell/pyad. The 
library can be downloaded from PyPI at https://github.com/jcarswell/pyad.

Breaking Changes from upstream
------------------------------

ADObject:

- _get_password_last_set - Act's like AD and returns 1970-01-01 if the date can't be parsed
- get_last_login - Act's like AD and returns 1970-01-01 if the date can't be parsed

Importing pyad directly exposes set_defaults, ADQuery, ADComputer, ADContainer, ADDomain,
ADGroup, ADUser, from_cn, from_dn, from_guid. Importing pyad.pyad no longer imports
the sub modules

Most ADObject update methods now take flush as an optional argument that defaults to True
to maintain compatibility with upstream code. For large updates it's recommended to set 
this to False until you are ready to write out the change, otherwise you may run into a 
back-off period in AD where all further changes will fail.

Requirements
------------

pyad requires pywin32, available at https://github.com/mhammond/pywin32.


Testing
-------

To run unittest you will need to set the configuration to be specific to your environment. 
To do this you will need to edit config.py located in the tests folder.


License
-------

pyad is licensed under the Apache License, Version 2.0 (the "License"). You may obtain a copy 
of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the 
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. See the License for the specific language governing permissions 
and limitations under the License.
