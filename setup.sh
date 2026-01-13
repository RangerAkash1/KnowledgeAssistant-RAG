#!/bin/bash

echo "======================================"
echo "Knowledge Assistant RAG - Setup"
echo "======================================"

echo ""
echo "Step 1: Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 4: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your API keys and settings"
else
    echo ".env file already exists"
fi

echo ""
echo "Step 5: Running migrations..."
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Failed to run migrations"
    exit 1
fi

echo ""
echo "Step 6: Creating directories..."
mkdir -p data/vector_store
mkdir -p media

echo ""
echo "======================================"
echo "Setup completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Run server: python manage.py runserver"
echo ""
