paleocore
==================

Paleo Core Project

Install Dependencies
--------------------
* Python > 3.8. On mac the easiest way to install python is with [homebrew](https://brew.sh/)
* PostgreSQL > 10. On mac the easiest way is to install [postgres.app](https://postgresapp.com/)

Installation
------------------
* Clone repository from GitHub and move into that directory
```
git clone https://github.com/paleocore/paleocore-lite.git
cd paleocore-ligt
```

* Create virtual Python environment
```
virtualenv -p python3 venv
```

* Start the virtual environment and install the python libraries stipulated in the requirements file. Separate files stipulate a base set of libraries which are imported into dev and production requirement files.
```
source venv/bin/activate
pip install -r requirements/dev.txt
```

* Create the database. Assuming the database software is installed. The default database for this project uses postgreSQL. The simplest method of implementing the database is using postgres.app.
```
createdb paleocorelite
```

* Run migrations.
```
python manage.py migrate
```

Run Server
--------------------
* Start virtual environment.

* Create superuser.
```
python manage.py createsuperuser
```

* Run server on local host.
```
python manage.py runserver localhost:8000
```

* Open [localhost:8000/django-admin](http://localhost:8000/django-admin) in a web browswer.

