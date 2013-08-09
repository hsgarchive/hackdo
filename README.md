HackDo
----------------------------------

[![Build Status](https://travis-ci.org/wgx731/hackdo.png?branch=dev)](https://travis-ci.org/wgx731/hackdo)
[![Build Status](https://drone.io/github.com/wgx731/hackdo/status.png)](https://drone.io/github.com/wgx731/hackdo/latest)

HackDo is meant to be a membership (and others) management system for Hackerspaces.

Keeping track of membership is a chore that takes time and can end up quite messy, so let's try and solve that pain point.

Most of the magic goes on in the Admin console (have a look in `hado/admin.py`).

Setup
-----

1. Create a virtualenv (install the package if you haven't already), eg. `dev`:

        $ virtualenv --no-site-packages dev
        $ . dev/bin/activate

2. Grab the source code (not compulsory to stick it in the virtualenv created above):

        (dev)$ cd (where you want to put the code)
        (dev)$ git clone git://github.com/hackerspacesg/hackdo.git

3. Grab and install other dependencies in the virtualenv:

        (dev)$ cd (where you put the code)
        (dev)$ pip install -r requirements.txt

4. Set up django's tables and migrations:

        (dev)$ mysql -u (your user) -p < scripts/hackdo.sql (NOTE: only run this script if you want to create a new clean database, before run the script remember to change password for hackdo user)
        (dev)$ python manage.py syncdb
        (dev)$ python manage.py migrate

5. Set up local settings:

        (dev)$ cp _local_settings.py local_settings.py (change the settings according to instructions inside)


Links
-----

  - [bug tracker](https://www.pivotaltracker.com/projects/155751)
  - [wiki](http://hackerspacesg.pbworks.com/w/page/33279936/Project:-HackDo)
