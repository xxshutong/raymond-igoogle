StockTrenz
==========================

THE STACK
---------
* Django application
* Runs on heroku cedar stack
* Backed by Postgresql database

PREREQUISITE
------------
These instructions are for Mac OSX 10.7 only. sudo where necessary.

* Install HomeBrew

    > /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"

* Install Git

    > brew install git

* Install Postgresql

    > brew install postgresql

    > initdb /usr/local/var/postgres

    > mkdir -p ~/Library/LaunchAgents

    > cp /usr/local/Cellar/postgresql/9.1.1/org.postgresql.postgres.plist ~/Library/LaunchAgents/

    > launchctl load -w ~/Library/LaunchAgents/org.postgresql.postgres.plist

    > createdb stocktrenz


* Local Memcache Setup

    > brew install memcached

* Install libmemcached for python

    > wget https://launchpad.net/libmemcached/1.0/1.0.4/+download/libmemcached-1.0.4.tar.gz

    > tar zxvf libmemcached-1.0.4.tar.gz

    > cd libmemcached-1.0.4

    > ./configure

    > make

    > sudo make install


* gem install heroku
* gem install foreman
* python


QUICK START
-----------

1. git clone <see repo url>
1. cd stocktrenz
1. ./setup.sh # if you have issues with lxml, talk to Shawn
1. source .ve/bin/activate
1. createdb stocktrenz
1. createuser -P -e stocktrenz # enter "stocktrenz" as password
1. python webcontent/manage.py syncdb
1. python webcontent/manage.py migrate
1. To start the server, you must run it from within the stocktrenz directory.
    Otherwise the TEMPLATE_DIR will not be found. This is to stay consistent
    with how it'd run within Heroku which puts the app in different directory.

        > foreman start

        or

        > python webcontent/manage.py runserver

**Note:** Default user name and password are admin/asdf

KEY LINKS
---------
* Learn about [Django on Heroku](http://devcenter.heroku.com/articles/django)
* Developerment API: http://localhost.xplusz.com:8000/api/v1/?format=json
** *Note** that port might be different check logs
* (todo) Admin portal: http://localhost.xplusz.com:8000/admin
** *Note** that port might be different check logs
* QA/Integration box: http://storypanda-xplusz-qa.herokuapp.com/api/v1/?format=json


DEPLOYMENT
----------

### Automatic Pipeline

1. Push your changes to github's master branch
1. This will automatically trigger the jekins project for functional and unit tests
1. If the func/unit test pass, then the build is automatically pushed to QA/Integration
1. Load tests are then run against the QA/Integration environment

### Manual Pushing to QA/Loadtest

* Make sure you have access to the heroku app.
* Add the heroku remote:

    > git remote add heroku <heroku git url>

* Push your code up:

    > git push heroku master

* Run migrations:

    > heroku run python webcontent/manage.py syncdb

    > heroku run python webcontent/manage.py migrate

* View your app:

    > heroku open

### Manual Pushing To Production

* *BE CAREFUL*
* Make sure you have access to the production heroku app.
* Add the heroku remote:

    > git remote add heroku-prod <heroku git url>

* Tag the release: "production-<DATE>-<RELEASE#>" where DATE is YYYY-MM-DD and RELEASE# is the 2 digit (XX) number for the release of the day, starting at 01.

    > git tag production-2012-03-20-01   # First release of March 20th, 2012

* Push your tag:

    > git push --tags origin

* Push your code up:

    > git push heroku-prod master

* Run migrations:

    > heroku run --app stocktrenz python webcontent/manage.py migrate

* View your app:

    > heroku open --app stocktrenz

* Inform QA to do a manual pass of production.

DEVELOPMENT
-----------

* Put development environment tools, like ipython, in dev_requirements.txt
* We need to keep the slug size for Heroku small
* Also, vim is the best dev tool there is.
