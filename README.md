<del>TallyUp (formerly known as HackDo)</del> HackDo
----------------------------------

<del>TallyUp</del> HackDo is meant to be a membership (and others) management system for Hackerspaces.

Keeping track of membership is a chore that takes time and can end up quite messy, so let's try and solve that pain point.

Most of the magic goes on in the Admin console (have a look in `hado/admin.py`).

Setup
-----

1. Create a virtualenv (install the package if you haven't already), eg. `dev`

       `$ virtualenv --no-site-packages dev`

2. Grab the source code, and stick it in the virtualenv created above

       `$ cd dev`  
       `$ git clone git://github.com/hackerspacesg/hackdo.git`

3. Grab other dependencies, and install them in the virtualenv

       `$ cd ..`  
       `$ pip install -r hackdo/scripts/requirements.txt`
     
4. Set up django's tables and migrations:

       `$ ./manage.py syncdb`  
       `$ ./manage.py migrate --all`

Links
-----

  - [bug tracker](https://www.pivotaltracker.com/projects/155751)
  - [wiki](http://hackerspacesg.pbworks.com/w/page/33279936/Project:-HackDo)
