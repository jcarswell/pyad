Introduction
============

pyad is a Python library designed to provide a simple, Pythonic interface to Active Directory
through ADSI on the Windows platform. Complete documentation can be found at
http://zakird.github.io/pyad/. Code is maintained at https://github.com/jcarswell/pyad. The 
library can be downloaded from PyPI at https://github.com/jcarswell/pyad.

Breaking Changes from upstream
==============================

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
============

pyad requires pywin32, available at https://github.com/mhammond/pywin32.

Alternatively,

|
|    pip install pywin32
|

works as well.


Connecting to Active Directory
==============================

By default, pyad will connect to the Active Directory domain to which the machine is
 joined (rootDSE):

.. code-block:: python

    from pyad import ADUser
    user = ADUser.from_cn("myuser")


It is also possible to pass in options when connecting to a specific object. This will not 
set the library defaults, but these settings will be used from any objects you derive from 
it (e.g. if you request group membership of a user) Example::

.. code-block:: python

   from pyad import ADUser
   user = ADUser.from_cn("myuser", options=dict(ldap_server="dc1.domain.com"))


Basic Object Manipulation
=========================

There are first order Python classes for different types of objects in Active Directory. For 
example, ADUser represents user objects and ADGroup represents groups. All objects subclass 
ADObject. Most methods are defined in ADObject, but subclasses generally provide additional 
helper methods (e.g. ADUser has `set_password` and ADGroup has `add_member`).

It is possible to connect to an object by distinguished name, CN, UPN, and GUID if you already 
know the type of object. Examples:

.. code-block:: python

    from pyad import ADUser
    user1 = ADUser.from_dn("cn=myuser, ou=staff, dc=domain, dc=com")
    user2 = ADUser.from_cn("myuser")
    user3 = ADUser.from_guid("XXX-XXX-XXX")


It is also possible to use the pyad factory with an arbitrary Active Directory object and 
to receive an appropriately classed Python object:

.. code-block:: python

    import pyad
    user = pyad.from_cn("user1")
    computer = pyad.from_dn("cn=WS1,ou=Workstations,dc=domain,dc=com")
    group = pyad.from_guid("XXX-XXX-XXX")


Unlike the ADSI interface, pyad objects are intended to interact with 
one another. Instead of adding the DN of a user to the members attribute 
of a group to add the user, you instead add the user object to the group. 
For instance:

.. code-block:: python

    user1 = ADUser.from_cn("myuser1")
    user2 = ADUser.from_cn("myuser2")
    group = ADGroup.from_dn("staff")

    group.add_members([user1, user2])

    for user in group.get_members():
        print user1.description


However, it is still possible to directly manipulate any attribute outside of the helper 
methods that pyad provides:

.. code-block:: python

    user1 = ADUser.from_cn("myuser1")
    user.set_attribute("description", "new description")
    user.append_to_attribute("member", "cn=myuser1, ou=staff, dc=domain, dc=com")


More details on how to manipulate the objects you find to is found in the next section.


Creating, Moving, and Deleting Objects
======================================

There are two methodologies for creating and deleting objects. In both cases, you must first 
bind to the parent container. When creating a new object, several attributes are required, but 
other additional attributes can be specified with the `optional_attributes` parameter. Example 1:

.. code-block:: python

    ou = ADContainer.from_dn("ou=workstations, dc=domain, dc=com")

    # create a new group without any optional attributes
    new_computer = ADComputer.create("WS-489", ou)

    # create a new group with additional attributes
    new_group = ADGroup.create("IT-STAFF", security_enabled=True, scope='UNIVERSAL',
                    optional_attributes = {"description":"all IT staff in our company"})

It is also possible to create new objects from the parent container:

.. code-block:: python

    ou = ADContainer.from_dn("ou=workstations, dc=domain, dc=com")
    computer = ou.create_computer("WS-490")

Once objects are created, they can be moved:

.. code-block:: python

    computer = ADComputer.from_cn("WS-500")
    computer.move(ADContainer.from_dn("ou=workstations, ou=HR, dc=company, dc=com"))

or renamed::

.. code-block:: python

    computer = ADComputer.from_cn("WS-500")
    computer.rename("WS-501")

Objects can be removed by calling delete()::

.. code-block:: python

    ADComputer.from_cn("WS-500").delete()


Searching Active Directory
==========================

As shown above, objects can be directly connected to via CN, DN, GUID, or UPN. However, 
objects can also be searched for through the ADQuery interface (and in the background, this 
is how objects are actually found when you connect by CN). It is important to note that the 
ADQuery interface will not provide you with pyad objects, but instead with only the attributes 
for which you queried, for performance reasons. Example:

.. code-block:: python

    from pyad import ADQuery
    q = ADQuery()

    q.execute_query(
        attributes = ["distinguishedName", "description"],
        where_clause = "objectClass = '*'",
        base_dn = "OU=users, DC=domain, DC=com"
    )

    for row in q.get_results():
        print row["distinguishedName"]


Testing
=======

To run unittest you will need to set the configuration to be specific to your environment. 
To do this you will need to edit config.py located in the tests folder.


License
=======

pyad is licensed under the Apache License, Version 2.0 (the "License"). You may obtain a copy 
of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the 
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. See the License for the specific language governing permissions 
and limitations under the License.
