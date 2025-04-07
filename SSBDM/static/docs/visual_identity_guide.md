# SSBDM Visual Identity Guide

## Introduction

This document outlines the visual identity standards for the Steel Manufacturing Breakdown and Maintenance (SSBDM) system. Adherence to these guidelines ensures a consistent, professional, and user-friendly experience across all aspects of the application.

## Brand Elements

### Logo

The SomaSteel logo is the primary branding element of the SSBDM system. It should be displayed prominently in the navigation header and in the loading screen.

- **Primary Logo**: Full color version for headers and primary branding areas
- **Monochrome Logo**: For footer and secondary placements
- **Icon-only Logo**: For favicon and small space constraints

The logo should always maintain its proportions and be surrounded by adequate white space (minimum clear space equal to the height of the "S" in the logo).

### Color Palette

#### Primary Colors

- **Primary Blue** (#0056b3): Used for primary actions, links, and key UI elements
- **Primary Light Blue** (#3478c9): Used for hover states and secondary elements
- **Primary Dark Blue** (#003b7a): Used for active states and emphasis

#### Secondary Colors

- **Secondary Gold** (#f0a30a): Used for call-to-action buttons, highlights, and notifications
- **Secondary Light Gold** (#ffb938): Used for hover states of secondary elements
- **Secondary Dark Gold** (#cc8800): Used for active states of secondary elements

#### Neutral Colors

- White (#ffffff): Primary background color
- Light Gray (#f8f9fa): Secondary background color
- Medium Gray (#6c757d): Text for secondary information
- Dark Gray (#343a40): Primary text color
- Black (#212529): Headers and emphasized text

#### Status Colors

- Success Green (#28a745): Operational status, successful actions
- Warning Yellow (#ffc107): Maintenance status, warnings, low stock
- Danger Red (#dc3545): Out of service status, errors, critical notifications
- Info Blue (#17a2b8): Informational messages and notifications

### Typography

#### Font Families

- **Primary Font**: Roboto (weights: 300, 400, 500, 700)
  - Used for all main content, navigation, and UI elements
  
- **Secondary Font**: Open Sans (weights: 400, 600, 700)
  - Used for headings and emphasized text
  
- **Monospace Font**: Roboto Mono
  - Used for code, technical specifications, and numeric data where monospaced formatting is beneficial

#### Font Sizes

- Base font size: 16px (1rem)
- Headings:
  - H1: 2.5rem
  - H2: 2rem
  - H3: 1.75rem
  - H4: 1.5rem
  - H5: 1.25rem
  - H6: 1rem (bold)
- Small text: 0.875rem
- Micro text: 0.75rem

### Iconography

The SSBDM system uses Font Awesome icons throughout the interface for consistent visual cues. Icons should be used to enhance usability, not replace text (except in space-constrained areas like mobile views).

Key icon usages:
- Navigation sections (dashboard, equipment, maintenance, etc.)
- Action buttons (edit, delete, view, etc.)
- Status indicators (operational, maintenance, out of service)
- Notifications and alerts

## Components

### Navigation

The main navigation is a horizontal navbar at the top of the screen, with dropdown menus for sub-sections. On mobile devices, it collapses into a standard mobile menu accessible via a hamburger icon.

- Background: White (#ffffff)
- Text color: Dark Gray (#343a40)
- Active item: Primary Blue (#0056b3)
- Hover state: Light gray background (#f8f9fa)

### Cards and Containers

Content is organized in cards and containers with subtle shadows and rounded corners.

- Background: White (#ffffff)
- Border: None
- Border Radius: 0.75rem
- Shadow: 0 4px 6px rgba(0,0,0,0.1)
- Hover effect: Slight elevation increase and shadow enhancement

### Buttons

Buttons use consistent styling based on their purpose:

- **Primary Buttons**: Primary Blue background, white text
- **Secondary Buttons**: Secondary Gold background, dark text
- **Outline Buttons**: Transparent background, colored border and text
- **Danger Buttons**: Danger Red background, white text

All buttons have subtle hover and active states, with a slight "push" effect when clicked.

### Forms

Form elements use consistent styling:

- Input fields have a light border and focus state with Primary Blue
- Labels are positioned above fields and use Medium Gray text
- Validation states include green for valid and red for invalid inputs
- Help text appears below fields in a smaller font size

### Tables

Tables use clean styling with subtle headers:

- Header background: Light Gray (#f8f9fa)
- Borders: Light Gray borders between rows
- Hover state: Very light blue background on row hover
- Responsive: Tables scroll horizontally on small screens

### Status Indicators

Status indicators use consistent colors and styles:

- **Operational**: Green badge with checkmark icon
- **Under Maintenance**: Yellow badge with wrench icon
- **Out of Service**: Red badge with x-mark icon
- **Low Stock**: Yellow badge with exclamation icon
- **Out of Stock**: Red badge with exclamation icon

## Layout Guidelines

### Spacing

Consistent spacing scale is used throughout the application:

- Extra Small (xs): 0.25rem (4px)
- Small (sm): 0.5rem (8px)
- Medium (md): 1rem (16px)
- Large (lg): 1.5rem (24px)
- Extra Large (xl): 2rem (32px)
- Extra Extra Large (xxl): 3rem (48px)

### Grid System

The application uses Bootstrap's 12-column grid system for layout. Major sections use the following patterns:

- Dashboard: Card grid with 3-4 cards per row on large screens, 2 on medium, 1 on small
- List views: Full width with responsive tables
- Detail views: Two-column layout on large screens (30% sidebar, 70% content), stacked on small screens
- Forms: Single column on small screens, potentially multi-column on large screens

### Responsive Breakpoints

- Small devices: < 576px
- Medium devices: ≥ 576px
- Large devices: ≥ 992px
- Extra-large devices: ≥ 1200px

## Animation Guidelines

Animations are used sparingly to enhance user experience without causing distraction:

- **Loading Screen**: Smooth fade-out after initial load
- **Page Transitions**: Subtle fade-in for page content
- **Hover Effects**: Slight elevation change for cards and buttons
- **Status Changes**: Smooth transitions for status changes
- **Alerts**: Fade-in and auto-dismissal for temporary notifications

Animation durations:
- Fast transitions: 150ms
- Normal transitions: 250ms
- Slow transitions: 500ms

## Implementation Details

### CSS Organization

The CSS is organized into logical sections:
- Variables (colors, typography, spacing, etc.)
- Base elements (body, headings, links, etc.)
- Components (buttons, cards, tables, etc.)
- Layout (grid, containers, etc.)
- Utilities (helpers, spacers, etc.)
- Responsive adjustments

### Accessibility Guidelines

- Maintain color contrast ratios of at least 4.5:1 for normal text
- Ensure all interactive elements are keyboard-navigable
- Include aria attributes for custom components
- Use semantic HTML elements
- Ensure form elements have proper labels
- Provide text alternatives for non-text content

## Usage Examples

### Dashboard Widgets

Dashboard widgets should use consistent card styling with:
- Clear title at the top
- Large, emphasized value
- Supporting information or trend indicator
- Icon relevant to the displayed metric
- Consistent spacing and alignment

### List Views

List views should use consistent styling with:
- Filter panel at the top (collapsible on mobile)
- Action buttons in the top right
- Responsive table with consistent column alignment
- Status indicators using the standard badge styles
- Pagination at the bottom when needed

### Detail Views

Detail views should use consistent styling with:
- Breadcrumb navigation at the top
- Main title and action buttons in the header
- Organized sections with clear headings
- Two-column layout for specifications and properties
- Related items in cards at the bottom

## Conclusion

This visual identity guide provides a comprehensive framework for maintaining a consistent, professional, and user-friendly interface throughout the SSBDM system. By adhering to these guidelines, we ensure that the application is not only visually appealing but also highly usable and accessible to all users. 