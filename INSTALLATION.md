

## Installation Notes for django (python) web application 'gsicosttool'

These notes are for installing the City of Raleigh NC GSI Cost Tool 'gsicosttool'
on a Windows 2016 Data Center server running an IIS webserver.

The gsicosttool is written using the python Django framework.

The instance described in these notes uses a Microsoft SQL Server database.  

## Folder Structure

I download all external (public) software that I'm going to install into  
    `C:\downloads`

I install all new software into folder so admin users can find out what I have installed  
    `C:\software`

I use a separate folder in inetpub to hold Django applications  
    `C:\inetpub\wwwdjango`

## Prerequisites

These are the packages required on the web server that are not covered in these notes

1. `git` https://git-scm.com/download/win
This is installed via a GUI
In Select Components you can uncheck all options

2. `IIS with FastCGI installed` https://docs.microsoft.com/en-us/iis/configuration/system.webserver/fastcgi/
	
## Install Python

Download Python 3.9.4 from https://www.python.org/downloads/ (27.6 MB)

Install python version 3.9.4 into folder  
    `C:\software\Python\Python39`

Python is installed via a GUI
You might have to run the installer as Admin
In Optional Features only check 'pip'
Use Advanced Options uncheck everything, but set the location to install.

Customize install location  
    `C:\software\Python\Python39`

Add python to System Environmental Variable 'Path'
Include 2 folders
    `C:\software\Python\Python39` and  
    `C:\software\Python\Python39\Scripts`
	
Install Python in folder
~~~~
user.name@MACHINENAME C:\software\Python\Python39
$ python --version
Python 3.9.4
~~~~
Upgrade Python Installation Program (pip)
~~~~a
user.name@MACHINENAME cd C:\software\Python\Python39
$ python -m pip install --upgrade pip
~~~~
Show version of pip
~~~~
user.name@MACHINENAME C:\software\Python\Python39
$ pip --version
pip 21.1 from c:\software\python\python39\lib\site-packages\pip (python 3.9)
~~~~
Install python package virtualenv
~~~~
user.name@MACHINENAME C:\software\Python\Python39
$ pip install virtualenv
Collecting virtualenv
  Downloading https://files.pythonhosted.org/packages/c5/97/00dd42a0fc41e9016b23f07ec7f657f636cb672fad9cf72b80f8f65c6a46/virtualenv-16.7.7-py2.py3-none-any.whl (3.4MB)
     |████████████████████████████████| 3.4MB 939kB/s
Installing collected packages: six, filelock, distlib, appdirs, virtualenv
Successfully installed appdirs-1.4.4 distlib-0.3.1 filelock-3.0.12 six-1.15.0 virtualenv-20.4.4
~~~~


## Download a copy of the application from github
~~~~
user.name@MACHINENAME C:\inetpub\wwwdjango
# git clone https://github.com/JamesBisese/gsicosttool.git gsicosttool
Cloning into 'gsicosttool'...
remote: Enumerating objects: 508, done.
remote: Counting objects: 100% (508/508), done.
remote: Compressing objects: 100% (349/349), done.
Recremote: Total 508 (delta 150), reused 491 (delta 138), pack-reused 0

Receiving objects: 100% (508/508), 11.66 MiB | 22.36 MiB/s, done.
Resolving deltas: 100% (150/150), done.
Updating files: 100% (304/304), done.

user.name@MACHINENAME C:\inetpub\wwwdjango
# chdir gsicosttool

user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool
# dir
...
d-----        4/26/2021   8:07 AM                docs
d-----        4/26/2021   8:07 AM                logs
d-----        4/26/2021   8:07 AM                src
-a----        4/26/2021   8:07 AM            120 .gitignore
-a----        4/26/2021   8:07 AM          33826 INSTALLATION.md
-a----        4/26/2021   8:07 AM           1143 README.md
..
user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool
# cd src

user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# dir
...
d-----        4/26/2021   8:07 AM                accounts
d-----        4/26/2021   8:07 AM                authtools
d-----        4/26/2021   8:07 AM                gsicosttool
d-----        4/26/2021   8:07 AM                media
d-----        4/26/2021   8:07 AM                profiles
d-----        4/26/2021   8:07 AM                scenario
d-----        4/26/2021   8:07 AM                static
d-----        4/26/2021   8:07 AM                templates
d-----        4/26/2021   8:07 AM                users
-a----        4/26/2021   8:07 AM            459 manage.py
-a----        4/26/2021   8:07 AM           1043 requirements.txt
...
~~~~

## Create a virtualenv for the application

This python virtual environment is used to sandbox all changes just for this single application
~~~~
user.name@MACHINENAME C:\inetpub\wwwdjango
$ chdir C:\software\Python\virtualenvs

user.name@MACHINENAME C:\software\Python\virtualenvs                      
# virtualenv gsicosttool                                                        
created virtual environment CPython3.9.4.final.0-64 in 965ms
  creator CPython3Windows(dest=C:\software\Python\virtualenvs\gsidoc, clear=False, no_vcs_ignore=False, global=False)
  seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=C:\Users\james.bisese\AppData\Local\pypa\virtualenv)
    added seed packages: pip==21.3.1, setuptools==59.2.0, wheel==0.37.0
  activators BashActivator,BatchActivator,FishActivator,PowerShellActivator,PythonActivator,XonshActivator                                                                     
~~~~
Go into that folder and 'activate' the virtual environment.
  Note that the prompt changes to indicate that the virtual env is active
~~~~
user.name@MACHINENAME C:\software\Python\virtualenvs
# chdir gsicosttool\Scripts

user.name@MACHINENAME C:\software\Python\virtualenvs\gsicosttool\Scripts
# ./activate

(gsicosttool) user.name@MACHINENAME C:\software\Python\virtualenvs\gsicosttool\Scripts
#
~~~~
An alternative way to activate the virtual environment is to run this command from anywhere 

~~~~
user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src\scenario\management\commands
# C:\software\Python\virtualenvs\gsicosttool\Scripts\activate

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src\scenario\management\commands
# 
~~~~

and to deactivate the virtual environment

~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src\scenario\management\commands
# deactivate

user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src\scenario\management\commands
#
~~~


## Install all required python packages 

Using the virtual environment, all the packages will be installed on the virtual environment 
folder `C:\software\Python\virtualenvs\gsicosttool` and will not affect the system-wide python installation.

The application 'requirements.txt' file contains a list of all the external python packages needed  to run the django app

The GSI Cost Tool requirements file is in  
    `C:\inetpub\wwwdjango\gsicosttool\src\requirements.txt` 

NOTE: there are some issues around the packages used to connect to the database.  As of the latest version 
they seem to work fine as found in the requirements.txt file. 

___

Install all the rest of the required packages using the requirements file

NOTE: the output will vary a bit from this, since I repeated these commands during testing and so have 'caches' of the files
~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# pip install -r requirements.txt
Collecting asgiref==3.4.1
  Using cached asgiref-3.4.1-py3-none-any.whl (25 kB)
Collecting Babel==2.9.1
  Using cached Babel-2.9.1-py2.py3-none-any.whl (8.8 MB)
Collecting beautifulsoup4==4.10.0
  Using cached beautifulsoup4-4.10.0-py3-none-any.whl (97 kB)
Collecting defusedxml==0.7.1
  Using cached defusedxml-0.7.1-py2.py3-none-any.whl (25 kB)
Collecting Django==3.2.9
  Using cached Django-3.2.9-py3-none-any.whl (7.9 MB)
Collecting django-admin-sortable==2.2.4
  Using cached django_admin_sortable-2.2.4-py3-none-any.whl (115 kB)
Collecting django-appconf==1.0.5
  Using cached django_appconf-1.0.5-py3-none-any.whl (6.4 kB)
Collecting django-bootstrap-datepicker-plus==3.0.5
  Using cached django_bootstrap_datepicker_plus-3.0.5-py3-none-any.whl (12 kB)
Collecting django-bootstrap4==21.1
  Using cached django_bootstrap4-21.1-py3-none-any.whl (24 kB)
Collecting django-braces==1.15.0
  Using cached django_braces-1.15.0-py2.py3-none-any.whl (14 kB)
Collecting django-crispy-forms==1.13.0
  Using cached django_crispy_forms-1.13.0-py3-none-any.whl (122 kB)
Collecting django-debug-toolbar==3.2.2
  Using cached django_debug_toolbar-3.2.2-py3-none-any.whl (200 kB)
Collecting django-environ==0.8.1
  Using cached django_environ-0.8.1-py2.py3-none-any.whl (17 kB)
Collecting django-filter
  Using cached django_filter-21.1-py3-none-any.whl (81 kB)
Collecting django-intl-tel-input==0.3.1
  Using cached django_intl_tel_input-0.3.1-py2.py3-none-any.whl (15 kB)
Collecting django-intl-tel-input2==0.2.0
  Using cached django_intl_tel_input2-0.2.0-py3-none-any.whl
Collecting django-jquery==3.1.0
  Using cached django_jquery-3.1.0-py2.py3-none-any.whl (33 kB)
Collecting django-location-field==2.1.0
  Using cached django_location_field-2.1.0-py2.py3-none-any.whl (71 kB)
Collecting django-mathfilters==1.0.0
  Using cached django_mathfilters-1.0.0-py3-none-any.whl (5.9 kB)
Collecting django-money==2.1
  Using cached django_money-2.1-py3-none-any.whl (33 kB)
Collecting django-moneyfield==0.2.1
  Using cached django_moneyfield-0.2.1-py3-none-any.whl
Collecting django-multiselectfield==0.1.12
  Using cached django_multiselectfield-0.1.12-py3-none-any.whl (15 kB)
Collecting django-mssql-backend
  Using cached django_mssql_backend-2.8.1-py3-none-any.whl (52 kB)
Collecting django-select2==7.9.0
  Using cached django_select2-7.9.0-py2.py3-none-any.whl (14 kB)
Collecting django_settings_export==1.2.1
  Using cached django_settings_export-1.2.1-py3-none-any.whl
Collecting django-tables2==2.4.1
  Using cached django_tables2-2.4.1-py2.py3-none-any.whl (93 kB)
Collecting django-utils-six==2.0
  Using cached django_utils_six-2.0-py3-none-any.whl (10 kB)
Collecting django-widget-tweaks==1.4.9
  Using cached django_widget_tweaks-1.4.9-py2.py3-none-any.whl (8.7 kB)
Collecting djangorestframework==3.12.4
  Using cached djangorestframework-3.12.4-py3-none-any.whl (957 kB)
Collecting djangorestframework-datatables==0.6.0
  Using cached djangorestframework_datatables-0.6.0-py2.py3-none-any.whl (14 kB)
Collecting djangorestframework-filters
  Using cached djangorestframework_filters-0.11.1-py2.py3-none-any.whl (12 kB)
Collecting easy-thumbnails==2.8
  Using cached easy_thumbnails-2.8-py3-none-any.whl (74 kB)
Collecting et-xmlfile==1.1.0
  Using cached et_xmlfile-1.1.0-py3-none-any.whl (4.7 kB)
Collecting importlib-metadata==4.8.2
  Using cached importlib_metadata-4.8.2-py3-none-any.whl (17 kB)
Collecting jdcal==1.4.1
  Using cached jdcal-1.4.1-py2.py3-none-any.whl (9.5 kB)
Collecting MarkupPy==1.14
  Using cached MarkupPy-1.14-py3-none-any.whl
Collecting odfpy==1.4.1
  Using cached odfpy-1.4.1-py2.py3-none-any.whl
Collecting openpyxl==3.0.9
  Using cached openpyxl-3.0.9-py2.py3-none-any.whl (242 kB)
Collecting packaging
  Using cached packaging-21.3-py3-none-any.whl (40 kB)
Collecting Pillow==8.4.0
  Using cached Pillow-8.4.0-cp39-cp39-win_amd64.whl (3.2 MB)
Collecting pip-review==1.1.0
  Using cached pip_review-1.1.0-py3-none-any.whl (7.2 kB)
Collecting psycopg2==2.9.2
  Using cached psycopg2-2.9.2-cp39-cp39-win_amd64.whl (1.2 MB)
Collecting py-moneyed==1.2
  Using cached py_moneyed-1.2-py2.py3-none-any.whl (17 kB)
Collecting pyodbc==4.0.32
  Using cached pyodbc-4.0.32-cp39-cp39-win_amd64.whl (72 kB)
Collecting pyparsing
  Using cached pyparsing-3.0.6-py3-none-any.whl (97 kB)
Collecting pytz==2021.3
  Using cached pytz-2021.3-py2.py3-none-any.whl (503 kB)
Collecting PyYAML==6.0
  Using cached PyYAML-6.0-cp39-cp39-win_amd64.whl (151 kB)
Collecting six==1.16.0
  Using cached six-1.16.0-py2.py3-none-any.whl (11 kB)
Collecting soupsieve==2.3.1
  Using cached soupsieve-2.3.1-py3-none-any.whl (37 kB)
Collecting sqlparse==0.4.2
  Using cached sqlparse-0.4.2-py3-none-any.whl (42 kB)
Collecting tablib==3.1.0
  Using cached tablib-3.1.0-py3-none-any.whl (48 kB)
Collecting typing-extensions==4.0.0
  Using cached typing_extensions-4.0.0-py3-none-any.whl (22 kB)
Collecting unicodecsv==0.14.1
  Using cached unicodecsv-0.14.1-py3-none-any.whl
Collecting Werkzeug==2.0.2
  Using cached Werkzeug-2.0.2-py3-none-any.whl (288 kB)
Collecting wfastcgi==3.0.0
  Using cached wfastcgi-3.0.0-py2.py3-none-any.whl
Collecting xlrd==2.0.1
  Using cached xlrd-2.0.1-py2.py3-none-any.whl (96 kB)
Collecting XlsxWriter==3.0.2
  Using cached XlsxWriter-3.0.2-py3-none-any.whl (149 kB)
Collecting xlwt==1.3.0
  Using cached xlwt-1.3.0-py2.py3-none-any.whl (99 kB)
Collecting xmlrunner==1.7.7
  Using cached xmlrunner-1.7.7-py3-none-any.whl
Collecting zipp==3.6.0
  Using cached zipp-3.6.0-py3-none-any.whl (5.3 kB)
Requirement already satisfied: setuptools in c:\software\python\virtualenvs\gsidoc\lib\site-packages (from django-money==2.1->-r requirements.txt (line 20)) (59.2.0)
Collecting svglib
  Using cached svglib-1.1.0-py3-none-any.whl
Collecting reportlab
  Using cached reportlab-3.6.3-cp39-cp39-win_amd64.whl (2.3 MB)
Requirement already satisfied: pip in c:\software\python\virtualenvs\gsidoc\lib\site-packages (from pip-review==1.1.0->-r requirements.txt (line 42)) (21.3.1)
Collecting django-filter
  Using cached django_filter-1.1.0-py2.py3-none-any.whl (45 kB)
Collecting lxml
  Downloading lxml-4.7.1-cp39-cp39-win_amd64.whl (3.7 MB)
     |████████████████████████████████| 3.7 MB 364 kB/s
Collecting cssselect2>=0.2.0
  Using cached cssselect2-0.4.1-py3-none-any.whl (13 kB)
Collecting tinycss2>=0.6.0
  Downloading tinycss2-1.1.1-py3-none-any.whl (21 kB)
Collecting webencodings
  Using cached webencodings-0.5.1-py2.py3-none-any.whl (11 kB)
Installing collected packages: webencodings, tinycss2, sqlparse, pytz, Pillow, asgiref, soupsieve, reportlab, pyparsing, lxml, Django, cssselect2, Babel, zipp, svglib, six, pyodbc, py-moneyed, packaging, et-xmlfile, djangorestframework, django-filter, django-appconf, defusedxml, beautifulsoup4, xmlrunner, xlwt, XlsxWriter, xlrd, wfastcgi, Werkzeug, unicodecsv, typing-extensions, tablib, PyYAML, psycopg2, pip-review, openpyxl, odfpy, MarkupPy, jdcal, importlib-metadata, easy-thumbnails, djangorestframework-filters, djangorestframework-datatables, django-widget-tweaks, django-utils-six, django-tables2, django-settings-export, django-select2, django-multiselectfield, django-mssql-backend, django-moneyfield, django-money, django-mathfilters, django-location-field, django-jquery, django-intl-tel-input2, django-intl-tel-input, django-environ, django-debug-toolbar, django-crispy-forms, django-braces, django-bootstrap4, django-bootstrap-datepicker-plus, django-admin-sortable
Successfully installed Babel-2.9.1 Django-3.2.9 MarkupPy-1.14 Pillow-8.4.0 PyYAML-6.0 Werkzeug-2.0.2 XlsxWriter-3.0.2 asgiref-3.4.1 beautifulsoup4-4.10.0 cssselect2-0.4.1 defusedxml-0.7.1 django-admin-sortable-2.2.4 django-appconf-1.0.5 django-bootstrap-datepicker-plus-3.0.5 django-bootstrap4-21.1 django-braces-1.15.0 django-crispy-forms-1.13.0 django-debug-toolbar-3.2.2 django-environ-0.8.1 django-filter-1.1.0 django-intl-tel-input-0.3.1 django-intl-tel-input2-0.2.0 django-jquery-3.1.0 django-location-field-2.1.0 django-mathfilters-1.0.0 django-money-2.1 django-moneyfield-0.2.1 django-mssql-backend-2.8.1 django-multiselectfield-0.1.12 django-select2-7.9.0 django-settings-export-1.2.1 django-tables2-2.4.1 django-utils-six-2.0 django-widget-tweaks-1.4.9 djangorestframework-3.12.4 djangorestframework-datatables-0.6.0 djangorestframework-filters-0.11.1 easy-thumbnails-2.8 et-xmlfile-1.1.0 importlib-metadata-4.8.2 jdcal-1.4.1 lxml-4.7.1 odfpy-1.4.1 openpyxl-3.0.9 packaging-21.3 pip-review-1.1.0 psycopg2-2.9.2 py-moneyed-1.2 pyodbc-4.0.32 pyparsing-3.0.6 pytz-2021.3 reportlab-3.6.3 six-1.16.0 soupsieve-2.3.1 sqlparse-0.4.2 svglib-1.1.0 tablib-3.1.0 tinycss2-1.1.1 typing-extensions-4.0.0 unicodecsv-0.14.1 webencodings-0.5.1 wfastcgi-3.0.0 xlrd-2.0.1 xlwt-1.3.0 xmlrunner-1.7.7 zipp-3.6.0
                                                                   
                                                                               
~~~~

# Configure the Application

The web application software is now installed.  Now the application needs to be 
configured, and the backend database needs to be created and populated.

## Configure the application

The application is configured using a number of `settings` files.  The files
are all located in folder
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings`

Normally, you will not need to edit any of the settings `.py` files, and 
the only files that need to be edited are the `.env` files.  These are 
read into the other files.

For local development, copy file
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\local.development.sample.env` and rename it
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\local.development.env`

For production, copy file
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\local.production.sample.env` and rename it
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\local.production.env`

When the application is running using the django development server it uses the files
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\base.py`    
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\development.py` and 
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\local.development.env`

When the application is running using the django production server it uses the files
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\base.py`    
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\production.py` and 
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\local.production.env`
    


## Create the Database

Now the backend database needs to be created and all 
lookup data needs to be loaded from CSV text files into the database.

**NOTE:** *this documentation is for using SQL Server database,
it will vary a bit depending on the ODBMS used.*

The connection to the database is defined in two places -
    `C:\inetpub\wwwdjango\gsicosttool\gsicosttool\settings\local.development.env` and
    `C:\inetpub\wwwdjango\gsicosttool\gsicosttool\settings\local.production.env`    

~~~~
# Sample Django database settings for PostgreSQL (requires package psycopg2)
#		DATABASES = {
#			'default': {
#		       'ENGINE': 'django.db.backends.postgresql',
#		       'NAME': '{DATABASENAME}',
#		       'USER': '{USER}',
#		       'PASSWORD': '{PASSWORD}',
#		       'HOST': '127.0.0.1',
#		       'PORT': '{PORT}',
#		       'DATABASE_SCHEMA': 'pubic'
#			}
#		}
# PostgreSQL
DATABASE_URL=postgres://{USER}:{PASSWORD}@127.0.0.1:{PORT}/{DATABASENAME}

# Sample Django database settings for Microsoft SQL Server (requires package pyodbc)
#		DATABASES = {
#			'default': {
#				'ENGINE': 'sql_server.pyodbc',
#				'NAME': '{DATABASENAME}',
#				'USER': '{USER}',
#				'PASSWORD': '{PASSWORD}',
#				'HOST': '{MACHINE_NAME}',
#				'PORT': '',
#		        'OPTIONS': {
#		            'driver': 'ODBC Driver 13 for SQL Server',
#		        },
#			}
#		}
# SQL Server
# DATABASE_URL=mssql://{USER}:{PASSWORD}@{MACHINENAME}:{PORT}/{DATABASENAME}
~~~~

Once the database configurations are saved in the settings file, test to make sure the
connection works

~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
$ python manage.py check_db
Connecting to the database...
Database available!
~~~~

Now that the connection is tested, you can run the python django 
process to make migration scripts that automate the 
process of creating tables and related objects in the database.
~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py makemigrations scenario
Migrations for 'scenario':
  scenario\migrations\0001_initial.py
    - Create model ArealFeatures
    - Create model ConventionalStructures
    - Create model CostItem
    - Create model NonConventionalStructures
    - Create model Project
    - Create model Structures
    - Create model Scenario
    - Create model CostItemDefaultEquations
    - Create model CostItemDefaultCosts
    - Create model StructureCostItemUserCosts
    - Create model CostItemUserAssumptions
    - Create model StructureCostItemDefaultFactors

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py makemigrations authtools
Migrations for 'authtools':
  authtools\migrations\0001_initial.py
    - Create model User

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py makemigrations profiles
Migrations for 'profiles':
  profiles\migrations\0001_initial.py
    - Create model Profile

~~~~

Run the python django process to run the migration scripts 
and create tables and related objects in the database.

~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, authtools, contenttypes, easy_thumbnails, profiles, scenario, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying authtools.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying easy_thumbnails.0001_initial... OK
  Applying easy_thumbnails.0002_thumbnaildimensions... OK
  Applying profiles.0001_initial... OK
  Applying scenario.0001_initial... OK
  Applying sessions.0001_initial... OK

~~~~

## Populate the Database

There are 2 ways to populate the database that might be required. One way is to create and 
**populate from scratch**. The other is to **load data from another instance** of the GSI Cost Tool.
Both methods are described here.

### Populate from scratch

There are a number of lookup lists used to configure the application.

The data that is loaded into the database is all in folder  
    `C:\inetpub\wwwdjango\gsicosttool\src\scenario\static\scenario\data`

All the files are CSV (text files)

~~~~
user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# chdir scenario\static\scenario\data

user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src\scenario\static\scenario\data
# dir
...
10/28/2019  05:56 PM             6,061 CostItemDefaultCosts.csv
10/28/2019  05:56 PM             2,477 CostItemDefaultEquations.csv
10/28/2019  05:56 PM             2,288 CostItemDefaultFactors.csv
10/28/2019  05:56 PM             5,717 CostItems.csv
10/28/2019  05:56 PM             2,266 Structures.csv
...

~~~~

The command scripts are in folder  
    `C:\inetpub\wwwdjango\gsicosttool\src\scenario\management\commands`

The scripts have to be run in a particular order to deal with dependencies.

The output from the command scripts has been removed.
~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py load_Structures
...

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py load_CostItem
...

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py load_CostItemDefaultCosts

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py load_CostItemDefaultEquations

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py load_CostItemDefaultFactors
~~~~

There is an optional command to create a handfull of user accounts
that can be useful for testing and development.  These accounts can be added
using a single command.  You can look in the script used to create
users and see/set the passwords assigned to these testing accounts.  
**Note: this is a security hole that should be close.  The user names and passwords 
could/should be loaded from a non-git file.**

    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\management\commands\create_users.py`

The accounts should be removed once testing is completed.

~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py create_users
User "admin@tetratech.com" created
User "manager@tetratech.com" created
User "user1@tetratech.com" created
User "user2@tetratech.com" created
User "user3@tetratech.com" created

~~~~
___
### Load data from another instance

As an alternative, you can load the data from the testing/development shared website.
The data from that site has been exported using `dumpdata`

This command is run on the REMOTE computer (not the one where the app is being installed)
~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py dumpdata --indent 4 > gsicosttool.json

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# ls -l gsicosttool.json
-rw-rw-rw-  1 user.name 0 531553 2019-10-28 10:48 gsicosttool.json
~~~~

That file is then copied to the new machine and loaded using `loaddata`

~~~~
TODO: includes a bit of work to drop and reinstall 3 constraints
~~~~

___

## Run django `collectstatic` command

Now run a command to collect all the files that will be 
served from IIS as 'static' files (not django application).
Static files include images, javascript, and css.

~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
$ python manage.py collectstatic

You have requested to collect static files at the destination
location as specified in your settings:

    `C:\inetpub\wwwdjango\gsicosttool\src\static`

This will overwrite existing files!
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: yes

222 static files copied to 'C:\inetpub\wwwdjango\gsicosttool\src\static'.

~~~~

### Run the application using the django development server

The application is now setup.  

It can be run in a development mode, and viewed in a web browser
locally using this command.

~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src\scenario\management\commands
# chdir C:\inetpub\wwwdjango\gsicosttool\src

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# python manage.py runserver 8000
Performing system checks...

System check identified no issues (0 silenced).
October 30, 2019 - 09:32:20
Django version 2.1, using settings 'gsicosttool.settings.development'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
~~~~

### Test local access via django development server

Then us a web-browser (running on the web server) and visit  
    [http://127.0.0.1:8000](http://127.0.0.1:8000 "http://127.0.0.1:8000")

#  Configure application in IIS

**Note:** *In these notes the application is installed as a 
Application under the Default Web Site in IIS.*

First, copy the sample web configuration file to the `src` folder.
Copy file 
    `C:\inetpub\wwwdjango\gsicosttool\docs\sample.web.config` 
and paste and change the name to `web.config`
New file
    `C:\inetpub\wwwdjango\gsicosttool\src\web.config` 

Then, in IIS, create a new `Application`
Set the `Alias` to **gsicosttool** and    
set the `Physical path` to `C:\inetpub\wwwdjango\gsicosttool\src`

Now use a web-browser (on the web server) and visit  
    [http://localhost/gsicosttool](http://localhost/gsicosttool "http://localhost/gsicosttool")

____
### These are the longer notes if you don't use the complete sample.web.config file above

In IIS, double-click the 'gsicosttool' application and open the **Handler Mappings** feature.

Then use Add Module Mapping

Set the fields:  
1. Request path: `*`    
2. Module: `FastCgiModule`  
3. Executable: 
    `C:\software\Python\virtualenvs\gsicosttool\Scripts\python.exe|C:\software\Python\virtualenvs\gsicosttool\Lib\site-packages\wfastcgi.py`  
4. Name: `GSICostTool FastCGI Module`

When you close this dialog it will prompt to save a FastCGI application.  Click 'yes'

In IIS, select the server machine node (first line after Start Page)

Then double-click 'FastCGI Settings' feature.

Select the row with the Full Path `C:\software\Python\virtualenvs\gsicosttool\Scripts\python.exe` 

Click Edit... from the Actions menu 

In the Edit FastCGI Application menu, select the 'Environment Variables' row
and double-click the '...' button on the right side.

Now add 3 entries:

Name: `PYTHONPATH`  
Value: `C:\inetpub\wwwdjango\gsicosttool\src`

Name: `WSGI_HANDLER`  
Value: `django.core.wsgi.get_wsgi_application()`

Name: `DJANGO_SETTINGS_MODULE`  
Value: `gsicosttool.settings.production`

Now make sure the `static` folder is configured correctly

In IIS, expand the 'gsicosttool' node, and then click the `static` subfolder.

Click the 'Handler Mappings' feature, and click 'View ordered list'
The 'StaticFile' handler should be at the top of the list.  If not, use
the 'Move Up' option to move it to the top.

The web application uses Django Datatables to display tables of 
data.  Datatables uses a very exhaustive syntax to display
the data, and this can make the query strings long - sometimes causing
IIS to refuse to use run the query.  To fix this

In IIS, select the server machine node (first line after Start Page)
Then open the Request Filtering feature.
On the right side menu, select Edit Feature Settings... and in the dialog box, change 
the 2 settings

* Maximum URL length (Bytes) 4096
* Maximum query string (Bytes) 5000

### Test local access via IIS

Now use a web-browser (on the web server) and visit  
    [http://localhost/gsicosttool](http://localhost/gsicosttool "http://localhost/gsicosttool")

# Configure for external access

Now you should be able to view the web application from 
another computer after making 1 edit.

Django has a security feature that requires setting the HTTP name
of the server the application is running on.

Edit the file
    `C:\inetpub\wwwdjango\gsicosttool\src\gsicosttool\settings\local.production.env`

Find the line that looks like this

ALLOWED_HOSTS=127.0.0.1,localhost

and add the hostname that users will use to reach the application.

For example

ALLOWED_HOSTS=127.0.0.1,localhost,insdev1.tetratech.com

### Test external access via IIS

Now use a web-browser (on the web server) and visit  
    [https://insdev1.tetratech.com/gsicosttool](https://insdev1.tetratech.com/gsicosttool "https://insdev1.tetratech.com/gsicosttool")


