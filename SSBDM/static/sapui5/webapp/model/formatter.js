sap.ui.define([], function () {
    "use strict";

    return {
        /**
         * Format currency values
         * @param {number} value Currency value
         * @returns {string} Formatted currency value
         */
        formatCurrency: function (value) {
            if (!value) {
                return "0.00";
            }
            
            return parseFloat(value).toFixed(2);
        },
        
        /**
         * Format date to locale specific date string
         * @param {string} dateString Date string in ISO format
         * @returns {string} Formatted date string
         */
        formatDate: function (dateString) {
            if (!dateString) {
                return "";
            }
            
            var oDate = new Date(dateString);
            var oOptions = { year: "numeric", month: "short", day: "numeric" };
            
            return oDate.toLocaleDateString(undefined, oOptions);
        },
        
        /**
         * Format date and time to locale specific datetime string
         * @param {string} dateString Date string in ISO format
         * @returns {string} Formatted datetime string
         */
        formatDateTime: function (dateString) {
            if (!dateString) {
                return "";
            }
            
            var oDate = new Date(dateString);
            var oOptions = { 
                year: "numeric", 
                month: "short", 
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            };
            
            return oDate.toLocaleDateString(undefined, oOptions);
        },
        
        /**
         * Format equipment status to display text
         * @param {string} status Equipment status code
         * @returns {string} Formatted status text
         */
        formatEquipmentStatus: function (status) {
            if (!status) {
                return "";
            }
            
            switch (status) {
                case "active":
                    return "Active";
                case "inactive":
                    return "Inactive";
                case "maintenance":
                    return "Under Maintenance";
                case "decommissioned":
                    return "Decommissioned";
                default:
                    return status;
            }
        },
        
        /**
         * Format maintenance log status to display text
         * @param {string} status Maintenance log status code
         * @returns {string} Formatted status text
         */
        formatMaintenanceStatus: function (status) {
            if (!status) {
                return "";
            }
            
            switch (status) {
                case "pending":
                    return "Pending";
                case "in_progress":
                    return "In Progress";
                case "completed":
                    return "Completed";
                default:
                    return status;
            }
        },
        
        /**
         * Format maintenance type to display text
         * @param {string} type Maintenance type code
         * @returns {string} Formatted type text
         */
        formatMaintenanceType: function (type) {
            if (!type) {
                return "";
            }
            
            switch (type) {
                case "preventive":
                    return "Preventive";
                case "corrective":
                    return "Corrective";
                case "predictive":
                    return "Predictive";
                case "regulatory":
                    return "Regulatory";
                default:
                    return type;
            }
        },
        
        /**
         * Format spare part status to display text
         * @param {string} status Spare part status code
         * @returns {string} Formatted status text
         */
        formatSparePartStatus: function (status) {
            if (!status) {
                return "";
            }
            
            switch (status) {
                case "in_stock":
                    return "In Stock";
                case "low_stock":
                    return "Low Stock";
                case "out_of_stock":
                    return "Out of Stock";
                default:
                    return status;
            }
        },
        
        /**
         * Format transaction type to display text
         * @param {string} type Transaction type code
         * @returns {string} Formatted type text
         */
        formatTransactionType: function (type) {
            if (!type) {
                return "";
            }
            
            switch (type) {
                case "receipt":
                    return "Receipt";
                case "issue":
                    return "Issue";
                case "return":
                    return "Return";
                case "adjustment":
                    return "Adjustment";
                default:
                    return type;
            }
        },
        
        /**
         * Format quantity with unit
         * @param {number} quantity Quantity value
         * @param {string} unit Unit of measure
         * @returns {string} Formatted quantity with unit
         */
        formatQuantityWithUnit: function (quantity, unit) {
            if (quantity === null || quantity === undefined) {
                return "";
            }
            
            return quantity + (unit ? " " + unit : "");
        },
        
        /**
         * Format phone number
         * @param {string} phoneNumber Phone number string
         * @returns {string} Formatted phone number
         */
        formatPhoneNumber: function (phoneNumber) {
            if (!phoneNumber) {
                return "";
            }
            
            // Basic formatting, can be extended based on country requirements
            return phoneNumber.replace(/(\d{3})(\d{3})(\d{4})/, "($1) $2-$3");
        },
        
        /**
         * Format file size in bytes to human-readable format
         * @param {number} bytes File size in bytes
         * @returns {string} Formatted file size
         */
        formatFileSize: function (bytes) {
            if (!bytes) {
                return "0 Bytes";
            }
            
            var sizes = ["Bytes", "KB", "MB", "GB", "TB"];
            var i = Math.floor(Math.log(bytes) / Math.log(1024));
            
            return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + " " + sizes[i];
        }
    };
}); 