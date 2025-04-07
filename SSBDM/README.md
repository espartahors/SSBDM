# SSBDM - Steel Structure Business Data Management

A comprehensive system for managing maintenance operations in steel structures, including equipment tracking, maintenance logging, document management, and spare parts inventory.

## Features

- **Equipment Management**: Track equipment details, technical specifications, hierarchical components, and maintenance history.
- **Maintenance Module**: Schedule, document, and track maintenance activities with detailed logs.
- **Document Management**: Store and organize important documents related to equipment and maintenance.
- **Spare Parts Inventory**: Track spare parts stock, suppliers, and usage history.
- **Area Management**: Organize equipment by physical location using a hierarchical structure.
- **User Management**: Control access with role-based permissions and track user activities.
- **Reporting**: Generate and export maintenance reports and equipment status summaries.

## Technical Stack

- **Framework**: Django 4.2.x
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Font Awesome, jQuery
- **Additional libraries**: django-mptt, django-filter, Pillow, django-crispy-forms

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip
- virtualenv (recommended)

### Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd SSBDM
   ```

2. **Create and activate a virtual environment**:
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL**:
   - Make sure PostgreSQL is running
   - Create a database named `ssbdm`
   - Update database credentials in `SSBDM/settings.py` if needed

5. **Reset the database** (use the provided scripts):
   ```
   # Windows
   .\reset_db.ps1
   
   # Linux/macOS
   chmod +x reset_db.sh
   ./reset_db.sh
   ```

6. **Run the development server**:
   ```
   python manage.py runserver
   ```

7. **Access the application**:
   Open your browser and navigate to `http://127.0.0.1:8000`

## Project Structure

- **equipment**: App for managing equipment, areas, and technical specifications
- **maintenance**: App for maintenance logs, tasks, and reports
- **documents**: App for document management
- **spare_parts**: App for spare parts inventory
- **security**: App for user management and permissions

## User Roles

- **Administrators**: Full access to all system functions
- **Maintenance Managers**: Manage maintenance schedules and assign tasks
- **Technicians**: Record maintenance activities and update equipment status
- **Inventory Managers**: Manage spare parts inventory
- **Viewers**: Read-only access to equipment and maintenance information

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name - Initial work 