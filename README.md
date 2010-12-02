TallyUp (formerly known as HackDo)
----------------------------------

TallyUp is meant to be a membership (and others) management system for Hackerspaces.

Keeping track of membership is a chore that takes time and can end up quite messy, so let's try and solve that pain point.

Most of the magic goes on in the Admin console (have a look in `hado/admin.py`).

Setup
-----

1. Grab the source code:

       $ git clone git://github.com/hackerspacesg/TallyUp.git

1. Since django has [a git mirror here](http://github.com/django/django), we can
   track it too. Checkout the django source we're running against:

       $ git submodule init
       $ git submodule update
  
   Note: if you already have a local checkout of the django's git mirror, pass
   it to `submodule update` via `--reference`. (RTM)
  
1. Grab other dependencies:

       $ pip install -r src/requirements.txt
     
1. Set up django's tables and migrations:

       $ ./manage.py syncdb
       $ ./manage.py migrate --all

!TODO use sqlite3 for easy testing

Links
-----

  - [bug tracker](https://www.pivotaltracker.com/projects/155751)
  - [wiki](http://hackerspacesg.pbworks.com/w/page/33279936/Project:-HackDo)
