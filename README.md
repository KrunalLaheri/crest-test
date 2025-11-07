# Product Management API

## Prerequisites

- Python 3.12 or higher
- Poetry (Python dependency management tool)
- Git

## Installation & Setup

### 1. Clone the Repository


git clone <repository-url>
cd crest-test


### 2. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip

pip install poetry


### 3. Install Dependencies
poetry install


This will create a virtual environment and install all required dependencies.

### 4. Environment Configuration

Create a `.env` file in the project root:


cp .env.example .env


Edit `.env` and update the values as needed:

env
SECRET_KEY=your-secure-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=db.sqlite3
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440


### 5. Run Migrations
poetry run python manage.py migrate


### 6. Create Superuser
poetry run python manage.py createsuperuser


Follow the prompts to create an admin account.

### 7. Create Required Directories
mkdir -p media/products logs


## Running the Server
### Development Server


poetry run python manage.py runserver


The API will be available at `http://127.0.0.1:8000/`

### Alternative: Activate Virtual Environment


poetry shell
python manage.py runserver