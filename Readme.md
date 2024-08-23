# Social Network - Django Project

## Setup Guide

1. **Create Database**  
   Create a database named `social_network`.

2. **Configure Database**  
   Update the database credentials in `social_network/settings.py`.

3. **Initialize Database**  
   Run the SQL script `sql/tables.sql` to set up the tables.

4. **Set Up Virtual Environment**  
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

5. **Install Dependencies**  
    ```bash
    pip install -r requirements.txt
   ```

6. Run the Server
    ```bash
    python3 manage.py runserver
   ```
