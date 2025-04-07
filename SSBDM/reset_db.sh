#!/bin/bash
# Reset PostgreSQL database script for Linux/macOS
# This script drops and recreates the PostgreSQL database for SSBDM

echo -e "\e[32mResetting SSBDM PostgreSQL Database...\e[0m"

# Database connection parameters
DB_NAME="ssbdm"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Export password for psql commands
export PGPASSWORD=$DB_PASSWORD

# Drop the database if it exists
echo -e "\e[33mDropping existing database...\e[0m"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"

# Create a new database
echo -e "\e[33mCreating new database...\e[0m"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

# Run migrations
echo -e "\e[33mRunning migrations...\e[0m"
python manage.py migrate

# Create a superuser
echo -e "\e[36mWould you like to create a superuser? (y/n)\e[0m"
read create_superuser
if [[ "$create_superuser" =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Load initial data if available
echo -e "\e[36mWould you like to load initial data? (y/n)\e[0m"
read load_data
if [[ "$load_data" =~ ^[Yy]$ ]]; then
    # Check if fixtures directory exists
    if [ -d "fixtures" ]; then
        echo -e "\e[33mLoading initial data...\e[0m"
        for fixture in fixtures/*.json; do
            python manage.py loaddata "$fixture"
        done
    else
        echo -e "\e[33mNo fixtures directory found. Skipping data loading.\e[0m"
    fi
fi

echo -e "\e[32mDatabase reset completed successfully!\e[0m" 