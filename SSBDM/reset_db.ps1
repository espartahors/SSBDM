# Reset PostgreSQL database script for Windows PowerShell
# This script drops and recreates the PostgreSQL database for SSBDM

Write-Host "Resetting SSBDM PostgreSQL Database..." -ForegroundColor Green

# Database connection parameters
$DB_NAME = "ssbdm_db"
$DB_USER = "postgres"
$DB_PASSWORD = "ibaali3303"
$DB_HOST = "localhost"
$DB_PORT = "5432"

try {
    # Drop the database if it exists
    Write-Host "Dropping existing database..." -ForegroundColor Yellow
    $dropCommand = "DROP DATABASE IF EXISTS $DB_NAME;"
    $env:PGPASSWORD = $DB_PASSWORD
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c $dropCommand postgres
    
    # Create a new database
    Write-Host "Creating new database..." -ForegroundColor Yellow
    $createCommand = "CREATE DATABASE $DB_NAME;"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c $createCommand postgres
    
    # Run migrations
    Write-Host "Running migrations..." -ForegroundColor Yellow
    python manage.py migrate

    # Create a superuser
    Write-Host "Would you like to create a superuser? (Y/N)" -ForegroundColor Cyan
    $createSuperuser = Read-Host
    if ($createSuperuser -eq "Y" -or $createSuperuser -eq "y") {
        python manage.py createsuperuser
    }

    # Load initial data if available
    Write-Host "Would you like to load initial data? (Y/N)" -ForegroundColor Cyan
    $loadData = Read-Host
    if ($loadData -eq "Y" -or $loadData -eq "y") {
        # Check if fixtures directory exists
        if (Test-Path -Path "fixtures") {
            Write-Host "Loading initial data..." -ForegroundColor Yellow
            Get-ChildItem -Path "fixtures" -Filter "*.json" | ForEach-Object {
                python manage.py loaddata $_.FullName
            }
        } else {
            Write-Host "No fixtures directory found. Skipping data loading." -ForegroundColor Yellow
        }
    }

    Write-Host "Database reset completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "Database reset failed!" -ForegroundColor Red
    exit 1
} 