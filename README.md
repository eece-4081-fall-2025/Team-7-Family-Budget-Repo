# Family Budgeting Tool (Team 7)

A Django-based web application that allows users to manage their personal and family budgets collaboratively. Each user can create an account, join or create a family group, edit their income and expenses, and view aggregated data for their group members.
This project follows modern CRUD fundamentals, Test-Driven Development (TDD) practices, and applies principles inspired by Arjan Codes’ functional programming techniques and avoidance of common OOP anti-patterns.

## Features 
Authentication  
User registration   
Login and logout system  
Redirect control for authenticated users  
Secure session management  

### User Profiles

Each user has a unique profile linked via one-to-one relationship  
Editable income and expense values  
Simple, intuitive profile editor with form validation

### Family Groups

Users can create or join a family group using a unique group code  
Only one active family group per user  
Group creator automatically becomes the admin  
Group members can view all other members’ income and expenses  
Clear role display (Admin / Member)  

### Dashboard

Personalized dashboard after login
Quick access to profile, family group, and logout options

## Testing

Comprehensive unit tests for authentication, signup, profile management, and group logic  
Tests validate all CRUD operations and access restrictions  

## Tech Stack
| Category | Technology  |  
| :-: | :-: |
|Framework	| Django 5.2  |
|Language	| Python 3.11  |
|Database	| SQLite (default, easily swappable for PostgreSQL)|  
|Frontend	| HTML, CSS, Django Templates |
|Authentication	| Django built-in Auth |
|Testing | Django TestCase Framework |  


## Running Tests

To run all tests:  
py manage.py test


## Setup Instructions
### Clone the repository

git clone [https://github.com/<your-username>   Team_7_repo_family_budgeting_tool.git  ](https://github.com/eece-4081-fall-2025/Team_7_repo_family_budgeting_tool.git)  
cd Team_7_repo_family_budgeting_tool  

### Create and activate virtual environment  
python -m venv venv
venv\Scripts\activate


### Install dependencies  
pip install -r requirements.txt  
### Run migrations
py manage.py makemigrations 
select this option 2) Ignore for now. Existing rows that contain NULL values will have to be handled manually, for example with a RunPython or RunSQL operation.
py manage.py migrate


### Start the development server
py manage.py runserver   


###  Access the app
Visit: http://127.0.0.1:8000/    

## Usage Overview

### Create Account

Navigate to /signup/  
Fill in your username and password

### Log In

Visit /accounts/login/  
Redirects to your dashboard

### Edit Profile

Go to “Edit Profile” from the dashboard  
Enter income and expenses

### Create or Join a Family Group

/group/create/ to start a new family group (generates a unique code)  
/group/join/ to join an existing group using its code  
You can only belong to one group at a time  

### View Family Members

/group/members/ displays all group members, their roles, and financial data formatted with dollar signs and commas.  

### Future Enhancements

Add budgeting analytics and chart visualizations  
Enable expense categorization and monthly summaries  
Integrate with APIs for exchange rates or savings goals  
Implement lazy loading for large family groups  


## Contributors
### Team 7 – University of Memphis EECE Department  
Drake Watters   
Brian Dunn  
Benjamin Borwick  
Gabriel Malone  
