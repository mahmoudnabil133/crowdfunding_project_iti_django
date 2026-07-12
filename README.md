# Crowdfunding Console App

A Django-based console application for creating and managing crowdfunding campaigns. Users can register, log in, create fundraising projects, and manage them through an interactive terminal interface.

## Features

### Authentication
- User registration with first name, last name, email, password, and Egyptian mobile phone validation
- Login with email and password
- Password confirmation check during registration

### Projects
- Create fundraising campaigns with title, details, target amount, and date range
- View all projects
- Edit your own projects (partial updates — leave blank to keep current value)
- Delete your own projects (with confirmation)
- Search projects by date range

## Requirements

- Python 3.14+
- Django 6.0.7

## Setup

```bash
# Clone the project
cd crowdfunding_project

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the app
python manage.py run
```

## Usage

The app runs entirely in the terminal via `python manage.py run`.

### Main Menu
1. **Register** — Create a new account
2. **Login** — Sign in with email and password

### User Menu (after login)
1. **Create Project** — Start a new fundraising campaign
2. **View All Projects** — Browse all campaigns
3. **Edit My Projects** — Update your own campaign details
4. **Delete My Project** — Remove one of your campaigns
5. **Search Projects by Date** — Filter campaigns by start/end date range
6. **Logout** — Sign out

### Project Fields
| Field | Description |
|---|---|
| Title | Campaign name |
| Details | Description of the project |
| Total target | Fundraising goal in EGP |
| Start date | Campaign launch date/time |
| End date | Campaign closing date/time |

### Validation
- Egyptian phone numbers: `01[0-25]xxxxxxxx` (11 digits)
- Target must be a positive amount
- Start date must be in the future
- End date must be after start date
- Duplicate emails and phone numbers are rejected

## Project Structure

```
crowdfunding_project/
├── crowdfunding/              # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                      # Main application
│   ├── models.py              # User and Project models
│   ├── admin.py               # Admin panel registration
│   └── management/commands/
│       └── run.py             # Console app entry point
├── requirements.txt
└── manage.py
```

## Models

### User (extends `AbstractUser`)
| Field | Type |
|---|---|
| email | EmailField (used as username) |
| mobile_phone | CharField(11), unique, Egyptian phone validated |
| first_name, last_name | CharField |
| password | Hashed password |

### Project
| Field | Type |
|---|---|
| user | ForeignKey to User |
| title | CharField(255) |
| details | TextField |
| total_target | DecimalField(12, 2) |
| start_date | DateTimeField |
| end_date | DateTimeField |
| created_at | DateTimeField (auto) |

## Admin Panel

Access the Django admin at `/admin/` with a superuser account:

```bash
python manage.py createsuperuser
python manage.py runserver
```
