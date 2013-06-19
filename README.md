HackDo
----------------------------------

[![Build Status](https://travis-ci.org/wgx731/hackdo.png?branch=dev)](https://travis-ci.org/wgx731/hackdo)

HackDo is meant to be a membership (and others) management system for Hackerspaces.

Keeping track of membership is a chore that takes time and can end up quite messy, so let's try and solve that pain point.

Most of the magic goes on in the Admin console (have a look in `hado/admin.py`).

Setup
-----

1. Create a virtualenv (install the package if you haven't already), eg. `dev`:

        $ virtualenv --no-site-packages dev
        $ . dev/bin/activate

2. Grab the source code, and stick it in the virtualenv created above:

        (dev)$ cd dev
        (dev)$ git clone git://github.com/hackerspacesg/hackdo.git

3. Grab and install other dependencies in the virtualenv:

        (dev)$ cd hackdo
        (dev)$ pip install -r scripts/requirements.txt

4. Set up django's tables and migrations:

        (dev)$ ./manage.py syncdb
        (dev)$ ./manage.py migrate --all

Links
-----

  - [bug tracker](https://www.pivotaltracker.com/projects/155751)
  - [wiki](http://hackerspacesg.pbworks.com/w/page/33279936/Project:-HackDo)
