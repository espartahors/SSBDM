sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast",
    "sap/m/MessageBox",
    "sap/m/Dialog",
    "sap/m/Button",
    "../../model/RestModel"
], function (Controller, JSONModel, MessageToast, MessageBox, Dialog, Button, RestModel) {
    "use strict";

    return Controller.extend("ssbdm.controller.equipment.EquipmentDetail", {
        onInit: function () {
            // Set up view model
            var oViewModel = new JSONModel({
                busy: false,
                equipment: {},
                maintenanceLogDialogMode: "create"
            });
            this.getView().setModel(oViewModel, "equipment");

            // Register for route matched event
            this.getOwnerComponent().getRouter().getRoute("equipmentDetail").attachPatternMatched(this._onRouteMatched, this);
        },

        /**
         * Handler for route matched event
         * @param {sap.ui.base.Event} oEvent event object
         * @private
         */
        _onRouteMatched: function (oEvent) {
            var sEquipmentId = oEvent.getParameter("arguments").id;
            
            // Load equipment details
            this._loadEquipmentData(sEquipmentId);
        },

        /**
         * Load equipment data from API
         * @param {string} sEquipmentId equipment ID
         * @private
         */
        _loadEquipmentData: function (sEquipmentId) {
            var oViewModel = this.getView().getModel("equipment");
            oViewModel.setProperty("/busy", true);

            // Call API to get equipment details
            RestModel.get("/api/equipment/equipment/" + sEquipmentId + "/").then(function (data) {
                // Update model with equipment data
                if (data) {
                    // Set base equipment data
                    oViewModel.setProperty("/equipment", data);
                    
                    // Load specifications
                    this._loadSpecifications(sEquipmentId);
                    
                    // Load maintenance logs
                    this._loadMaintenanceLogs(sEquipmentId);
                    
                    // Load documents
                    this._loadDocuments(sEquipmentId);
                }
                oViewModel.setProperty("/busy", false);
            }.bind(this)).catch(function (error) {
                console.error("Error loading equipment data:", error);
                oViewModel.setProperty("/busy", false);
                MessageBox.error("Failed to load equipment details. Please try again later.");
            });
        },

        /**
         * Load equipment specifications
         * @param {string} sEquipmentId equipment ID
         * @private
         */
        _loadSpecifications: function (sEquipmentId) {
            var oViewModel = this.getView().getModel("equipment");

            // Call API to get specifications
            RestModel.get("/api/equipment/equipment/" + sEquipmentId + "/specifications/").then(function (data) {
                if (data && data.results) {
                    oViewModel.setProperty("/specifications", data.results);
                } else {
                    oViewModel.setProperty("/specifications", []);
                }
            }).catch(function (error) {
                console.error("Error loading specifications:", error);
                oViewModel.setProperty("/specifications", []);
            });
        },

        /**
         * Load maintenance logs for equipment
         * @param {string} sEquipmentId equipment ID
         * @private
         */
        _loadMaintenanceLogs: function (sEquipmentId) {
            var oViewModel = this.getView().getModel("equipment");

            // Call API to get maintenance logs
            RestModel.get("/api/maintenance/logs/?equipment=" + sEquipmentId).then(function (data) {
                if (data && data.results) {
                    oViewModel.setProperty("/maintenance_logs", data.results);
                    oViewModel.setProperty("/maintenance_logs_count", data.results.length);
                } else {
                    oViewModel.setProperty("/maintenance_logs", []);
                    oViewModel.setProperty("/maintenance_logs_count", 0);
                }
            }).catch(function (error) {
                console.error("Error loading maintenance logs:", error);
                oViewModel.setProperty("/maintenance_logs", []);
                oViewModel.setProperty("/maintenance_logs_count", 0);
            });
        },

        /**
         * Load documents for equipment
         * @param {string} sEquipmentId equipment ID
         * @private
         */
        _loadDocuments: function (sEquipmentId) {
            var oViewModel = this.getView().getModel("equipment");

            // Call API to get documents
            RestModel.get("/api/equipment/equipment/" + sEquipmentId + "/documents/").then(function (data) {
                if (data && data.results) {
                    oViewModel.setProperty("/documents", data.results);
                    oViewModel.setProperty("/documents_count", data.results.length);
                } else {
                    oViewModel.setProperty("/documents", []);
                    oViewModel.setProperty("/documents_count", 0);
                }
            }).catch(function (error) {
                console.error("Error loading documents:", error);
                oViewModel.setProperty("/documents", []);
                oViewModel.setProperty("/documents_count", 0);
            });
        },

        /**
         * Navigate back to equipment list
         */
        onNavBack: function () {
            this.getOwnerComponent().getRouter().navTo("equipment");
        },

        /**
         * Refresh equipment data
         */
        onRefresh: function () {
            var oViewModel = this.getView().getModel("equipment");
            var sEquipmentId = oViewModel.getProperty("/equipment/id");
            
            if (sEquipmentId) {
                this._loadEquipmentData(sEquipmentId);
                MessageToast.show("Equipment data refreshed");
            }
        },

        /**
         * Handle edit equipment
         */
        onEditEquipment: function () {
            var oViewModel = this.getView().getModel("equipment");
            var sEquipmentId = oViewModel.getProperty("/equipment/id");
            
            MessageToast.show("Edit equipment with ID: " + sEquipmentId);
            // In a real app, navigate to edit form or open dialog
            // this.getOwnerComponent().getRouter().navTo("editEquipment", { id: sEquipmentId });
        },

        /**
         * Open create maintenance log dialog
         */
        onCreateMaintenanceLog: function () {
            var oViewModel = this.getView().getModel("equipment");
            oViewModel.setProperty("/maintenanceLogDialogMode", "create");
            
            if (!this._oMaintenanceLogDialog) {
                // Load dialog from fragment
                this._oMaintenanceLogDialog = sap.ui.xmlfragment(
                    "ssbdm.view.fragments.MaintenanceLogDialog", 
                    this
                );
                this.getView().addDependent(this._oMaintenanceLogDialog);
            }
            
            // Reset form
            var oFormModel = new JSONModel({
                equipment_id: oViewModel.getProperty("/equipment/id"),
                maintenance_type: "preventive",
                status: "pending",
                date: new Date(),
                description: "",
                cost: 0,
                parts_used: []
            });
            this._oMaintenanceLogDialog.setModel(oFormModel, "formData");
            
            // Open dialog
            this._oMaintenanceLogDialog.open();
        },

        /**
         * Handle maintenance log dialog save
         */
        onSaveMaintenanceLog: function () {
            var oDialog = this._oMaintenanceLogDialog;
            var oFormModel = oDialog.getModel("formData");
            var oFormData = oFormModel.getData();
            var oViewModel = this.getView().getModel("equipment");
            var sEquipmentId = oViewModel.getProperty("/equipment/id");
            var sMode = oViewModel.getProperty("/maintenanceLogDialogMode");
            
            // Validate form
            if (!oFormData.maintenance_type || !oFormData.status || !oFormData.description) {
                MessageBox.error("Please fill all required fields");
                return;
            }
            
            // Show busy indicator
            oViewModel.setProperty("/busy", true);
            
            if (sMode === "create") {
                // Create new maintenance log
                RestModel.post("/api/maintenance/logs/", oFormData).then(function (data) {
                    // Reload maintenance logs
                    this._loadMaintenanceLogs(sEquipmentId);
                    oViewModel.setProperty("/busy", false);
                    oDialog.close();
                    MessageToast.show("Maintenance log created successfully");
                }.bind(this)).catch(function (error) {
                    console.error("Error creating maintenance log:", error);
                    oViewModel.setProperty("/busy", false);
                    MessageBox.error("Failed to create maintenance log. Please try again.");
                });
            } else {
                // Update existing maintenance log
                var sLogId = oFormData.id;
                RestModel.put("/api/maintenance/logs/" + sLogId + "/", oFormData).then(function (data) {
                    // Reload maintenance logs
                    this._loadMaintenanceLogs(sEquipmentId);
                    oViewModel.setProperty("/busy", false);
                    oDialog.close();
                    MessageToast.show("Maintenance log updated successfully");
                }.bind(this)).catch(function (error) {
                    console.error("Error updating maintenance log:", error);
                    oViewModel.setProperty("/busy", false);
                    MessageBox.error("Failed to update maintenance log. Please try again.");
                });
            }
        },

        /**
         * Handle maintenance log dialog cancel
         */
        onCancelMaintenanceLog: function () {
            this._oMaintenanceLogDialog.close();
        },

        /**
         * Handle maintenance log press
         * @param {sap.ui.base.Event} oEvent event object
         */
        onMaintenanceLogPress: function (oEvent) {
            var oItem = oEvent.getSource();
            var oContext = oItem.getBindingContext("equipment");
            var sLogId = oContext.getProperty("id");
            
            // Navigate to maintenance log detail
            this.getOwnerComponent().getRouter().navTo("maintenanceLogDetail", {
                id: sLogId
            });
        },

        /**
         * Handle delete maintenance log
         * @param {sap.ui.base.Event} oEvent event object
         */
        onDeleteMaintenanceLog: function (oEvent) {
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("equipment");
            var sLogId = oContext.getProperty("id");
            var sDate = oContext.getProperty("date");
            var oViewModel = this.getView().getModel("equipment");
            var sEquipmentId = oViewModel.getProperty("/equipment/id");
            
            // Confirm delete
            MessageBox.confirm("Are you sure you want to delete maintenance log from " + sDate + "?", {
                title: "Confirm Delete",
                onClose: function (oAction) {
                    if (oAction === MessageBox.Action.OK) {
                        // Delete maintenance log
                        oViewModel.setProperty("/busy", true);
                        RestModel.delete("/api/maintenance/logs/" + sLogId + "/").then(function () {
                            // Reload maintenance logs
                            this._loadMaintenanceLogs(sEquipmentId);
                            oViewModel.setProperty("/busy", false);
                            MessageToast.show("Maintenance log deleted successfully");
                        }.bind(this)).catch(function (error) {
                            console.error("Error deleting maintenance log:", error);
                            oViewModel.setProperty("/busy", false);
                            MessageBox.error("Failed to delete maintenance log. Please try again.");
                        });
                    }
                }.bind(this)
            });
        },

        /**
         * Open add document dialog
         */
        onAddDocument: function () {
            MessageToast.show("Add document functionality will be implemented");
            // In a real implementation, open file upload dialog
        },

        /**
         * Handle document press
         * @param {sap.ui.base.Event} oEvent event object
         */
        onDocumentPress: function (oEvent) {
            var oItem = oEvent.getSource();
            var oContext = oItem.getBindingContext("equipment");
            var sDocumentId = oContext.getProperty("id");
            var sDocumentUrl = oContext.getProperty("file");
            
            // Open document in new tab
            window.open(sDocumentUrl, "_blank");
        },

        /**
         * Handle download document
         * @param {sap.ui.base.Event} oEvent event object
         */
        onDownloadDocument: function (oEvent) {
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("equipment");
            var sDocumentUrl = oContext.getProperty("file");
            var sName = oContext.getProperty("name");
            
            // Trigger download
            var link = document.createElement("a");
            link.href = sDocumentUrl;
            link.download = sName;
            link.click();
        },

        /**
         * Handle delete document
         * @param {sap.ui.base.Event} oEvent event object
         */
        onDeleteDocument: function (oEvent) {
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("equipment");
            var sDocumentId = oContext.getProperty("id");
            var sDocumentName = oContext.getProperty("name");
            var oViewModel = this.getView().getModel("equipment");
            var sEquipmentId = oViewModel.getProperty("/equipment/id");
            
            // Confirm delete
            MessageBox.confirm("Are you sure you want to delete document '" + sDocumentName + "'?", {
                title: "Confirm Delete",
                onClose: function (oAction) {
                    if (oAction === MessageBox.Action.OK) {
                        // Delete document
                        oViewModel.setProperty("/busy", true);
                        RestModel.delete("/api/equipment/equipment/" + sEquipmentId + "/documents/" + sDocumentId + "/").then(function () {
                            // Reload documents
                            this._loadDocuments(sEquipmentId);
                            oViewModel.setProperty("/busy", false);
                            MessageToast.show("Document deleted successfully");
                        }.bind(this)).catch(function (error) {
                            console.error("Error deleting document:", error);
                            oViewModel.setProperty("/busy", false);
                            MessageBox.error("Failed to delete document. Please try again.");
                        });
                    }
                }.bind(this)
            });
        }
    });
}); 