# null-auth-authentication

***Activate your virtual environment first***

### Pre-requisite

#### Database set-up
We assume that you might be using the [MySQL](https://www.mysql.com/) in your local environment, if not, then you've to install it first before moving forward.    
once it's downloaded, run the MySQL service (the default port is 3306).    
    
In linux, to run the MySQL service,     
run the following command: `sudo systemctl start mysql` or check the command for your distro/O.S.    

After this, make necessary editions to the project's [settings.py](djangoauthapi1/settings.py)    
Add your mysql username and password here:    
```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'NullJobNEW',
        'USER': 'root', # your mysql username
        'PASSWORD': 'root', # your mysql password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
**NOTE**: Remember, the database which is mentioned as the value of key called "NAME" need to be exist (In this case it's NullJobNEW).    
You've two choices here, either to create this database manually or by using the python script.    

1. To create the database manually using MySQL interface    
Command: `CREATE DATABASE databasename`     

2. To create the database using the [python script](python_mysql_connector/py_mysql.py)
For example:     
```python
┌──[hi-man@blackHat ~/NullJobs/testing-file-upload/null-auth-authentication]
└──$ >> python -i python_mysql_connector/py_mysql.py 
>>> 
>>> dbconnection = MySQL(database="NullJob")
Wrong database information provided! Database=NullJob
Do you want to create a new database named NullJob [Y/N]: y
Database has been created!
>>> 
>>>
```

#### Install modules
Install all the required modules mentioned in the requirements.txt    
Command: `python -m pip install -r requirements.txt`

    
#### Migration Commands
Once the database is set-up and you have downloaded the repo, run the following commands to create the tables of the models in your local database    
`python manage.py makemigrations` (Create migration files for the models)   
`python manage.py migrate` (Apply the created migration files in the db)

     
#### Initial Data for the defined models

Location: `seedFiles/`    
This directory contains the initial data for the defined models in Jobapp/models.py

Currently we have three modles defined:    
1. Company
2. Job
3. User

In order to import this data into the database, run this following command    
Command: `python manage.py loaddata filename.json`

In our case, files are present in the seedFiles/ directory,    
For example: `python manage.py loaddata seedFiles/company.json`

---
    
### Jobapp API

APIs related code is present in Jobapp/    
APIs avialable:    

1. Company: ***/api/v1/company***   
    Filters: name, location

   Actions avialable:    
    * `/api/v1/company/{company_id}` : Show details of a specific job    
    * `/api/v1/company/jobs` : Show number of jobs available in N number of companies    
    * `/api/v1/company/users` : Show number of users available in N number of companies       
    
2. Jobs ***/api/v1/jobs***    
    Filters: company, location    
    
    Actions avialable:    
    * `/api/v1/jobs/{job_id}` : Show details of a specific job     
    * `/api/v1/jobs/{job_id}/users` : Show users applied for a specific job    
    
    
3. User ***/api/v1/user***    
    Filters: NA    
    
    Actions available:    
    * `/api/v1/user/{user_id}` : Show details of a specific user    
    * `/api/v1/user/{user_id}/jobs` : Show number of jobs applied by a specific user    
