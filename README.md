

# Green Stormwater Infrastructure (GSI) Cost Tool (gsicosttool)

gsicosttool is the _City of Raleigh NC GSI_ Cost Tool_. It is built with [Python][0] using the [Django Web Framework][1].

This project has the following basic apps:

* Cost Items - each structure has 1 or more Cost Items
* Structures - each scenario has 0 or more structures
* Scenario - users build scenarios that they can then compare with other scenarios
* Project - user creates projects, and then (multiple) scenarios for each project
* Profile - user profile manager
* User - user manager
* GSI - Green Stormwater Infrastructure

## Installation

### Quick start

To set up a development environment quickly, first install Python 3. It
comes with virtualenv built-in. So create a virtual env by:

    1. `$ python3 -m venv gsicosttool`
    2. `$ . gsicosttool/bin/activate`

Install all dependencies:

    pip install -r requirements.txt

Run migrations:

    python manage.py migrate

### Detailed instructions

Take a look at the docs for more information. TBD

[0]: https://www.python.org/
[1]: https://www.djangoproject.com/
