# SSBDM Database Restructuring

This document outlines the changes made to the database structure in the SSBDM application to improve data integrity, performance, and flexibility.

## Major Changes

1. **UUID Primary Keys**: All models now use UUIDs (Universally Unique Identifiers) as primary keys instead of auto-incrementing integers. This provides:
   - Better security (IDs are not guessable)
   - Easier merging of data from different sources
   - Avoidance of ID conflicts in distributed systems

2. **Consistent Field Naming**: Field names are now consistent across models:
   - Standard timestamps: `created_at`, `updated_at`
   - Standard user tracking: `created_by`, `updated_by`
   - Common field names across models (e.g., `code` instead of `part_number`)

3. **Improved Relationships**: The relationship between equipment, spare parts, and documents is now explicitly tracked using:
   - `BOMRelationship` model for defining theoretical relationships
   - `EquipmentSparePartUsage` model for tracking actual installations and replacements

4. **Database Indexes**: Strategic indexes have been added to improve query performance on frequently searched fields.

5. **Metadata Fields**: All models now include comprehensive metadata for better tracking:
   - Creation and update timestamps
   - User tracking for audit trails
   - Additional descriptive fields

6. **Centralized Bill of Materials**: The SSBOM feature now serves as the central source of truth for equipment structure, with support for:
   - Equipment hierarchies (parent-child relationships)
   - Equipment-spare part relationships with quantification
   - Equipment-document relationships with proper categorization

## Migration Path

To migrate from the old structure to the new structure, follow these steps:

1. **Backup your data**: Always create a full backup before major database changes
```
python manage.py dumpdata > db_backup.json
```

2. **Configure database connection**: Update `settings.py` to use your preferred database (SQLite or PostgreSQL)

3. **Create migrations**: Generate migrations for the new model structure
```
python manage.py makemigrations
```

4. **Apply migrations**: Apply the migrations to create the new structure
```
python manage.py migrate
```

5. **Run data migration script**: Migrate your existing data to the new structure
```
python data_migration.py
```

6. **Verify data integrity**: Confirm that all data has been correctly migrated

## New Models and Fields

### Equipment Models

- `Area`: Now uses MPTT for better hierarchy handling and includes a UUID primary key
- `Equipment`: Added fields for financial tracking, criticality, and maintenance scheduling
- `TechnicalSpecification`: Enhanced with better metadata tracking

### Spare Parts Models

- `Category`: Now uses MPTT and includes code field for better referencing
- `SparePart`: Renamed fields for consistency and added financial/supplier tracking
- `SparePartTransaction`: Enhanced to track equipment usage and financial impact

### Document Models

- `DocumentCategory`: Added code field and improved categorization
- `EquipmentDocument`: Added fields for document tracking, revision control, and expiration

### SSBOM Models

- `BOMRelationship`: Central model connecting equipment, spare parts, and documents
- `EquipmentSparePartUsage`: Tracks actual usage/installation history of spare parts
- `BOMChangeLog`: Audit trail for relationship changes
- `EquipmentHierarchy`: Materialized view for efficient hierarchy querying

## Database Diagram

For a visual representation of the new database structure, refer to the entity-relationship diagram in the documentation folder.

## Benefits of the New Structure

1. **Better Data Integrity**: Proper constraints and validation ensure data consistency
2. **Improved Performance**: Strategic indexes and materialized views speed up common queries
3. **Enhanced Tracking**: Comprehensive audit trails and historical data
4. **Better Relationship Modeling**: Explicit relationships with additional metadata
5. **Future Extensibility**: Structure designed to accommodate future features
6. **Support for Complex Hierarchies**: Better equipment and component hierarchies 