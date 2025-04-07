sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast",
    "../model/RestModel"
], function(Controller, JSONModel, MessageToast, RestModel) {
    "use strict";

    return Controller.extend("ssbdm.controller.Home", {
        onInit: function() {
            // Initialize models for dashboard data
            this._initModels();
            
            // Load initial data
            this._loadDashboardData();
        },
        
        /**
         * Initialize models for dashboard data
         * @private
         */
        _initModels: function() {
            // Equipment dashboard data
            var oEquipmentModel = new JSONModel({
                totalCount: 0,
                activeCount: 0,
                areaCount: 0
            });
            this.getView().setModel(oEquipmentModel, "equipment");

            // Maintenance dashboard data
            var oMaintenanceModel = new JSONModel({
                logCount: 0,
                pendingTaskCount: 0,
                overdueTaskCount: 0,
                activePlanCount: 0,
                documentCount: 0
            });
            this.getView().setModel(oMaintenanceModel, "maintenance");

            // Spare parts dashboard data
            var oSparePartsModel = new JSONModel({
                totalCount: 0,
                lowStockCount: 0,
                categoryCount: 0,
                recentTransactionCount: 0
            });
            this.getView().setModel(oSparePartsModel, "spareParts");

            // Audit log model for recent activities
            var oAuditLogModel = new JSONModel({
                results: []
            });
            this.getView().setModel(oAuditLogModel, "auditLog");
        },
        
        /**
         * Load all dashboard data
         * @private
         */
        _loadDashboardData: function() {
            this._loadEquipmentData();
            this._loadMaintenanceData();
            this._loadSparePartsData();
            this._loadRecentActivities();
        },
        
        /**
         * Load equipment dashboard data
         * @private
         */
        _loadEquipmentData: function() {
            var oEquipmentModel = this.getView().getModel("equipment");
            
            // Make API calls to get equipment summary data
            RestModel.get("/api/equipment/equipment/").then(function(data) {
                // Update model with counts
                oEquipmentModel.setProperty("/totalCount", data.count || 0);
                
                // Get active equipment count
                return RestModel.get("/api/equipment/equipment/", { status: "active" });
            }).then(function(data) {
                oEquipmentModel.setProperty("/activeCount", data.count || 0);
                
                // Get areas count
                return RestModel.get("/api/equipment/areas/");
            }).then(function(data) {
                oEquipmentModel.setProperty("/areaCount", data.count || 0);
            }).catch(function(error) {
                console.error("Error loading equipment data:", error);
            });
        },
        
        /**
         * Load maintenance dashboard data
         * @private
         */
        _loadMaintenanceData: function() {
            var oMaintenanceModel = this.getView().getModel("maintenance");
            
            // Make API calls to get maintenance summary data
            RestModel.get("/api/maintenance/logs/").then(function(data) {
                oMaintenanceModel.setProperty("/logCount", data.count || 0);
                
                // Get pending tasks count
                return RestModel.get("/api/maintenance/tasks/", { status: "pending" });
            }).then(function(data) {
                oMaintenanceModel.setProperty("/pendingTaskCount", data.count || 0);
                
                // Get overdue tasks
                return RestModel.get("/api/maintenance/tasks/overdue/");
            }).then(function(data) {
                oMaintenanceModel.setProperty("/overdueTaskCount", data.count || 0);
                
                // Get active plans count
                return RestModel.get("/api/maintenance/plans/active/");
            }).then(function(data) {
                oMaintenanceModel.setProperty("/activePlanCount", data.count || 0);
                
                // Get documents count
                return RestModel.get("/api/maintenance/documents/");
            }).then(function(data) {
                oMaintenanceModel.setProperty("/documentCount", data.count || 0);
            }).catch(function(error) {
                console.error("Error loading maintenance data:", error);
            });
        },
        
        /**
         * Load spare parts dashboard data
         * @private
         */
        _loadSparePartsData: function() {
            var oSparePartsModel = this.getView().getModel("spareParts");
            
            // Make API calls to get spare parts summary data
            RestModel.get("/api/spare-parts/parts/").then(function(data) {
                oSparePartsModel.setProperty("/totalCount", data.count || 0);
                
                // Get low stock items count
                return RestModel.get("/api/spare-parts/parts/low_stock/");
            }).then(function(data) {
                oSparePartsModel.setProperty("/lowStockCount", data.count || 0);
                
                // Get categories count
                return RestModel.get("/api/spare-parts/categories/");
            }).then(function(data) {
                oSparePartsModel.setProperty("/categoryCount", data.count || 0);
                
                // Get recent transactions count (last 7 days)
                return RestModel.get("/api/spare-parts/transactions/recent/", { days: 7 });
            }).then(function(data) {
                oSparePartsModel.setProperty("/recentTransactionCount", data.count || 0);
            }).catch(function(error) {
                console.error("Error loading spare parts data:", error);
            });
        },
        
        /**
         * Load recent activities from audit logs
         * @private
         */
        _loadRecentActivities: function() {
            var oAuditLogModel = this.getView().getModel("auditLog");
            
            // Get recent audit logs (last 10)
            RestModel.get("/api/maintenance/audit-logs/recent/", { days: 1 }).then(function(data) {
                // Limit to 10 results for dashboard
                var aResults = data.results || [];
                if (aResults.length > 10) {
                    aResults = aResults.slice(0, 10);
                }
                
                oAuditLogModel.setProperty("/results", aResults);
            }).catch(function(error) {
                console.error("Error loading audit logs:", error);
            });
        },
        
        /**
         * Handle navigation to Equipment page
         */
        onNavToEquipment: function() {
            this.getOwnerComponent().getRouter().navTo("equipment");
        },
        
        /**
         * Handle navigation to Maintenance Logs page
         */
        onNavToMaintenanceLogs: function() {
            this.getOwnerComponent().getRouter().navTo("maintenance");
        },
        
        /**
         * Handle navigation to Maintenance Tasks page
         */
        onNavToMaintenanceTasks: function() {
            this.getOwnerComponent().getRouter().navTo("maintenanceTasks");
        },
        
        /**
         * Handle navigation to Spare Parts page
         */
        onNavToSpareParts: function() {
            this.getOwnerComponent().getRouter().navTo("spareParts");
        },
        
        /**
         * Handle refresh button press
         */
        onRefreshPress: function() {
            this._loadDashboardData();
            MessageToast.show("Dashboard data refreshed");
        }
    });
}); 