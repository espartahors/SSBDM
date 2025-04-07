sap.ui.define([
    "sap/ui/core/UIComponent",
    "sap/ui/Device",
    "sap/ui/model/json/JSONModel",
    "sap/ui/model/odata/v2/ODataModel"
], function(UIComponent, Device, JSONModel, ODataModel) {
    "use strict";

    return UIComponent.extend("ssbdm.Component", {
        metadata: {
            manifest: "json"
        },

        /**
         * The component is initialized by UI5 automatically during the startup
         * @public
         * @override
         */
        init: function() {
            // Call the base component's init function
            UIComponent.prototype.init.apply(this, arguments);

            // Set device model
            this.setDeviceModel();

            // Initialize user model
            this.setUserModel();

            // Enable routing
            this.getRouter().initialize();
        },

        /**
         * Set the device model
         * @private
         */
        setDeviceModel: function() {
            var oDeviceModel = new JSONModel(Device);
            oDeviceModel.setDefaultBindingMode("OneWay");
            this.setModel(oDeviceModel, "device");
        },

        /**
         * Set the user model
         * @private
         */
        setUserModel: function() {
            // For demo purposes, we use a static user model
            var oUserModel = new JSONModel({
                username: "Demo User",
                isAdmin: true,
                isStaff: true,
                isMaintenanceUser: true,
                userId: "1",
                permissions: ["can_manage_maintenance", "can_manage_tasks", "can_manage_documents", "can_view_audit_logs"]
            });
            this.setModel(oUserModel, "userInfo");
        },

        /**
         * Create REST models for API consumption
         * @private
         */
        createRESTModels: function() {
            // Equipment API
            this.setModel(new JSONModel(), "equipmentList");
            this.setModel(new JSONModel(), "areaList");
            this.setModel(new JSONModel(), "techSpecList");

            // Maintenance API
            this.setModel(new JSONModel(), "maintenanceLogList");
            this.setModel(new JSONModel(), "maintenanceTaskList");
            this.setModel(new JSONModel(), "maintenancePlanList");
            this.setModel(new JSONModel(), "documentList");
            this.setModel(new JSONModel(), "auditLogList");

            // Spare Parts API
            this.setModel(new JSONModel(), "sparePartList");
            this.setModel(new JSONModel(), "categoryList");
            this.setModel(new JSONModel(), "transactionList");
        }
    });
}); 