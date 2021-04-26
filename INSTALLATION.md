

## Installation Notes for django (python) web application 'gsicosttool'

These notes are for installing the City of Raleigh NC GSI Cost Tool 'gsicosttool'
on a Windows 2016 Data Center server running an IIS webserver.

The gsicosttool is written using the python Django framework.

The instance described in these notes uses a Microsoft SQL Server database, and 
there is a dependency on using a python package 'pyodbc' that only runs
on Django 2.1.  

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
pip 21.1 from c:\software\python\python38\lib\site-packages\pip (python 3.8)
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
# git clone https://github.com/JamesBisese/gsicosttool.git
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
10/28/2019  09:55 AM    <DIR>          docs
10/28/2019  09:55 AM            23,070 INSTALLATION.md
10/28/2019  09:55 AM             1,133 README.md
10/28/2019  09:55 AM    <DIR>          src
..
user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool
# cd src

user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# dir
...
10/28/2019  09:55 AM    <DIR>          accounts
10/28/2019  09:55 AM    <DIR>          authtools
10/28/2019  09:55 AM    <DIR>          costly
10/28/2019  09:55 AM               458 manage.py
10/28/2019  09:55 AM    <DIR>          media
10/28/2019  09:55 AM    <DIR>          profiles
10/28/2019  09:55 AM             1,026 requirements.txt
10/28/2019  09:55 AM    <DIR>          scenario
10/28/2019  09:55 AM    <DIR>          templates
10/28/2019  09:55 AM    <DIR>          users
10/28/2019  09:55 AM                 0 __init__.py
...
~~~~

## Create a virtualenv for the application

This python virtual environment is used to sandbox all changes just for this single application
~~~~
user.name@MACHINENAME C:\inetpub\wwwdjango
$ chdir C:\software\Python\virtualenvs

user.name@MACHINENAME C:\software\Python\virtualenvs                      
# virtualenv gsicosttool                                                        
Using base prefix 'c:\\software\\python\\python38'                              
New python executable in  
C:\software\Python\virtualenvs\gsicosttool\Scripts\python.exe                                                                          
Installing setuptools, pip, wheel...                                            
done.                                                                           
~~~~
Go into that folder and 'activate' the virtual environment.
  Note that the prompt changes to indicate that the virtual env is active
~~~~
user.name@MACHINENAME C:\software\Python\virtualenvs
# chdir gsicosttool\Scripts

user.name@MACHINENAME C:\software\Python\virtualenvs\gsicosttool\Scripts
# activate

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

The application 'requirements' file contains a list of all the external python packages needed  to run the django app

The GSI Cost Tool requirements file is in  
    `C:\inetpub\wwwdjango\gsicosttool\src\requirements.txt` 


From experience, I know that there are several python packages that 
failed to install during the first attempt, so I suggest using
pre-compiled versions of these packages.

Pre-compiled version for windows are available from  
    `https://www.lfd.uci.edu/~gohlke/pythonlibs/`

On that page download these 3 packages to your `download` folder 
(you can download the most recent version of these packages if there are updates)
1. `C:\downloads\pyodbc-4.0.27-cp38-cp38-win32.whl`

Install pre-compiled python packages
~~~~

(gsicosttool) user.name@MACHINENAME C:\software\Python\virtualenvs\gsicosttool\Scripts
# pip install C:\downloads\pyodbc-4.0.27-cp38-cp38-win32.whl
Processing c:\downloads\pyodbc-4.0.27-cp38-cp38-win32.whl
Installing collected packages: pyodbc
Successfully installed pyodbc-4.0.27
~~~~

Note: if you want to use PostgreSQL instead of Microsoft SQL Server, you need to install one other pre-compiled package

From  `https://www.lfd.uci.edu/~gohlke/pythonlibs/` download the package to your `download` folder 
(you can download the most recent version of these packages if there are updates)
1. `C:\downloads\psycopg2-2.8.4-cp38-cp38-win32.whl`

Install pre-compiled python packages
~~~~

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool\src>pip install C:\downloads\psycopg2-2.8.4-cp38-cp38-win32.whl
Processing c:\downloads\psycopg2-2.8.4-cp38-cp38-win32.whl
Installing collected packages: psycopg2
Successfully installed psycopg2-2.8.4
~~~~

___

Install all the rest of the required packages using the requirements file

NOTE: the output will vary a bit from this, since I repeated these commands during testing and so have 'caches' of the files
~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# pip install -r requirements.txt
Collecting beautifulsoup4==4.8.1
  Using cached https://files.pythonhosted.org/packages/3b/c8/a55eb6ea11cd7e5ac4bacdf92bac4693b90d3ba79268be16527555e186f0/beautifulsoup4-4.8.1-py3-none-any.whl
Collecting defusedxml==0.6.0
  Using cached https://files.pythonhosted.org/packages/06/74/9b387472866358ebc08732de3da6dc48e44b0aacd2ddaa5cb85ab7e986a2/defusedxml-0.6.0-py2.py3-none-any.whl
Collecting Django==2.1
  Using cached https://files.pythonhosted.org/packages/51/1a/e0ac7886c7123a03814178d7517dc822af0fe51a72e1a6bff26153103322/Django-2.1-py3-none-any.whl
Collecting django-appconf==1.0.3
  Using cached https://files.pythonhosted.org/packages/f6/b3/fcec63afcf323581c4919f21e90ef8c8200034108a6a0ab47a6bf6a9327b/django_appconf-1.0.3-py2.py3-none-any.whl
Collecting django-bootstrap-datepicker-plus==3.0.5
  Using cached https://files.pythonhosted.org/packages/2a/82/7ee6834d67a9d5b6d46a620f8995dc2680e00e4cb75c438803bb0f9f3863/django_bootstrap_datepicker_plus-3.0.5-py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\e8\e4\9f\9c0ba98d8724f34974a392838bc53c2cf1d7d4bff62e9c09ae\django_bootstrap4-1.0.1-cp38-none-any.whl
Collecting django-braces==1.13.0
  Using cached https://files.pythonhosted.org/packages/84/3c/fa2cca1411b456a84714efea8a2c805924eba6147e6b68e326caca9c7383/django_braces-1.13.0-py2.py3-none-any.whl
Collecting django-crispy-forms==1.8.0
  Using cached https://files.pythonhosted.org/packages/26/b0/71e60d4da12f2f6544a94bc50873956db99d02e130336d6150f6e25fd1e8/django_crispy_forms-1.8.0-py2.py3-none-any.whl
Collecting django-debug-toolbar==2.0
  Using cached https://files.pythonhosted.org/packages/67/ed/587fd4fd954717fb4cd6b87fa3345ff793ecb995d91c604fcaf26510eeff/django_debug_toolbar-2.0-py3-none-any.whl
Collecting django-environ==0.4.5
  Using cached https://files.pythonhosted.org/packages/9f/32/76295a1a5d00bf556c495216581c6997e7fa5f533b2229e0a9d6cbaa95ae/django_environ-0.4.5-py2.py3-none-any.whl
Collecting django-jquery==3.1.0
  Using cached https://files.pythonhosted.org/packages/ea/89/3c3ebe3190ee00222a34588ac0383702f0d91ebb2983408cf906c0236671/django_jquery-3.1.0-py2.py3-none-any.whl
Collecting django-location-field==2.1.0
  Using cached https://files.pythonhosted.org/packages/03/d2/cf97ca76c810892212e541cb81214cf4497ff55e641fef1bcf2b6c0ac321/django_location_field-2.1.0-py2.py3-none-any.whl
Collecting django-mathfilters==0.4.0
  Using cached https://files.pythonhosted.org/packages/c6/fb/fa2fe3d531dc018d486b03c91461063e1005e31bb00b7f2ebc6dfa09701f/django_mathfilters-0.4.0-py2.py3-none-any.whl
Collecting django-money==0.15.1
  Using cached https://files.pythonhosted.org/packages/53/10/01dd0577650fe28ed5bf529b248eef6becd4fe7c23b6d011bb95d76d3160/django_money-0.15.1-py2.py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\32\70\44\c0ced5d9d9570455c3d4caa2838858eedcb9ed9345c7c432d0\django_moneyfield-0.2.1-cp38-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\7d\24\a7\e35067e3500c49fa24c46ac0feacdec63ab14ac982652703bf\django_multiselectfield-0.1.9-cp38-none-any.whl
Collecting django-pyodbc-azure==2.1.0.0
  Using cached https://files.pythonhosted.org/packages/18/ab/133c68bbea94839d8f3b8b4aea4f70e1c6b8ac929aba4adbadc458566a76/django_pyodbc_azure-2.1.0.0-py3-none-any.whl
Collecting django-select2==7.1.1
  Using cached https://files.pythonhosted.org/packages/33/12/06b41f5cc5afa172c44cc7b8d95c2a0d5e69b64b9ef4fb7b9528e39a0ba1/django_select2-7.1.1-py2.py3-none-any.whl
Collecting django-tables2==2.1.1
  Using cached https://files.pythonhosted.org/packages/10/15/614b4945666806817fb6ad4c9470c0fd1c029135ef01814159de7ced451e/django_tables2-2.1.1-py2.py3-none-any.whl
Collecting django-widget-tweaks==1.4.5
  Using cached https://files.pythonhosted.org/packages/1c/11/a8d3a4d73a09973d62ce381fb73a926707cb1485aa29599f2afc04dee7b4/django_widget_tweaks-1.4.5-py2.py3-none-any.whl
Collecting djangorestframework==3.10.3
  Using cached https://files.pythonhosted.org/packages/33/8e/87a4e0025e3c4736c1dc728905b1b06a94968ce08de15304417acb40e374/djangorestframework-3.10.3-py3-none-any.whl
Collecting djangorestframework-datatables==0.5.0
  Using cached https://files.pythonhosted.org/packages/7f/3d/515911b8975bcc47ce52bf0c60185adc0b2ed828dee660273de8390bea4d/djangorestframework_datatables-0.5.0-py2.py3-none-any.whl
Collecting djangorestframework-filters==0.11.1
  Using cached https://files.pythonhosted.org/packages/c0/20/3506c608b3ec79a67c24b70702322ac46bc73e6217a0d9239dfef83e20c6/djangorestframework_filters-0.11.1-py2.py3-none-any.whl
Collecting django-filter==1.1.0
  Using cached https://files.pythonhosted.org/packages/ee/99/eb6f20b0ca4e2800279963599971e70c71767b9d151f44fcbcd1caa19f32/django_filter-1.1.0-py2.py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\01\c6\20\9239cdf26057e0462a634e00827d083ca1fbfa113f327c1178\easy_thumbnails-2.6-py2.py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\2a\77\35\0da0965a057698121fc7d8c5a7a9955cdbfb3cc4e2423cad39\et_xmlfile-1.0.1-cp38-none-any.whl
Collecting jdcal==1.4.1
  Using cached https://files.pythonhosted.org/packages/f0/da/572cbc0bc582390480bbd7c4e93d14dc46079778ed915b505dc494b37c57/jdcal-1.4.1-py2.py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\6f\a3\6f\430d3dacf1a1c44f904338b4474409e8087d9f0858c3d28faf\markuppy-1.14-cp38-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\06\2d\19\f5a4eed468fecff295ff8ac49e5dd5fb22d7ffc7ff072deabf\odfpy-1.4.0-py2.py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\34\ee\6c\1279f7b70ea72432c2cef15dd3d915477cb3771d1618f6b8ef\openpyxl-3.0.0-py2.py3-none-any.whl
Collecting Pillow==6.2.1
  Using cached https://files.pythonhosted.org/packages/dc/f3/c4244b8bb4175889a12e483d9d9ab51137dc9d7f1cbdfcf37939d14ba7f9/Pillow-6.2.1-cp38-cp38-win32.whl
Collecting py-moneyed==0.8.0
  Using cached https://files.pythonhosted.org/packages/fc/84/2efdf86de54c2601a66caa4504f6978432f15f79b593772e9b0cc9cceddc/py_moneyed-0.8.0-py2.py3-none-any.whl
Requirement already satisfied: pyodbc==4.0.27 in c:\software\python\virtualenvs\gsicosttool\lib\site-packages (from -r requirements.txt (line 33)) (4.0.27)
Collecting pytz==2019.3
  Using cached https://files.pythonhosted.org/packages/e7/f9/f0b53f88060247251bf481fa6ea62cd0d25bf1b11a87888e53ce5b7c8ad2/pytz-2019.3-py2.py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\d9\45\dd\65f0b38450c47cf7e5312883deb97d065e030c5cca0a365030\pyyaml-5.1.2-cp38-cp38-win32.whl
Collecting six==1.12.0
  Using cached https://files.pythonhosted.org/packages/73/fb/00a976f728d0d1fecfe898238ce23f502a721c0ac0ecfedb80e0d88c64e9/six-1.12.0-py2.py3-none-any.whl
Collecting soupsieve==1.9.4
  Using cached https://files.pythonhosted.org/packages/5d/42/d821581cf568e9b7dfc5b415aa61952b0f5e3dede4f3cbd650e3a1082992/soupsieve-1.9.4-py2.py3-none-any.whl
Collecting sqlparse==0.3.0
  Using cached https://files.pythonhosted.org/packages/ef/53/900f7d2a54557c6a37886585a91336520e5539e3ae2423ff1102daf4f3a7/sqlparse-0.3.0-py2.py3-none-any.whl
Collecting tablib==0.14.0
  Using cached https://files.pythonhosted.org/packages/7f/8d/665f895e4355f1ee95665e003b994512c8b670148a921aa9acec9d1607fb/tablib-0.14.0-py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\a6\09\e9\e800279c98a0a8c94543f3de6c8a562f60e51363ed26e71283\unicodecsv-0.14.1-cp38-none-any.whl
Collecting Werkzeug==0.16.0
  Using cached https://files.pythonhosted.org/packages/ce/42/3aeda98f96e85fd26180534d36570e4d18108d62ae36f87694b476b83d6f/Werkzeug-0.16.0-py2.py3-none-any.whl
Processing c:\users\user.name\appdata\local\pip\cache\wheels\41\08\4c\ca04f4a87b91080dc6a631bbd82390e4412dfefb7a236d5f94\wfastcgi-3.0.0-py2.py3-none-any.whl
Collecting xlrd==1.2.0
  Using cached https://files.pythonhosted.org/packages/b0/16/63576a1a001752e34bf8ea62e367997530dc553b689356b9879339cf45a4/xlrd-1.2.0-py2.py3-none-any.whl
Collecting xlwt==1.3.0
  Using cached https://files.pythonhosted.org/packages/44/48/def306413b25c3d01753603b1a222a011b8621aed27cd7f89cbc27e6b0f4/xlwt-1.3.0-py2.py3-none-any.whl
Requirement already satisfied: setuptools in c:\software\python\virtualenvs\gsicosttool\lib\site-packages (from django-money==0.15.1->-r requirements.txt (line 14)) (41.5.1)
Installing collected packages: soupsieve, beautifulsoup4, defusedxml, pytz, Django, six, django-appconf, django-bootstrap-datepicker-plus, django-bootstrap4, django-braces, django-crispy-forms, sqlparse, django-debug-toolbar, django-environ, django-jquery, django-location-field, django-mathfilters, py-moneyed, django-money, django-moneyfield, django-multiselectfield, django-pyodbc-azure, django-select2, django-tables2, django-widget-tweaks, djangorestframework, djangorestframework-datatables, django-filter, djangorestframework-filters, Pillow, easy-thumbnails, et-xmlfile, jdcal, MarkupPy, odfpy, openpyxl, PyYAML, xlrd, xlwt, tablib, unicodecsv, Werkzeug, wfastcgi
Successfully installed Django-2.1 MarkupPy-1.14 Pillow-6.2.1 PyYAML-5.1.2 Werkzeug-0.16.0 beautifulsoup4-4.8.1 defusedxml-0.6.0 django-appconf-1.0.3 django-bootstrap-datepicker-plus-3.0.5 django-bootstrap4-1.0.1 django-braces-1.13.0 django-crispy-forms-1.8.0 django-debug-toolbar-2.0 django-environ-0.4.5 django-filter-1.1.0 django-jquery-3.1.0 django-location-field-2.1.0 django-mathfilters-0.4.0 django-money-0.15.1 django-moneyfield-0.2.1 django-multiselectfield-0.1.9 django-pyodbc-azure-2.1.0.0 django-select2-7.1.1 django-tables2-2.1.1 django-widget-tweaks-1.4.5 djangorestframework-3.10.3 djangorestframework-datatables-0.5.0 djangorestframework-filters-0.11.1 easy-thumbnails-2.6 et-xmlfile-1.0.1 jdcal-1.4.1 odfpy-1.4.0 openpyxl-3.0.0 py-moneyed-0.8.0 pytz-2019.3 six-1.12.0 soupsieve-1.9.4 sqlparse-0.3.0 tablib-0.14.0 unicodecsv-0.14.1 wfastcgi-3.0.0 xlrd-1.2.0 xlwt-1.3.0
                                                                   
                                                                               
~~~~

# Configure the Application

The web application software is now installed.  Now the application needs to be 
configured, and the backend database needs to be created and populated.

## Configure the application

The application is configured using a number of `settings` files.  The files
are all located in folder
    `C:\inetpub\wwwdjango\costly\costly\settings`

Normally, you will not need to edit any of the settings `.py` files, and 
the only files that need to be edited are the `.env` files.  These are 
read into the other files.

For local development, copy file
    `C:\inetpub\wwwdjango\costly\costly\settings\local.development.sample.env` and rename it
    `C:\inetpub\wwwdjango\costly\costly\settings\local.development.env`

For production, copy file
    `C:\inetpub\wwwdjango\costly\costly\settings\local.production.sample.env` and rename it
    `C:\inetpub\wwwdjango\costly\costly\settings\local.production.env`

When the application is running using the django development server it uses the files
    `C:\inetpub\wwwdjango\costly\costly\settings\base.py`    
    `C:\inetpub\wwwdjango\costly\costly\settings\development.py` and 
    `C:\inetpub\wwwdjango\costly\costly\settings\local.development.env`

When the application is running using the django development server it uses the files
    `C:\inetpub\wwwdjango\costly\costly\settings\base.py`    
    `C:\inetpub\wwwdjango\costly\costly\settings\production.py` and 
    `C:\inetpub\wwwdjango\costly\costly\settings\local.production.env`
    


## Create the Database

Now the backend database needs to be created and all 
lookup data needs to be loaded from CSV text files into the database.

**NOTE:** *this documentation is for using SQL Server database,
it will vary a bit depending on the ODBMS used.*

The connection to the database is defined in two places -
    `C:\inetpub\wwwdjango\costly\costly\settings\local.development.env` and
    `C:\inetpub\wwwdjango\costly\costly\settings\local.production.env`    

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
    - Create model CostItemUserCosts
    - Create model CostItemUserAssumptions
    - Create model CostItemDefaultFactors

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

    `C:\inetpub\wwwdjango\gsicosttool\src\costly\management\commands\create_users.py`

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
# python manage.py dumpdata --indent 4 > costly.json

(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool\src
# ls -l costly.json
-rw-rw-rw-  1 user.name 0 531553 2019-10-28 10:48 costly.json
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
Django version 2.1, using settings 'costly.settings.development'
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
Value: `costly.settings.production`

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
    `C:\inetpub\wwwdjango\gsicosttool\src\costly\settings\local.production.env`

Find the line that looks like this

ALLOWED_HOSTS=127.0.0.1,localhost

and add the hostname that users will use to reach the application.

For example

ALLOWED_HOSTS=127.0.0.1,localhost,insdev1.tetratech.com

### Test external access via IIS

Now use a web-browser (on the web server) and visit  
    [https://insdev1.tetratech.com/gsicosttool](https://insdev1.tetratech.com/gsicosttool "https://insdev1.tetratech.com/gsicosttool")


