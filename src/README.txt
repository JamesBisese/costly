

--- update process

Updating COR web server

The update requires logging onto a 'virtual desktop' tool and then using 
Remote Desktop Connection (RDC) to connect to the web server.

I use the virtual desktop in a web browser

https://vdi.raleighnc.gov

That prompts me for a username and password, and requires a 2-factor authorization 
from my phone using the 'DUO' app.

Once I login to the virtual desktop, I can use RDC to connect to the web server

GSITOOLWV1

I can also use Edge from here to get to the webserver on COR network

	https://gsicosttool.raleighnc.gov/

The root of the GIT repository is at

C:\inetpub\wwwdjango\gsicosttool

The web application is being served from folder

	C:\inetpub\wwwdjango\gsicosttool\src

The python virtual env for the web application is in folder

	C:\software\Python\virtualenvs\gsicosttool

There is also a folder for shared files and things I copy/remove from the webserver 
during updates to prevent overwriting modified files or save the output from 'dumpdata'

	C:\Data_and_Tools\gsicosttool

Once logged in, I usually will open a command prompt as administrator and the 'activate' 
it so that I am ready to use python and Django commands

Microsoft Windows [Version 10.0.19042.1526]
(c) Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>C:\software\Python\virtualenvs\gsicosttool\Scripts\activate 

(gsicosttool) C:\WINDOWS\system32>cd C:\inetpub\wwwdjango\gsicosttool\src     

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool\src>  

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool\src>cd ..

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>git status

On branch master

Your branch is up to date with 'origin/master'.
Changes not staged for commit:
(use "git add/rm <file>..." to update what will be committed)
(use "git restore <file>..." to discard changes in working directory)
modified:   src/authtools/migrations/0001_initial.py
modified:   src/gsicosttool/settings/production.py
modified:   src/manage.py
modified:   src/requirements.txt
modified:   src/scenario/migrations/0001_initial.py
deleted:    src/scenario/migrations/0002_auto_20220110_1126.py
no changes added to commit (use "git add" and/or "git commit -a")

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>copy src\manage.py C:\Data_and_Tool\gsicosttool\working\edit_files\2022-03-09\.
1 file(s) copied.

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>copy src\requirements.txt C:\Data_and_Tool\gsicosttool\working\edit_files\2022-03-09\.
1 file(s) copied.
																												   
(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>git restore src\manage.py

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>git restore src\requirements.txt

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>copy src\gsicosttool\settings\production.py C:\Data_and_Tool\gsicosttool\working\edit_files\2022-03-09\.
1 file(s) copied.

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>git restore src\gsicosttool\settings\production.py

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>git pull  
                                                               
remote: Enumerating objects: 68, done.                                                                                  
remote: Counting objects: 100% (68/68), done.                                                                           
remote: Compressing objects: 100% (7/7), done.                                                                          
remote: Total 35 (delta 27), reused 35 (delta 27), pack-reused 0                                                        
Unpacking objects: 100% (35/35), 7.01 KiB | 40.00 KiB/s, done.                                                          
From https://github.com/JamesBisese/gsicosttool                                                                            
1131cd5..9c31401  master     -> origin/master                                                                        
Updating 1131cd5..9c31401                                                                                               
Fast-forward                                                                                                             
src/gsicosttool/settings/base.py                   | 116 +++++++++++---------                                           
src/gsicosttool/settings/development.py            | 106 ++++++++----------                                             
.../settings/local.development.sample.env          |  19 +---                                                           
.../settings/local.production.sample.env           |  17 +--                                                            
src/gsicosttool/settings/production.py             | 122 ++++++++++++++++-----                                          
src/gsicosttool/templates/gsicosttool/why.html     |   2 +-                                                             
src/profiles/templates/profiles/edit_profile.html  |   7 +-                                                             
src/profiles/templates/profiles/show_profile.html  |   3 -                                                              
src/requirements.txt                               |   3 +-                                                             
src/scenario/static/scenario/js/displaycontrols.js |  69 ------------                                                   
src/scenario/static/scenario/js/results_compare.js |  82 ++++++++++++++                                                 
src/scenario/tests/test_selenium.py                |  52 ++++++---                                                      
src/scenario/tests/test_settings.py                |  67 +++++++++++                                                    
src/scenario/views/index.py                        |  62 +++++------                                                    
src/templates/_navbar-right.html                   |   2 -                                                              
src/templates/_navbar.html                         |   8 +-                                                             
src/templates/base.html                            |   3 +-                                                             
src/templates/pre-base.html                        |   2 +-                                                             
18 files changed, 440 insertions(+), 302 deletions(-)                                                                   
create mode 100644 src/scenario/tests/test_settings.py

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool>cd src

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool\src>python manage.py collectstatic

You have requested to collect static files at the destination
location as specified in your settings:
C:\inetpub\wwwdjango\gsicosttool\src\static
This will overwrite existing files!
Are you sure you want to do this?
Type 'yes' to continue, or 'no' to cancel: yes

# ..... lots of output

2 static files copied to 'C:\inetpub\wwwdjango\gsicosttool\src\static', 326 unmodified.

(gsicosttool) C:\inetpub\wwwdjango\gsicosttool\src>

# now make any changes to the local.production.env file (like change the release number and date)

# then restart the IIS server to pick up the changes