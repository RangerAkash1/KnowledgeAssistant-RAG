@echo off
echo ======================================
echo Knowledge Assistant RAG - Setup
echo ======================================

echo.
echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    exit /b 1
)

echo.
echo Step 4: Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your API keys and settings
) else (
    echo .env file already exists
)

echo.
echo Step 5: Running migrations...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo Failed to run migrations
    exit /b 1
)

echo.
echo Step 6: Creating directories...
if not exist "data\vector_store" mkdir data\vector_store
if not exist "media" mkdir media

echo.
echo ======================================
echo Setup completed successfully!
echo ======================================
echo.
echo Next steps:
echo 1. Edit .env file with your OpenAI API key
echo 2. Create superuser: python manage.py createsuperuser
echo 3. Run server: python manage.py runserver
echo.

pause
