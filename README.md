# null-auth-authentication

***Activate your virtual environment first***

### Migrations
Once the repo. is downloaded, run the following commands to create the tables of the models in your local database    
`python manage.py makemigrations` (Create migration files for the models)   
`python manage.py migrate` (Apply the created migration files in the db)
     
### Initial Data for the defined models
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
