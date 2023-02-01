## Install the dependencies:

$ pip install -r requirements.txt

## Run migrations:

$ python manage.py migrate



## Create the superuser:

$ python manage.py createsuperuser

## Run the server

$ python manage.py runserver


## Run the tests

$ python manage.py test d0010

## Import a file:

$ python manage.py import.py <filename>


## Display the results:

Visit http://localhost:<port>/admin/d0010/registerreading/ to see the imported data.


## Comments

Assumptions:

- I assume each file will be imported just one time. In case somebody needs to overwrite the data, they will have to remove the entities manually, for example through the admin panel. Otherwise Integrity Errors will occur.


Potentials improvements:

- increase test coverage (account for parsing errors etc)
- extract data from header/footer
- figure out if I need update_or_create for some entities (can validation status change?)
