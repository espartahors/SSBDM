sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/ui/model/Filter",
    "sap/ui/model/FilterOperator",
    "sap/ui/model/Sorter",
    "sap/m/MessageToast",
    "sap/m/MessageBox",
    "sap/m/Dialog",
    "sap/m/Button",
    "sap/m/List",
    "sap/m/StandardListItem",
    "../../model/RestModel"
], function (Controller, JSONModel, Filter, FilterOperator, Sorter, MessageToast,
             MessageBox, Dialog, Button, List, StandardListItem, RestModel) {
    "use strict";

    return Controller.extend("ssbdm.controller.maintenance.Maintenance", {
        onInit: function () {
            // Set up view model
            var oViewModel = new JSONModel({
                headerExpanded: true,
                maintenanceLogs: [],
                maintenanceCount: 0,
                busy: false,
                statusOptions: [
                    { key: "", text: "All" },
                    { key: "pending", text: "Pending" },
                    { key: "in_progress", text: "In Progress" },
                    { key: "completed", text: "Completed" }
                ],
                typeOptions: [
                    { key: "", text: "All" },
                    { key: "preventive", text: "Preventive" },
                    { key: "corrective", text: "Corrective" },
                    { key: "predictive", text: "Predictive" },
                    { key: "regulatory", text: "Regulatory" }
                ]
            });
            this.getView().setModel(oViewModel, "view");

            // Initialize filters
            this._filters = {
                status: [],
                type: [],
                dateRange: [],
                search: []
            };

            // Load initial data
            this._loadMaintenanceLogs();

            // Register for route matched event
            this.getOwnerComponent().getRouter().getRoute("maintenance").attachPatternMatched(this._onRouteMatched, this);
        },

        /**
         * Handler for route matched event
         * @param {sap.ui.base.Event} oEvent event object
         * @private
         */
        _onRouteMatched: function (oEvent) {
            // Refresh data when navigating to this view
            this._loadMaintenanceLogs();
        },

        /**
         * Load maintenance logs from API
         * @private
         */
        _loadMaintenanceLogs: function () {
            var oViewModel = this.getView().getModel("view");
            oViewModel.setProperty("/busy", true);

            // Call API to get maintenance logs
            RestModel.get("/api/maintenance/logs/").then(function (data) {
                // Update model with maintenance logs data
                if (data && data.results) {
                    oViewModel.setProperty("/maintenanceLogs", data.results);
                    oViewModel.setProperty("/maintenanceCount", data.results.length);
                } else {
                    oViewModel.setProperty("/maintenanceLogs", []);
                    oViewModel.setProperty("/maintenanceCount", 0);
                }
                oViewModel.setProperty("/busy", false);
            }).catch(function (error) {
                console.error("Error loading maintenance logs:", error);
                oViewModel.setProperty("/busy", false);
                MessageBox.error("Failed to load maintenance logs. Please try again.");
            });
        },

        /**
         * Navigate back to previous page
         */
        onNavBack: function () {
            this.getOwnerComponent().getRouter().navTo("home");
        },

        /**
         * Create new maintenance log
         */
        onCreateLog: function () {
            // In a real app, navigate to create form or open dialog
            this.getOwnerComponent().getRouter().navTo("maintenanceCreate");
        },

        /**
         * Toggle filter bar
         */
        onToggleFilterBar: function () {
            var oDynamicPage = this.byId("dynamicPageId");
            var oViewModel = this.getView().getModel("view");
            var bExpanded = !oDynamicPage.getHeaderExpanded();
            
            oDynamicPage.setHeaderExpanded(bExpanded);
            oViewModel.setProperty("/headerExpanded", bExpanded);
        },

        /**
         * Refresh maintenance logs
         */
        onRefresh: function () {
            this._loadMaintenanceLogs();
            MessageToast.show("Maintenance logs refreshed");
        },

        /**
         * Reset all filters
         */
        onResetFilters: function () {
            // Reset filter values
            this.byId("searchField").setValue("");
            this.byId("statusFilter").setSelectedKey("");
            this.byId("typeFilter").setSelectedKey("");
            this.byId("dateRangeFilter").setValue("");
            
            // Clear all filters
            this._filters = {
                status: [],
                type: [],
                dateRange: [],
                search: []
            };
            
            // Apply empty filters
            this._applyFilters();
            
            MessageToast.show("Filters reset");
        },

        /**
         * Handle search
         * @param {sap.ui.base.Event} oEvent event object
         */
        onSearch: function (oEvent) {
            var sQuery = oEvent.getParameter("query");
            this._applySearchFilter(sQuery);
        },

        /**
         * Handle live search
         * @param {sap.ui.base.Event} oEvent event object
         */
        onSearchLiveChange: function (oEvent) {
            var sQuery = oEvent.getParameter("newValue");
            this._applySearchFilter(sQuery);
        },

        /**
         * Apply search filter
         * @param {string} sQuery search query
         * @private
         */
        _applySearchFilter: function (sQuery) {
            // Create filters for search
            var aSearchFilters = [];
            if (sQuery && sQuery.length > 0) {
                aSearchFilters.push(new Filter("description", FilterOperator.Contains, sQuery));
                aSearchFilters.push(new Filter("equipment_name", FilterOperator.Contains, sQuery));
                aSearchFilters.push(new Filter("equipment_code", FilterOperator.Contains, sQuery));
                aSearchFilters.push(new Filter("technician_name", FilterOperator.Contains, sQuery));

                // Combine with OR operator
                this._filters.search = [new Filter({
                    filters: aSearchFilters,
                    and: false
                })];
            } else {
                this._filters.search = [];
            }

            // Apply filters
            this._applyFilters();
        },

        /**
         * Handle filter change
         * @param {sap.ui.base.Event} oEvent event object
         */
        onFilterChange: function (oEvent) {
            var oComboBox = oEvent.getSource();
            var sFilterId = oComboBox.getId();
            var sSelectedKey = oEvent.getParameter("selectedItem").getKey();
            
            // Create filters based on filter type
            if (sFilterId.indexOf("statusFilter") !== -1) {
                this._applyStatusFilter(sSelectedKey);
            } else if (sFilterId.indexOf("typeFilter") !== -1) {
                this._applyTypeFilter(sSelectedKey);
            }
        },

        /**
         * Apply status filter
         * @param {string} sStatusKey selected status key
         * @private
         */
        _applyStatusFilter: function (sStatusKey) {
            if (sStatusKey) {
                this._filters.status = [new Filter("status", FilterOperator.EQ, sStatusKey)];
            } else {
                this._filters.status = [];
            }

            // Apply filters
            this._applyFilters();
        },

        /**
         * Apply type filter
         * @param {string} sTypeKey selected type key
         * @private
         */
        _applyTypeFilter: function (sTypeKey) {
            if (sTypeKey) {
                this._filters.type = [new Filter("maintenance_type", FilterOperator.EQ, sTypeKey)];
            } else {
                this._filters.type = [];
            }

            // Apply filters
            this._applyFilters();
        },

        /**
         * Handle date range change
         * @param {sap.ui.base.Event} oEvent event object
         */
        onDateRangeChange: function (oEvent) {
            var oDateRange = oEvent.getSource();
            var oDateValue = oDateRange.getDateValue();
            var oSecondDateValue = oDateRange.getSecondDateValue();
            
            if (oDateValue && oSecondDateValue) {
                // Set time to start and end of day
                oDateValue.setHours(0, 0, 0, 0);
                oSecondDateValue.setHours(23, 59, 59, 999);
                
                // Create filters for date range
                this._filters.dateRange = [new Filter({
                    path: "date",
                    operator: FilterOperator.BT,
                    value1: oDateValue,
                    value2: oSecondDateValue
                })];
            } else {
                this._filters.dateRange = [];
            }
            
            // Apply filters
            this._applyFilters();
        },

        /**
         * Apply all filters to table
         * @private
         */
        _applyFilters: function () {
            // Merge all filters
            var aFilters = [];
            aFilters = aFilters.concat(
                this._filters.status, 
                this._filters.type, 
                this._filters.dateRange, 
                this._filters.search
            );
            
            // Get table binding and apply filters
            var oTable = this.byId("maintenanceTable");
            var oBinding = oTable.getBinding("items");
            
            if (oBinding) {
                oBinding.filter(aFilters);
            }
        },

        /**
         * Open sort dialog
         */
        onOpenSortDialog: function () {
            if (!this._oSortDialog) {
                this._oSortDialog = new Dialog({
                    title: "Sort By",
                    contentWidth: "280px",
                    content: new List({
                        items: [
                            new StandardListItem({ title: "Date (Newest First)", type: "Active", custom: { path: "date", descending: true } }),
                            new StandardListItem({ title: "Date (Oldest First)", type: "Active", custom: { path: "date", descending: false } }),
                            new StandardListItem({ title: "Equipment", type: "Active", custom: { path: "equipment_name", descending: false } }),
                            new StandardListItem({ title: "Status", type: "Active", custom: { path: "status", descending: false } }),
                            new StandardListItem({ title: "Type", type: "Active", custom: { path: "maintenance_type", descending: false } })
                        ],
                        itemPress: this.onSortItemPress.bind(this)
                    }),
                    beginButton: new Button({
                        text: "Close",
                        press: function () {
                            this._oSortDialog.close();
                        }.bind(this)
                    })
                });
                this.getView().addDependent(this._oSortDialog);
            }
            
            this._oSortDialog.open();
        },

        /**
         * Handle sort item press
         * @param {sap.ui.base.Event} oEvent event object
         */
        onSortItemPress: function (oEvent) {
            var oItem = oEvent.getParameter("listItem");
            var oCustomData = oItem.getCustomData()[0].getValue();
            
            // Create sorter
            var oSorter = new Sorter(oCustomData.path, oCustomData.descending);
            
            // Apply sorter to table
            var oTable = this.byId("maintenanceTable");
            var oBinding = oTable.getBinding("items");
            
            if (oBinding) {
                oBinding.sort(oSorter);
            }
            
            // Close dialog
            this._oSortDialog.close();
            
            // Show message
            MessageToast.show("Sorted by " + oItem.getTitle());
        },

        /**
         * Handle maintenance log item press
         * @param {sap.ui.base.Event} oEvent event object
         */
        onMaintenanceLogPress: function (oEvent) {
            var oItem = oEvent.getSource();
            var oContext = oItem.getBindingContext("view");
            var sMaintenanceId = oContext.getProperty("id");
            
            // Navigate to maintenance log detail
            this.getOwnerComponent().getRouter().navTo("maintenanceLogDetail", {
                id: sMaintenanceId
            });
        },

        /**
         * Handle edit maintenance log
         * @param {sap.ui.base.Event} oEvent event object
         */
        onEditMaintenanceLog: function (oEvent) {
            // Stop event propagation to prevent navigation
            oEvent.stopPropagation();
            
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("view");
            var sMaintenanceId = oContext.getProperty("id");
            
            // Navigate to edit maintenance log
            this.getOwnerComponent().getRouter().navTo("maintenanceEdit", {
                id: sMaintenanceId
            });
        },

        /**
         * Handle delete maintenance log
         * @param {sap.ui.base.Event} oEvent event object
         */
        onDeleteMaintenanceLog: function (oEvent) {
            // Stop event propagation to prevent navigation
            oEvent.stopPropagation();
            
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("view");
            var sMaintenanceId = oContext.getProperty("id");
            var sDescription = oContext.getProperty("description");
            var sEquipmentName = oContext.getProperty("equipment_name");
            
            // Confirm delete
            MessageBox.confirm(
                "Are you sure you want to delete maintenance log for " + sEquipmentName + "?\n" + 
                "Description: " + sDescription, 
                {
                    title: "Confirm Delete",
                    onClose: function (oAction) {
                        if (oAction === MessageBox.Action.OK) {
                            // Delete maintenance log
                            this._deleteMaintenanceLog(sMaintenanceId);
                        }
                    }.bind(this)
                }
            );
        },

        /**
         * Delete maintenance log
         * @param {string} sMaintenanceId maintenance log ID
         * @private
         */
        _deleteMaintenanceLog: function (sMaintenanceId) {
            var oViewModel = this.getView().getModel("view");
            oViewModel.setProperty("/busy", true);
            
            // Call API to delete maintenance log
            RestModel.delete("/api/maintenance/logs/" + sMaintenanceId + "/").then(function () {
                // Reload maintenance logs
                this._loadMaintenanceLogs();
                MessageToast.show("Maintenance log deleted successfully");
            }.bind(this)).catch(function (error) {
                console.error("Error deleting maintenance log:", error);
                oViewModel.setProperty("/busy", false);
                MessageBox.error("Failed to delete maintenance log. Please try again.");
            });
        },

        /**
         * Handle table update finished
         * @param {sap.ui.base.Event} oEvent event object
         */
        onUpdateFinished: function (oEvent) {
            var iTotalItems = oEvent.getParameter("total");
            var oViewModel = this.getView().getModel("view");
            
            // Update maintenance log count
            oViewModel.setProperty("/maintenanceCount", iTotalItems);
        }
    });
}); 