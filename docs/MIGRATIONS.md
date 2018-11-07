## Database Migrations

### Steps:

1. Create migration repository 	
```bash
$ python manage.py db init
```
2. Generate initial migration	
```bash
$ python manage.py db migrate
```
3. Apply migrations to the database
```bash
$ python manage.py db upgrade
```
4. Create function and trigger in db
```bash
$ python manage.py DbTrigger 
```
5. Create view in db for search
```bash
$ python manage.py CreateView
```
5. Seed data in db
```bash
$ python manage.py Seed
```
**Note:** After making changes in the schema only run step 2 and 3.
