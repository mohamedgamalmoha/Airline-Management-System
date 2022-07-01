# Airline-Management-System
API end points for CRUD operations  
A flight management system that allows airlines to manage their system

## The following requirements are specified 
- Advertise flights and customers choose Airline Companies 
- REST API Interface
- Business Logics Layer
- Database The system will include a database

## How to run the program correctly 
- Install python (in case it was not installed) 
- Install the requirements  
    ```
    pip install -r requirements.txt
    ```
- Migrate Database
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```
- Run custom commands for creating default superuser & uploading dummy data:
    ```
    python manage.py default_superuser
    python manage.py upload_data
    ```
- Run the server
    ```
    python manage.py runserver
    ```
