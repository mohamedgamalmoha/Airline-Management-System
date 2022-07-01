# Airline-Management-System
API end points for CRUD operations  
## The following requirements are specified 
- Function generate_1d_matrix
- Take min and max values of x from the user.
- The following operators is supported: + - / * ^.- 
- The GUI is simple and beautiful (well organized).

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
