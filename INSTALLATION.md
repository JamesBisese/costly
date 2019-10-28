

## Installation Notes for django (python) web application 'gsicosttool'

This is an INTERIM document.
These notes are copied and pasted from an installation for another package.  I am working through the differences.


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

Download Python 3.8.0 from https://www.python.org/downloads/ (25.2 MB)

Install python version 3.8 into folder  
    `C:\software\Python\Python38`

Python is installed via a GUI
You might have to run the installer as Admin
In Optional Features only check 'pip'
Use Advanced Options uncheck everything, but set the location to install.

Customize install location  
    `C:\software\Python\Python38`

Add python to System Environmental Variable 'Path'
Include 2 folders
    `C:\software\Python\Python38` and  
    `C:\software\Python\Python38\Scripts`
	
Install Python in folder
~~~~
user.name@MACHINENAME C:\software\Python\Python38
$ python --version
Python 3.8.0
~~~~
Upgrade Python Installation Program (pip)
~~~~a
user.name@MACHINENAME C:\software\Python\Python38
$ python -m pip install --upgrade pip
~~~~
Show version of pip
~~~~
user.name@MACHINENAME C:\software\Python\Python38
$ pip --version
pip 19.3.1 from c:\software\python\python38\lib\site-packages\pip (python 3.8)
~~~~
Install python package virtualenv
~~~~
user.name@MACHINENAME C:\software\Python\Python38
$ pip install virtualenv
Collecting virtualenv
  Downloading https://files.pythonhosted.org/packages/c5/97/00dd42a0fc41e9016b23f07ec7f657f636cb672fad9cf72b80f8f65c6a46/virtualenv-16.7.7-py2.py3-none-any.whl (3.4MB)
     |████████████████████████████████| 3.4MB 939kB/s
Installing collected packages: virtualenv
Successfully installed virtualenv-16.7.7
~~~~


## Download a copy of the application from github
~~~~
james.bisese@DIVS704INSWEB1 C:\inetpub\wwwdjango
# git clone https://github.com/JamesBisese/gsicosttool.git
Cloning into 'gsicosttool'...
remote: Enumerating objects: 508, done.
remote: Counting objects: 100% (508/508), done.
remote: Compressing objects: 100% (349/349), done.
Recremote: Total 508 (delta 150), reused 491 (delta 138), pack-reused 0

Receiving objects: 100% (508/508), 11.66 MiB | 22.36 MiB/s, done.
Resolving deltas: 100% (150/150), done.
Updating files: 100% (304/304), done.

james.bisese@DIVS704INSWEB1 C:\inetpub\wwwdjango
# chdir gsicosttool

james.bisese@DIVS704INSWEB1 C:\inetpub\wwwdjango\gsicosttool
# dir
 Volume in drive C is Windows
 Volume Serial Number is 9AA8-C0AB

 Directory of C:\inetpub\wwwdjango\gsicosttool

10/28/2019  09:55 AM    <DIR>          .
10/28/2019  09:55 AM    <DIR>          ..
10/28/2019  09:55 AM    <DIR>          docs
10/28/2019  09:55 AM            23,070 INSTALLATION.md
10/28/2019  09:55 AM             1,133 README.md
10/28/2019  09:55 AM    <DIR>          src
               2 File(s)         24,203 bytes
               4 Dir(s)  107,116,556,288 bytes free

james.bisese@DIVS704INSWEB1 C:\inetpub\wwwdjango\gsicosttool
# cd src

james.bisese@DIVS704INSWEB1 C:\inetpub\wwwdjango\gsicosttool\src
# dir
 Volume in drive C is Windows
 Volume Serial Number is 9AA8-C0AB

 Directory of C:\inetpub\wwwdjango\gsicosttool\src

10/28/2019  09:55 AM    <DIR>          .
10/28/2019  09:55 AM    <DIR>          ..
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
               3 File(s)          1,484 bytes
              10 Dir(s)  107,112,361,984 bytes free

~~~~

## Create a virtualenv for the application

This python virtual environment is used to sandbox all changes just for this single application
~~~~
user.name@MACHINENAME C:\inetpub\wwwdjango
$ chdir C:\software\Python\virtualenvs

james.bisese@DIVS704INSWEB1 C:\software\Python\virtualenvs                      
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
james.bisese@DIVS704INSWEB1 C:\software\Python\virtualenvs
# cd gsicosttool\Scripts

james.bisese@DIVS704INSWEB1 C:\software\Python\virtualenvs\gsicosttool\Scripts
# activate

(gsicosttool) james.bisese@DIVS704INSWEB1 C:\software\Python\virtualenvs\gsicosttool\Scripts
#
~~~~
## Install all required python packages 

Using the virtual environment, all the packages will be installed on the virtual environment 
folder `C:\software\Python\virtualenvs\gsicosttool` and will not affect the system-wide python installation.

The file `C:\inetpub\wwwdjango\gsicosttool\src\requirements.txt` contains a list of all the external python packages needed  to run the django app

From experience, I know that there are several python packages that 
failed to install during the first attempt, so I suggest using
pre-compiled versions of these packages.

Pre-compiled version for windows are available from  
    'https://www.lfd.uci.edu/~gohlke/pythonlibs/'

On that page download these 3 packages to your `download` folder 
(you can download the most recent version of these packages if there are updates)
1. `C:\downloads\psycopg2-2.8.4-cp38-cp38-win32.whl`
1. `C:\downloads\pyodbc-4.0.27-cp38-cp38-win32.whl`
1. `C:\downloads\Django-2.2.6-py3-none-any.whl`

Install pre-compiled python packages
~~~~
(gsicosttool) user.name@MACHINENAME C:\software\Python\virtualenvs\gsicosttool\Scripts
# pip install C:\downloads\psycopg2-2.8.4-cp38-cp38-win32.whl
Processing c:\downloads\psycopg2-2.8.4-cp38-cp38-win32.whl
Installing collected packages: psycopg2
Successfully installed psycopg2-2.8.4

(gsicosttool) user.name@MACHINENAME C:\software\Python\virtualenvs\gsicosttool\Scripts
# pip install C:\downloads\pyodbc-4.0.27-cp38-cp38-win32.whl
Processing c:\downloads\pyodbc-4.0.27-cp38-cp38-win32.whl
Installing collected packages: pyodbc
Successfully installed pyodbc-4.0.27

(gsicosttool) user.name@MACHINENAME C:\software\Python\virtualenvs\gsicosttool\Scripts
# pip install C:\downloads\Django-2.2.6-py3-none-any.whl
Processing c:\downloads\django-2.2.6-py3-none-any.whl
Collecting sqlparse
  Using cached https://files.pythonhosted.org/packages/ef/53/900f7d2a54557c6a37886585a91336520e5539e3ae2423ff1102daf4f3a7/sqlparse-0.3.0-py2.py3-none-any.whl
Collecting pytz
  Downloading https://files.pythonhosted.org/packages/e7/f9/f0b53f88060247251bf481fa6ea62cd0d25bf1b11a87888e53ce5b7c8ad2/pytz-2019.3-py2.py3-none-any.whl (509kB)
     |████████████████████████████████| 512kB 3.3MB/s
Installing collected packages: sqlparse, pytz, Django
Successfully installed Django-2.2.6 pytz-2019.3 sqlparse-0.3.0

~~~~
Install all the rest of the required packages using the requirements file

NOTE: the output will vary a bit from this, since I repeated these commands during testing and so have 'caches' of the files
~~~~
(gsicosttool) user.name@MACHINENAME C:\software\Python\virtualenvs\gsicos
tool\Scripts                                                                   
# pip install -r C:\inetpub\wwwdjango\gsicosttool\src\requirements.txt         
Collecting beautifulsoup4==4.8.1                                               
  Downloading https://files.pythonhosted.org/packages/3b/c8/a55eb6ea11cd7e5ac4b
cdf92bac4693b90d3ba79268be16527555e186f0/beautifulsoup4-4.8.1-py3-none-any.whl 
101kB)                                                                         
     |████████████████████████████████| 102kB 2.2MB/s                          
Collecting defusedxml==0.6.0                                                   
  Using cached https://files.pythonhosted.org/packages/06/74/9b387472866358ebc0
732de3da6dc48e44b0aacd2ddaa5cb85ab7e986a2/defusedxml-0.6.0-py2.py3-none-any.whl
Requirement already satisfied: Django==2.2.6 in c:\software\python\virtualenvs\
sicosttool\lib\site-packages (from -r C:\inetpub\wwwdjango\gsicosttool\src\requ
rements.txt (line 3)) (2.2.6)                                                  
Collecting django-appconf==1.0.3                                               
  Downloading https://files.pythonhosted.org/packages/f6/b3/fcec63afcf323581c49
9f21e90ef8c8200034108a6a0ab47a6bf6a9327b/django_appconf-1.0.3-py2.py3-none-any.
hl                                                                             
Collecting django-bootstrap-datepicker-plus==3.0.5                             
  Downloading https://files.pythonhosted.org/packages/2a/82/7ee6834d67a9d5b6d46
620f8995dc2680e00e4cb75c438803bb0f9f3863/django_bootstrap_datepicker_plus-3.0.5
py3-none-any.whl                                                               
Collecting django-bootstrap4==1.0.1                                            
  Downloading https://files.pythonhosted.org/packages/3a/01/af39712da23fb3a1f1b
1787dc150c255bd60f70324a6ec14be90d1576f2/django-bootstrap4-1.0.1.tar.gz (6.8MB)
     |████████████████████████████████| 6.8MB 225kB/s                          
Collecting django-braces==1.13.0                                               
  Downloading https://files.pythonhosted.org/packages/84/3c/fa2cca1411b456a8471
efea8a2c805924eba6147e6b68e326caca9c7383/django_braces-1.13.0-py2.py3-none-any.
hl                                                                             
Collecting django-crispy-forms==1.8.0                                          
  Downloading https://files.pythonhosted.org/packages/26/b0/71e60d4da12f2f6544a
4bc50873956db99d02e130336d6150f6e25fd1e8/django_crispy_forms-1.8.0-py2.py3-none
any.whl (105kB)                                                                
     |████████████████████████████████| 112kB 6.8MB/s                          
Collecting django-debug-toolbar==2.0                                           
  Downloading https://files.pythonhosted.org/packages/67/ed/587fd4fd954717fb4cd
b87fa3345ff793ecb995d91c604fcaf26510eeff/django_debug_toolbar-2.0-py3-none-any.
hl (198kB)                                                                     
     |████████████████████████████████| 204kB 6.8MB/s                          
Collecting django-environ==0.4.5                                               
  Downloading https://files.pythonhosted.org/packages/9f/32/76295a1a5d00bf556c4
5216581c6997e7fa5f533b2229e0a9d6cbaa95ae/django_environ-0.4.5-py2.py3-none-any.
hl                                                                             
Collecting django-filter==2.2.0                                                
  Downloading https://files.pythonhosted.org/packages/0a/c9/acc63b687002afae8b5
37afd6230d88c99411aa2daedf07fed3f0913516/django_filter-2.2.0-py3-none-any.whl (
9kB)                                                                           
     |████████████████████████████████| 71kB 4.8MB/s                           
Collecting django-intl-tel-input==0.3.1                                        
  Downloading https://files.pythonhosted.org/packages/94/45/dbe1787c5a51f4f8814
e65c276ba9dc78c35bb4fdbcc950496b4b611f61/django_intl_tel_input-0.3.1-py2.py3-no
e-any.whl                                                                      
Collecting django-intl-tel-input2==0.2.0                                       
  Downloading https://files.pythonhosted.org/packages/07/d3/c65b8e91b26151b3d35
c0fc5297f9b0a9ec31f7da6f7fdca6c0716082f9/django-intl-tel-input2-0.2.0.tar.gz   
Collecting django-jquery==3.1.0                                                
  Downloading https://files.pythonhosted.org/packages/ea/89/3c3ebe3190ee00222a3
588ac0383702f0d91ebb2983408cf906c0236671/django_jquery-3.1.0-py2.py3-none-any.w
l                                                                              
Collecting django-location-field==2.1.0                                        
  Downloading https://files.pythonhosted.org/packages/03/d2/cf97ca76c810892212e
41cb81214cf4497ff55e641fef1bcf2b6c0ac321/django_location_field-2.1.0-py2.py3-no
e-any.whl (71kB)                                                               
     |████████████████████████████████| 71kB 2.3MB/s                           
Collecting django-mathfilters==0.4.0                                           
  Downloading https://files.pythonhosted.org/packages/c6/fb/fa2fe3d531dc018d486
03c91461063e1005e31bb00b7f2ebc6dfa09701f/django_mathfilters-0.4.0-py2.py3-none-
ny.whl                                                                         
Collecting django-money==0.15.1                                                
  Downloading https://files.pythonhosted.org/packages/53/10/01dd0577650fe28ed5b
529b248eef6becd4fe7c23b6d011bb95d76d3160/django_money-0.15.1-py2.py3-none-any.w
l                                                                              
Collecting django-moneyfield==0.2.1                                            
  Downloading https://files.pythonhosted.org/packages/aa/25/91c3dad4a7f05a94c85
e04ca208026c0e4e1e90da013662602dfe1fbfa3/django-moneyfield-0.2.1.tar.gz        
Collecting django-multiselectfield==0.1.9                                      
  Downloading https://files.pythonhosted.org/packages/9e/1d/de057c2fcf1ec880025
df258b4b8ad346af5d8a5155273f15f4c1f5536e/django-multiselectfield-0.1.9.tar.gz  
Collecting django-pyodbc-azure==2.1.0.0                                        
  Downloading https://files.pythonhosted.org/packages/18/ab/133c68bbea94839d8f3
8b4aea4f70e1c6b8ac929aba4adbadc458566a76/django_pyodbc_azure-2.1.0.0-py3-none-a
y.whl                                                                          
Collecting django-select2==7.1.1                                               
  Downloading https://files.pythonhosted.org/packages/33/12/06b41f5cc5afa172c44
c7b8d95c2a0d5e69b64b9ef4fb7b9528e39a0ba1/django_select2-7.1.1-py2.py3-none-any.
hl                                                                             
Collecting django-tables2==2.1.1                                               
  Using cached https://files.pythonhosted.org/packages/10/15/614b4945666806817f
6ad4c9470c0fd1c029135ef01814159de7ced451e/django_tables2-2.1.1-py2.py3-none-any
whl                                                                            
Collecting django-widget-tweaks==1.4.5                                         
  Downloading https://files.pythonhosted.org/packages/1c/11/a8d3a4d73a09973d62c
381fb73a926707cb1485aa29599f2afc04dee7b4/django_widget_tweaks-1.4.5-py2.py3-non
-any.whl                                                                       
Collecting djangorestframework==3.10.3                                         
  Using cached https://files.pythonhosted.org/packages/33/8e/87a4e0025e3c4736c1
c728905b1b06a94968ce08de15304417acb40e374/djangorestframework-3.10.3-py3-none-a
y.whl                                                                          
Collecting djangorestframework-datatables==0.5.0                               
  Using cached https://files.pythonhosted.org/packages/7f/3d/515911b8975bcc47ce
2bf0c60185adc0b2ed828dee660273de8390bea4d/djangorestframework_datatables-0.5.0-
y2.py3-none-any.whl                                                            
Collecting djangorestframework-filters==0.11.1                                 
  Downloading https://files.pythonhosted.org/packages/c0/20/3506c608b3ec79a67c2
b70702322ac46bc73e6217a0d9239dfef83e20c6/djangorestframework_filters-0.11.1-py2
py3-none-any.whl                                                               
Collecting easy-thumbnails==2.6                                                
  Downloading https://files.pythonhosted.org/packages/ae/37/442523964379e1076a4
9c29a89861f44e8c237fa6857e71b113cb2cb5bd/easy-thumbnails-2.6.tar.gz (68kB)     
     |████████████████████████████████| 71kB 1.2MB/s                           
Processing c:\users\username\appdata\local\pip\cache\wheels\2a\77\35\0da096
a057698121fc7d8c5a7a9955cdbfb3cc4e2423cad39\et_xmlfile-1.0.1-cp38-none-any.whl 
Collecting jdcal==1.4.1                                                        
  Using cached https://files.pythonhosted.org/packages/f0/da/572cbc0bc582390480
bd7c4e93d14dc46079778ed915b505dc494b37c57/jdcal-1.4.1-py2.py3-none-any.whl     
Collecting MarkupPy==1.14                                                      
  Downloading https://files.pythonhosted.org/packages/4e/ca/f43541b41bd17fc945c
ae7ea44f1661dc21ea65ecc944a6fa138eead94c/MarkupPy-1.14.tar.gz                  
Processing c:\users\username\appdata\local\pip\cache\wheels\06\2d\19\f5a4ee
468fecff295ff8ac49e5dd5fb22d7ffc7ff072deabf\odfpy-1.4.0-py2.py3-none-any.whl   
Collecting openpyxl==3.0.0                                                     
  Downloading https://files.pythonhosted.org/packages/6f/af/88ff9eef0b8f665aee1
11ac6cede5ad12190c5bd726242bd2b26fc21b32/openpyxl-3.0.0.tar.gz (172kB)         
     |████████████████████████████████| 174kB 6.8MB/s                          
Collecting Pillow==6.2.1                                                       
  Downloading https://files.pythonhosted.org/packages/dc/f3/c4244b8bb4175889a12
483d9d9ab51137dc9d7f1cbdfcf37939d14ba7f9/Pillow-6.2.1-cp38-cp38-win32.whl (1.8M
)                                                                              
     |████████████████████████████████| 1.8MB 6.8MB/s                          
Requirement already satisfied: psycopg2==2.8.4 in c:\software\python\virtualenv
\gsicosttool\lib\site-packages (from -r C:\inetpub\wwwdjango\gsicosttool\src\re
uirements.txt (line 34)) (2.8.4)                                               
Collecting py-moneyed==0.8.0                                                   
  Downloading https://files.pythonhosted.org/packages/fc/84/2efdf86de54c2601a66
aa4504f6978432f15f79b593772e9b0cc9cceddc/py_moneyed-0.8.0-py2.py3-none-any.whl 
Requirement already satisfied: pyodbc==4.0.27 in c:\software\python\virtualenvs
gsicosttool\lib\site-packages (from -r C:\inetpub\wwwdjango\gsicosttool\src\req
irements.txt (line 36)) (4.0.27)                                               
Requirement already satisfied: pytz==2019.3 in c:\software\python\virtualenvs\g
icosttool\lib\site-packages (from -r C:\inetpub\wwwdjango\gsicosttool\src\requi
ements.txt (line 37)) (2019.3)                                                 
Processing c:\users\username\appdata\local\pip\cache\wheels\d9\45\dd\65f0b3
450c47cf7e5312883deb97d065e030c5cca0a365030\pyyaml-5.1.2-cp38-cp38-win32.whl   
Collecting six==1.12.0                                                         
  Using cached https://files.pythonhosted.org/packages/73/fb/00a976f728d0d1fecf
898238ce23f502a721c0ac0ecfedb80e0d88c64e9/six-1.12.0-py2.py3-none-any.whl      
Collecting soupsieve==1.9.4                                                    
  Downloading https://files.pythonhosted.org/packages/5d/42/d821581cf568e9b7dfc
b415aa61952b0f5e3dede4f3cbd650e3a1082992/soupsieve-1.9.4-py2.py3-none-any.whl  
Requirement already satisfied: sqlparse==0.3.0 in c:\software\python\virtualenv
\gsicosttool\lib\site-packages (from -r C:\inetpub\wwwdjango\gsicosttool\src\re
uirements.txt (line 41)) (0.3.0)                                               
Collecting tablib==0.14.0                                                      
  Downloading https://files.pythonhosted.org/packages/7f/8d/665f895e4355f1ee956
5e003b994512c8b670148a921aa9acec9d1607fb/tablib-0.14.0-py3-none-any.whl (65kB) 
     |████████████████████████████████| 71kB 1.6MB/s                           
Processing c:\users\username\appdata\local\pip\cache\wheels\a6\09\e9\e80027
c98a0a8c94543f3de6c8a562f60e51363ed26e71283\unicodecsv-0.14.1-cp38-none-any.whl
Collecting Werkzeug==0.16.0                                                    
  Downloading https://files.pythonhosted.org/packages/ce/42/3aeda98f96e85fd2618
534d36570e4d18108d62ae36f87694b476b83d6f/Werkzeug-0.16.0-py2.py3-none-any.whl (
27kB)                                                                          
     |████████████████████████████████| 327kB 6.8MB/s                          
Collecting xlrd==1.2.0                                                         
  Using cached https://files.pythonhosted.org/packages/b0/16/63576a1a001752e34b
8ea62e367997530dc553b689356b9879339cf45a4/xlrd-1.2.0-py2.py3-none-any.whl      
Collecting xlwt==1.3.0                                                         
  Using cached https://files.pythonhosted.org/packages/44/48/def306413b25c3d017
3603b1a222a011b8621aed27cd7f89cbc27e6b0f4/xlwt-1.3.0-py2.py3-none-any.whl      
Requirement already satisfied: setuptools in c:\software\python\virtualenvs\gsi
osttool\lib\site-packages (from django-money==0.15.1->-r C:\inetpub\wwwdjango\g
icosttool\src\requirements.txt (line 17)) (41.5.0)                             
Building wheels for collected packages: django-bootstrap4, django-intl-tel-inpu
2, django-moneyfield, django-multiselectfield, easy-thumbnails, MarkupPy, openp
xl                                                                             
  Building wheel for django-bootstrap4 (setup.py) ... done                     
  Created wheel for django-bootstrap4: filename=django_bootstrap4-1.0.1-cp38-no
e-any.whl size=158264 sha256=943657aee12820f825e320374012818fa0593683e897178cac
bfb106c695b8c                                                                  
  Stored in directory: c:\users\username\AppData\Local\pip\Cache\wheels\e8\
4\9f\9c0ba98d8724f34974a392838bc53c2cf1d7d4bff62e9c09ae                        
  Building wheel for django-intl-tel-input2 (setup.py) ... done                
  Created wheel for django-intl-tel-input2: filename=django_intl_tel_input2-0.2
0-cp38-none-any.whl size=7200 sha256=69544e342dd7f528efe2d2ec9abcd054388fc45741
5dcef02c4753c9d49d2f4                                                          
  Stored in directory: c:\users\username\AppData\Local\pip\Cache\wheels\ba\
3\61\70f116684bfd91a77876169b91d0baeec9f7a504a5efcc4170                        
  Building wheel for django-moneyfield (setup.py) ... done                     
  Created wheel for django-moneyfield: filename=django_moneyfield-0.2.1-cp38-no
e-any.whl size=5996 sha256=a82f3779eca7b671ca41f24db1e8df4946e5c0d923127b419314
3aad97b38ea                                                                    
  Stored in directory: c:\users\username\AppData\Local\pip\Cache\wheels\32\
0\44\c0ced5d9d9570455c3d4caa2838858eedcb9ed9345c7c432d0                        
  Building wheel for django-multiselectfield (setup.py) ... done               
  Created wheel for django-multiselectfield: filename=django_multiselectfield-0
1.9-cp38-none-any.whl size=14385 sha256=59ae968a79dbcd164940d8b552fdc0bb8e91640
c264652d1138e1929e9837d5                                                       
  Stored in directory: c:\users\username\AppData\Local\pip\Cache\wheels\7d\
4\a7\e35067e3500c49fa24c46ac0feacdec63ab14ac982652703bf                        
  Building wheel for easy-thumbnails (setup.py) ... done                       
  Created wheel for easy-thumbnails: filename=easy_thumbnails-2.6-py2.py3-none-
ny.whl size=67176 sha256=3d05f25c43edb633b72254cb3c6007f432fa48aa91cb0634aecb44
379cd2cf7                                                                      
  Stored in directory: c:\users\username\AppData\Local\pip\Cache\wheels\01\
6\20\9239cdf26057e0462a634e00827d083ca1fbfa113f327c1178                        
  Building wheel for MarkupPy (setup.py) ... done                              
  Created wheel for MarkupPy: filename=MarkupPy-1.14-cp38-none-any.whl size=742
 sha256=75b26d0d6e6b9d101a1b3f5430141747e49e29b26c7b3cf16ae364db0a39fc72       
  Stored in directory: c:\users\username\AppData\Local\pip\Cache\wheels\6f\
3\6f\430d3dacf1a1c44f904338b4474409e8087d9f0858c3d28faf                        
  Building wheel for openpyxl (setup.py) ... done                              
  Created wheel for openpyxl: filename=openpyxl-3.0.0-py2.py3-none-any.whl size
241193 sha256=04e3b72d3f32e54f3f7afe9e98168ed287a636d76c1cbf46a1917254bba11fcd 
  Stored in directory: c:\users\username\AppData\Local\pip\Cache\wheels\34\
e\6c\1279f7b70ea72432c2cef15dd3d915477cb3771d1618f6b8ef                        
Successfully built django-bootstrap4 django-intl-tel-input2 django-moneyfield d
ango-multiselectfield easy-thumbnails MarkupPy openpyxl                        
ERROR: django-pyodbc-azure 2.1.0.0 has requirement Django<2.2,>=2.1.0, but you'
l have django 2.2.6 which is incompatible.                                     
ERROR: djangorestframework-filters 0.11.1 has requirement django-filter~=1.1, b
t you'll have django-filter 2.2.0 which is incompatible.                       
Installing collected packages: soupsieve, beautifulsoup4, defusedxml, six, djan
o-appconf, django-bootstrap-datepicker-plus, django-bootstrap4, django-braces, 
jango-crispy-forms, django-debug-toolbar, django-environ, django-filter, django
intl-tel-input, django-intl-tel-input2, django-jquery, django-location-field, d
ango-mathfilters, py-moneyed, django-money, django-moneyfield, django-multisele
tfield, django-pyodbc-azure, django-select2, django-tables2, django-widget-twea
s, djangorestframework, djangorestframework-datatables, djangorestframework-fil
ers, Pillow, easy-thumbnails, et-xmlfile, jdcal, MarkupPy, odfpy, openpyxl, PyY
ML, xlwt, xlrd, tablib, unicodecsv, Werkzeug                                   
Successfully installed MarkupPy-1.14 Pillow-6.2.1 PyYAML-5.1.2 Werkzeug-0.16.0 
eautifulsoup4-4.8.1 defusedxml-0.6.0 django-appconf-1.0.3 django-bootstrap-date
icker-plus-3.0.5 django-bootstrap4-1.0.1 django-braces-1.13.0 django-crispy-for
s-1.8.0 django-debug-toolbar-2.0 django-environ-0.4.5 django-filter-2.2.0 djang
-intl-tel-input-0.3.1 django-intl-tel-input2-0.2.0 django-jquery-3.1.0 django-l
cation-field-2.1.0 django-mathfilters-0.4.0 django-money-0.15.1 django-moneyfie
d-0.2.1 django-multiselectfield-0.1.9 django-pyodbc-azure-2.1.0.0 django-select
-7.1.1 django-tables2-2.1.1 django-widget-tweaks-1.4.5 djangorestframework-3.10
3 djangorestframework-datatables-0.5.0 djangorestframework-filters-0.11.1 easy-
humbnails-2.6 et-xmlfile-1.0.1 jdcal-1.4.1 odfpy-1.4.0 openpyxl-3.0.0 py-moneye
-0.8.0 six-1.12.0 soupsieve-1.9.4 tablib-0.14.0 unicodecsv-0.14.1 xlrd-1.2.0 xl
t-1.3.0                                                                        
                                                                               
~~~~

## Configure the Application

The web application software is now installed.  Now the backend database needs 
to be created and populated.

## Create the Database

Now the backend database needs to be created and all 
lookup data needs to be loaded from CSV text files into the database.

**NOTE:** *this documentation is for using PostgreSQL database,
it will vary a bit depending on the ODBMS used.*

The connection to the database is defined in the file  
    `C:\inetpub\wwwdjango\costly\costly\settings\base.py`
~~~~
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'costtool',
		'USER': 'postgres',
		'PASSWORD': '...........',
		'HOST': '127.0.0.1',
		'PORT': '5433',
		'DATABASE_SCHEMA': 'pubic'
	}
}
~~~~

Run python django process to make migration scripts that automate the 
process of creating tables and related objects in the database.
~~~~
(gsicosttool) user.name@MACHINENAME C:\inetpub\wwwdjango\gsicosttool
# python manage.py makemigrations wbddata
Migrations for 'wbddata':
  wbddata\migrations\0001_initial.py
    - Create model HUC
    - Create model WBD
    - Create model WBDAttributes
    - Create model HuNavigator
    - Create index huc_code_idx on field(s) huc_code of model hunavigator
    - Create index upstream_huc_code_idx on field(s) upstream_huc_code of model hunavigator
    - Alter unique_together for hunavigator (1 constraint(s))
~~~~

Run the python django process to run the migration scripts 
and create tables and related objects in the database.

~~~~
(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
# python manage.py migrate wbddata
Operations to perform:
  Apply all migrations: wbddata
Running migrations:
  Applying wbddata.0001_initial... OK

(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
#
~~~~

## Populate the Database

Now you have to load the data into the tables using 
python django 'command' scripts.

The data that is loaded into the database is all in folder  
    `C:\inetpub\wwwdjango\wbd\wbddata\static\data`

All the files are CSV (text files)

~~~~
user.name@MACHINENAME C:\Data_and_Tools\django_install\wbd
$ chdir C:\inetpub\wwwdjango\wbd\wbddata\static\data

user.name@MACHINENAME C:\inetpub\wwwdjango\wbd\wbddata\static\data
$ dir
...
10/22/2019  05:24 PM         6,917,283 geography.csv
10/22/2019  05:24 PM        11,123,358 huc12_attributes.csv
10/22/2019  05:24 PM         6,313,002 huc12_route.csv
10/22/2019  05:24 PM           134,008 huc_hydrologic_unit_codes.csv
10/22/2019  05:24 PM        77,923,289 metrics2016.csv
10/22/2019  05:24 PM        30,412,333 metrics2017.csv
10/22/2019  05:24 PM         6,917,283 metrics2020.csv
10/22/2019  05:24 PM            98,822 wbd_attributes.csv
10/22/2019  05:24 PM        11,123,359 wbd_navigation.csv
...

~~~~

The command scripts are in folder  
    `C:\inetpub\wwwdjango\wbd\wbddata\management\commands`

The scripts have to be run in a particular order to deal with dependencies.

The output from the command scripts has been removed.
~~~~
(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
# python manage.py load_HUC
...

(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
# python manage.py load_WBD
...

(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
# python manage.py load_WbdAttributes

(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
# python manage.py load_HuNavigator
~~~~

Then run a command does not load data into the database, but 
 instead makes a set of folders and files that improve 
 the performance of the system used to export Attribute data
~~~~
(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
# python manage.py create_source_category_indicator_files
~~~~

This command will create additional sub-folders so that the data 
folder now contains  

~~~~
user.name@MACHINENAME C:\Data_and_Tools\django_install\wbd
$ chdir C:\inetpub\wwwdjango\wbd\wbddata\static\data

user.name@MACHINENAME C:\inetpub\wwwdjango\wbd\wbddata\static\data
$ dir
...
10/22/2019  06:09 PM    <DIR>          django_cache
10/22/2019  06:04 PM    <DIR>          Geography
10/22/2019  05:24 PM         6,917,283 geography.csv
10/22/2019  05:24 PM        11,123,358 huc12_attributes.csv
10/22/2019  05:24 PM         6,313,002 huc12_route.csv
10/22/2019  05:24 PM           134,008 huc_hydrologic_unit_codes.csv
10/22/2019  05:24 PM        77,923,289 metrics2016.csv
10/22/2019  05:24 PM        30,412,333 metrics2017.csv
10/22/2019  05:24 PM         6,917,283 metrics2020.csv
10/22/2019  06:04 PM    <DIR>          Service2016
10/22/2019  06:04 PM    <DIR>          Service2017
10/22/2019  05:24 PM            98,822 wbd_attributes.csv
10/22/2019  05:24 PM        11,123,359 wbd_navigation.csv
...

~~~~

Now run a command to collect all the files that will be 
served from IIS as 'static' files (not django application).
Static files include images, javascript, and css.

~~~~
(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
$ python manage.py collectstatic

You have requested to collect static files at the destination
location as specified in your settings:

    C:\inetpub\wwwdjango\wbd\static

This will overwrite existing files!
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: yes

222 static files copied to 'C:\inetpub\wwwdjango\wbd\static'.

~~~~

### Run the application using the django development server

The application is now setup.  

It can be run in a development mode, and viewed in a web browser
locally using this command.

~~~~
(wbd) user.name@MACHINENAME C:\inetpub\wwwdjango\wbd
$ python manage.py runserver 8000
Performing system checks...

System check identified no issues (0 silenced).

You have 17 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

October 25, 2019 - 13:32:09
Django version 2.2.5, using settings 'wbd.development_settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
~~~~

### Test local access via django development server

Then us a web-browser (running on the web server) and visit  
    [http://127.0.0.1:8000](http://127.0.0.1:8000 "http://127.0.0.1:8000")

#  Configure application in IIS

**Note:** *In these notes the application is installed as a 
Application under the Default Web Site in IIS.*

In IIS, add the folder `C:\inetpub\wwwdjango\wbd` as an Application

Set the `Alias` to **wbd** and set the `Physical path` to `C:\inetpub\wwwdjango\wbd`

In IIS, double-click the 'wbd' application and open the **Handler Mappings** feature.

Set the fields:  
1. Request path: `*`    
2. Module: `FastCgiModule`  
3. Executable: 
    `C:\software\Python\virtualenvs\wbd\Scripts\python.exe|C:\software\Python\virtualenvs\wbd\Lib\site-packages\wfastcgi.py`  
4. Name: `WBD FastCGI Module`

When you close this dialog it will prompt to save a FastCGI application.  Click 'yes'

In IIS, select the server machine node (first line after Start Page)

Then double-click 'FastCGI Settings' feature.

Select the row with the Full Path `C:\software\Python\virtualenvs\wbd\Scripts\python.exe` 

Click Edit... from the Actions menu 

In the Edit FastCGI Application menu, select the 'Environment Variables' row
and double-click the '...' button on the right side.

Now add 3 entries:

Name: `PYTHONPATH`  
Value: `C:\inetpub\wwwdjango\wbd`

Name: `WSGI_HANDLER`  
Value: `django.core.wsgi.get_wsgi_application()`

Name: `DJANGO_SETTINGS_MODULE`  
Value: `wbd.production_settings`

Now make sure the 'static' folder is configured correctly

In IIS, expand the 'wbd' node, and then click the 'static' subfolder.

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
    [http://localhost/wbd](http://localhost/wbd "http://localhost/wbd")

# Configure for external access

Now you should be able to view the web application from 
another computer after making 1 edit.

Django has a security feature that requires setting the HTTP name
of the server the application is running on.

Edit the file
    `C:\inetpub\wwwdjango\wbd\wbd\production_settings.py`

Find the line that looks like this

ALLOWED_HOSTS = ['localhost',]

and add the hostname that users will use to reach the application.

For example

ALLOWED_HOSTS = ['localhost', 'insdev1.tetratech.com',]

### Test external access via IIS

Now use a web-browser (on the web server) and visit  
    [https://insdev1.tetratech.com/wbd](https://insdev1.tetratech.com/wbd "https://insdev1.tetratech.com/wbd")


