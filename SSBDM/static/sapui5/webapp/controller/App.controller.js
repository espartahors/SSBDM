sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast",
    "sap/f/Menu",
    "sap/m/MenuItem"
], function (Controller, JSONModel, MessageToast, Menu, MenuItem) {
    "use strict";

    return Controller.extend("ssbdm.controller.App", {
        onInit: function () {
            var oViewModel = new JSONModel({
                selectedKey: "home",
                navigation: [
                    {
                        title: "Home",
                        icon: "sap-icon://home",
                        key: "home"
                    },
                    {
                        title: "Equipment",
                        icon: "sap-icon://machine",
                        key: "equipment"
                    },
                    {
                        title: "Maintenance",
                        icon: "sap-icon://wrench",
                        key: "maintenance"
                    },
                    {
                        title: "Spare Parts",
                        icon: "sap-icon://product",
                        key: "spareParts"
                    }
                ],
                fixedNavigation: [
                    {
                        title: "Settings",
                        icon: "sap-icon://settings",
                        key: "settings"
                    },
                    {
                        title: "Help",
                        icon: "sap-icon://sys-help",
                        key: "help"
                    }
                ]
            });

            this.getView().setModel(oViewModel);

            // Initialize user menu
            this._initUserMenu();

            // Subscribe to routing events
            var oRouter = this.getOwnerComponent().getRouter();
            oRouter.attachRouteMatched(this._onRoutePatternMatched, this);
        },

        /**
         * Handler for route pattern matched
         * @param {sap.ui.base.Event} oEvent route matched event
         * @private
         */
        _onRoutePatternMatched: function (oEvent) {
            var sRouteName = oEvent.getParameter("name"),
                oViewModel = this.getView().getModel();

            // Update selected key based on route
            oViewModel.setProperty("/selectedKey", sRouteName);
        },

        /**
         * Initialize user menu
         * @private
         */
        _initUserMenu: function () {
            // Create menu instance
            if (!this._oUserMenu) {
                this._oUserMenu = new Menu({
                    items: [
                        new MenuItem({
                            text: "Profile",
                            icon: "sap-icon://person-placeholder",
                            press: this.onUserProfilePress.bind(this)
                        }),
                        new MenuItem({
                            text: "Logout",
                            icon: "sap-icon://log",
                            press: this.onUserLogoutPress.bind(this)
                        })
                    ]
                });

                this.getView().addDependent(this._oUserMenu);
            }
        },

        /**
         * Handler for user menu button press
         * @param {sap.ui.base.Event} oEvent button press event
         */
        onUserMenuPress: function (oEvent) {
            // Toggle menu
            var oButton = oEvent.getSource();

            if (this._oUserMenu.isOpen()) {
                this._oUserMenu.close();
            } else {
                this._oUserMenu.openBy(oButton);
            }
        },

        /**
         * Handler for user profile menu item press
         */
        onUserProfilePress: function () {
            MessageToast.show("User profile pressed");
        },

        /**
         * Handler for user logout menu item press
         */
        onUserLogoutPress: function () {
            MessageToast.show("Logout pressed");
        },

        /**
         * Handler for side navigation toggle button press
         */
        onSideNavTogglePress: function () {
            var oSideNavigation = this.getView().byId("sideNavigation");
            var bExpanded = oSideNavigation.getExpanded();

            oSideNavigation.setExpanded(!bExpanded);
        },

        /**
         * Handler for side navigation item select
         * @param {sap.ui.base.Event} oEvent item select event
         */
        onNavItemSelect: function (oEvent) {
            var oItem = oEvent.getParameter("item");
            var sKey = oItem.getKey();

            // Navigate to the selected route
            this.getOwnerComponent().getRouter().navTo(sKey);
        }
    });
}); 