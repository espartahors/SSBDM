sap.ui.define([
    "ssbdm/controller/BaseController",
    "sap/ui/model/json/JSONModel",
    "sap/ui/model/Filter",
    "sap/ui/model/FilterOperator",
    "sap/m/MessageBox",
    "sap/m/MessageToast"
], function (BaseController, JSONModel, Filter, FilterOperator, MessageBox, MessageToast) {
    "use strict";

    return BaseController.extend("ssbdm.controller.equipment.Equipment", {
        /**
         * Called when the controller is instantiated
         */
        onInit: function () {
            // Set up local view model for filtering
            this._initViewModel();
            
            // Get the router and register for route pattern matched event
            this.getRouter().getRoute("equipment").attachPatternMatched(this._onRouteMatched, this);
        },
        
        /**
         * Initialize the view model with filter values
         * @private
         */
        _initViewModel: function() {
            var oViewModel = new JSONModel({
                filters: {
                    status: "",
                    area: "",
                    searchText: ""
                },
                busy: false,
                noDataText: this.getResourceBundle().getText("loading"),
                itemsCount: 0
            });
            
            this.setModel(oViewModel, "view");
        },
        
        /**
         * Route pattern matched handler - loads equipment data
         * @private
         */
        _onRouteMatched: function() {
            this._loadEquipmentData();
            this._loadFiltersData();
        },
        
        /**
         * Load equipment data from the backend API
         * @private
         */
        _loadEquipmentData: function() {
            // Show busy indicator
            this.getModel("view").setProperty("/busy", true);
            
            // Get the equipment model
            var oModel = this.getModel("equipmentAPI");
            
            // Refresh the model
            oModel.refresh(true);
            
            // Set the no data text to loading while the data is being loaded
            this.getModel("view").setProperty("/noDataText", this.getResourceBundle().getText("loading"));
            
            // Register the model's data loaded event
            oModel.attachEventOnce("requestCompleted", function() {
                this.getModel("view").setProperty("/busy", false);
                this.getModel("view").setProperty("/noDataText", this.getResourceBundle().getText("noEquipmentDataFound"));
                this._updateItemsCount();
            }.bind(this));
            
            // Register the model's error event
            oModel.attachEventOnce("requestFailed", function() {
                this.getModel("view").setProperty("/busy", false);
                this.getModel("view").setProperty("/noDataText", this.getResourceBundle().getText("errorLoadingData"));
                MessageToast.show(this.getResourceBundle().getText("errorLoadingData"));
            }.bind(this));
        },
        
        /**
         * Load filter data (status and area lists)
         * @private
         */
        _loadFiltersData: function() {
            // Load status options
            var oStatusModel = this.getModel("equipmentStatusAPI");
            oStatusModel.refresh(true);
            
            // Load area options
            var oAreaModel = this.getModel("equipmentAreasAPI");
            oAreaModel.refresh(true);
        },
        
        /**
         * Updates the count of items in the table
         * @private
         */
        _updateItemsCount: function() {
            var oTable = this.byId("equipmentTable");
            var iCount = oTable.getBinding("items").getLength();
            this.getModel("view").setProperty("/itemsCount", iCount);
        },
        
        /**
         * Handler for the create button press
         */
        onCreatePress: function() {
            this.navTo("equipmentDetail", {
                id: "new"
            });
        },
        
        /**
         * Handler for the edit button press
         * @param {sap.ui.base.Event} oEvent Event object
         */
        onEditPress: function(oEvent) {
            var oSource = oEvent.getSource();
            var oEquipment = oSource.getBindingContext("equipmentAPI").getObject();
            
            this.navTo("equipmentDetail", {
                id: oEquipment.id
            });
        },
        
        /**
         * Handler for the delete button press
         * @param {sap.ui.base.Event} oEvent Event object
         */
        onDeletePress: function(oEvent) {
            var oSource = oEvent.getSource();
            var oEquipment = oSource.getBindingContext("equipmentAPI").getObject();
            var sEquipmentName = oEquipment.name;
            
            MessageBox.confirm(
                this.getResourceBundle().getText("equipmentDeleteConfirm", [sEquipmentName]),
                {
                    title: this.getResourceBundle().getText("confirm"),
                    onClose: function(sAction) {
                        if (sAction === MessageBox.Action.OK) {
                            this._deleteEquipment(oEquipment.id);
                        }
                    }.bind(this)
                }
            );
        },
        
        /**
         * Deletes equipment via API call
         * @param {string} sEquipmentId ID of the equipment to delete
         * @private
         */
        _deleteEquipment: function(sEquipmentId) {
            // Show busy indicator
            this.getModel("view").setProperty("/busy", true);
            
            // Get the equipment model
            var oModel = this.getModel("equipmentAPI");
            
            // Perform DELETE request
            var sUrl = "/api/equipment/" + sEquipmentId + "/";
            
            jQuery.ajax({
                url: sUrl,
                type: "DELETE",
                success: function() {
                    MessageToast.show(this.getResourceBundle().getText("equipmentDeleteSuccess"));
                    this._loadEquipmentData();
                }.bind(this),
                error: function() {
                    MessageBox.error(this.getResourceBundle().getText("equipmentDeleteError"));
                    this.getModel("view").setProperty("/busy", false);
                }.bind(this)
            });
        },
        
        /**
         * Handler for item press - navigate to detail view
         * @param {sap.ui.base.Event} oEvent Event object
         */
        onItemPress: function(oEvent) {
            var oItem = oEvent.getSource();
            var oEquipment = oItem.getBindingContext("equipmentAPI").getObject();
            
            this.navTo("equipmentDetail", {
                id: oEquipment.id
            });
        },
        
        /**
         * Handler for the search field
         * @param {sap.ui.base.Event} oEvent Event object
         */
        onSearch: function(oEvent) {
            var sValue = oEvent.getParameter("query");
            this.getModel("view").setProperty("/filters/searchText", sValue);
            this._applyFilters();
        },
        
        /**
         * Handler for the status filter selection
         * @param {sap.ui.base.Event} oEvent Event object
         */
        onStatusFilterChange: function(oEvent) {
            var sKey = oEvent.getParameter("selectedItem").getKey();
            this.getModel("view").setProperty("/filters/status", sKey);
            this._applyFilters();
        },
        
        /**
         * Handler for the area filter selection
         * @param {sap.ui.base.Event} oEvent Event object
         */
        onAreaFilterChange: function(oEvent) {
            var sKey = oEvent.getParameter("selectedItem").getKey();
            this.getModel("view").setProperty("/filters/area", sKey);
            this._applyFilters();
        },
        
        /**
         * Apply the filters to the table
         * @private
         */
        _applyFilters: function() {
            var oTable = this.byId("equipmentTable");
            var oBinding = oTable.getBinding("items");
            var aFilters = [];
            var oFilters = this.getModel("view").getProperty("/filters");
            
            // Create search filter
            if (oFilters.searchText) {
                aFilters.push(new Filter({
                    filters: [
                        new Filter("code", FilterOperator.Contains, oFilters.searchText),
                        new Filter("name", FilterOperator.Contains, oFilters.searchText),
                        new Filter("model", FilterOperator.Contains, oFilters.searchText),
                        new Filter("manufacturer", FilterOperator.Contains, oFilters.searchText)
                    ],
                    and: false
                }));
            }
            
            // Add status filter
            if (oFilters.status) {
                aFilters.push(new Filter("status", FilterOperator.EQ, oFilters.status));
            }
            
            // Add area filter
            if (oFilters.area) {
                aFilters.push(new Filter("area", FilterOperator.EQ, oFilters.area));
            }
            
            // Apply the filters
            oBinding.filter(aFilters);
            
            // Update count
            this._updateItemsCount();
        },
        
        /**
         * Handler for the clear filters button
         */
        onClearFilters: function() {
            // Reset filters in the view model
            this.getModel("view").setProperty("/filters", {
                status: "",
                area: "",
                searchText: ""
            });
            
            // Reset UI controls
            this.byId("searchField").setValue("");
            this.byId("statusFilter").setSelectedKey("");
            this.byId("areaFilter").setSelectedKey("");
            
            // Clear filters on the table
            var oTable = this.byId("equipmentTable");
            var oBinding = oTable.getBinding("items");
            oBinding.filter([]);
            
            // Update count
            this._updateItemsCount();
        },
        
        /**
         * Handler for refresh button press
         */
        onRefresh: function() {
            this._loadEquipmentData();
        },
        
        /**
         * Formatter for equipment status
         * @param {string} sStatus Status code
         * @returns {string} Semantic state for the UI control
         */
        formatStatusState: function(sStatus) {
            switch (sStatus) {
                case "ACTIVE":
                    return "Success";
                case "INACTIVE":
                    return "Error";
                case "MAINTENANCE":
                    return "Warning";
                default:
                    return "None";
            }
        }
    });
}); 