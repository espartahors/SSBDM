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
    "../../model/RestModel",
    "../../model/formatter"
], function (Controller, JSONModel, Filter, FilterOperator, Sorter, MessageToast,
             MessageBox, Dialog, Button, List, StandardListItem, RestModel, formatter) {
    "use strict";

    return Controller.extend("ssbdm.controller.spareparts.SpareParts", {
        formatter: formatter,
        
        onInit: function () {
            // Set up view model
            var oViewModel = new JSONModel({
                headerExpanded: true,
                spareParts: [],
                sparePartsCount: 0,
                busy: false,
                categoryOptions: [
                    { key: "", text: "All Categories" }
                ],
                stockOptions: [
                    { key: "", text: "All" },
                    { key: "in_stock", text: "In Stock" },
                    { key: "low_stock", text: "Low Stock" },
                    { key: "out_of_stock", text: "Out of Stock" }
                ]
            });
            this.getView().setModel(oViewModel, "view");

            // Initialize filters
            this._filters = {
                category: [],
                stock: [],
                search: []
            };

            // Load initial data
            this._loadSpareParts();
            this._loadCategories();

            // Register for route matched event
            this.getOwnerComponent().getRouter().getRoute("spareParts").attachPatternMatched(this._onRouteMatched, this);
        },

        /**
         * Handler for route matched event
         * @param {sap.ui.base.Event} oEvent event object
         * @private
         */
        _onRouteMatched: function (oEvent) {
            // Refresh data when navigating to this view
            this._loadSpareParts();
        },

        /**
         * Load spare parts from API
         * @private
         */
        _loadSpareParts: function () {
            var oViewModel = this.getView().getModel("view");
            oViewModel.setProperty("/busy", true);

            // Call API to get spare parts
            RestModel.get("/api/spare-parts/parts/").then(function (data) {
                // Update model with spare parts data
                if (data && data.results) {
                    oViewModel.setProperty("/spareParts", data.results);
                    oViewModel.setProperty("/sparePartsCount", data.results.length);
                } else {
                    oViewModel.setProperty("/spareParts", []);
                    oViewModel.setProperty("/sparePartsCount", 0);
                }
                oViewModel.setProperty("/busy", false);
            }).catch(function (error) {
                console.error("Error loading spare parts:", error);
                oViewModel.setProperty("/busy", false);
                MessageBox.error("Failed to load spare parts. Please try again.");
            });
        },

        /**
         * Load categories from API
         * @private
         */
        _loadCategories: function () {
            var oViewModel = this.getView().getModel("view");

            // Call API to get categories
            RestModel.get("/api/spare-parts/categories/").then(function (data) {
                var aCategoryOptions = [{ key: "", text: "All Categories" }];
                
                // Add all categories to options
                if (data && data.results) {
                    data.results.forEach(function (category) {
                        aCategoryOptions.push({
                            key: category.id.toString(),
                            text: category.name
                        });
                    });
                }
                
                oViewModel.setProperty("/categoryOptions", aCategoryOptions);
            }).catch(function (error) {
                console.error("Error loading categories:", error);
            });
        },

        /**
         * Navigate back to previous page
         */
        onNavBack: function () {
            this.getOwnerComponent().getRouter().navTo("home");
        },

        /**
         * Navigate to transactions page
         */
        onNavigateToTransactions: function () {
            this.getOwnerComponent().getRouter().navTo("transactions");
        },

        /**
         * Create new spare part
         */
        onCreateSparePart: function () {
            MessageToast.show("Create spare part functionality will be implemented");
            // In a real app, navigate to create form or open dialog
            // this.getOwnerComponent().getRouter().navTo("sparePartCreate");
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
         * Refresh spare parts
         */
        onRefresh: function () {
            this._loadSpareParts();
            MessageToast.show("Spare parts refreshed");
        },

        /**
         * Reset all filters
         */
        onResetFilters: function () {
            // Reset filter values
            this.byId("searchField").setValue("");
            this.byId("categoryFilter").setSelectedKey("");
            this.byId("stockFilter").setSelectedKey("");
            
            // Clear all filters
            this._filters = {
                category: [],
                stock: [],
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
                aSearchFilters.push(new Filter("name", FilterOperator.Contains, sQuery));
                aSearchFilters.push(new Filter("part_number", FilterOperator.Contains, sQuery));
                aSearchFilters.push(new Filter("description", FilterOperator.Contains, sQuery));

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
            if (sFilterId.indexOf("categoryFilter") !== -1) {
                this._applyCategoryFilter(sSelectedKey);
            } else if (sFilterId.indexOf("stockFilter") !== -1) {
                this._applyStockFilter(sSelectedKey);
            }
        },

        /**
         * Apply category filter
         * @param {string} sCategoryKey selected category key
         * @private
         */
        _applyCategoryFilter: function (sCategoryKey) {
            if (sCategoryKey) {
                this._filters.category = [new Filter("category", FilterOperator.EQ, sCategoryKey)];
            } else {
                this._filters.category = [];
            }

            // Apply filters
            this._applyFilters();
        },

        /**
         * Apply stock filter
         * @param {string} sStockKey selected stock key
         * @private
         */
        _applyStockFilter: function (sStockKey) {
            if (sStockKey) {
                this._filters.stock = [new Filter("status", FilterOperator.EQ, sStockKey)];
            } else {
                this._filters.stock = [];
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
                this._filters.category, 
                this._filters.stock, 
                this._filters.search
            );
            
            // Get table binding and apply filters
            var oTable = this.byId("sparePartsTable");
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
                            new StandardListItem({ title: "Part Number", type: "Active", custom: { path: "part_number", descending: false } }),
                            new StandardListItem({ title: "Name", type: "Active", custom: { path: "name", descending: false } }),
                            new StandardListItem({ title: "Category", type: "Active", custom: { path: "category_name", descending: false } }),
                            new StandardListItem({ title: "Stock Quantity (High to Low)", type: "Active", custom: { path: "stock_quantity", descending: true } }),
                            new StandardListItem({ title: "Stock Quantity (Low to High)", type: "Active", custom: { path: "stock_quantity", descending: false } }),
                            new StandardListItem({ title: "Price (High to Low)", type: "Active", custom: { path: "unit_price", descending: true } }),
                            new StandardListItem({ title: "Price (Low to High)", type: "Active", custom: { path: "unit_price", descending: false } })
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
            var oTable = this.byId("sparePartsTable");
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
         * Handle spare part item press
         * @param {sap.ui.base.Event} oEvent event object
         */
        onSparePartPress: function (oEvent) {
            var oItem = oEvent.getSource();
            var oContext = oItem.getBindingContext("view");
            var sSparePartId = oContext.getProperty("id");
            
            // Navigate to spare part detail
            this.getOwnerComponent().getRouter().navTo("sparePartDetail", {
                id: sSparePartId
            });
        },

        /**
         * Handle create transaction
         * @param {sap.ui.base.Event} oEvent event object
         */
        onCreateTransaction: function (oEvent) {
            // Stop event propagation to prevent navigation
            oEvent.stopPropagation();
            
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("view");
            var sSparePartId = oContext.getProperty("id");
            var sSparePartName = oContext.getProperty("name");
            
            MessageToast.show("Create transaction for " + sSparePartName);
            // In a real app, navigate to create transaction form or open dialog
            // this.getOwnerComponent().getRouter().navTo("transactionCreate", { partId: sSparePartId });
        },

        /**
         * Handle edit spare part
         * @param {sap.ui.base.Event} oEvent event object
         */
        onEditSparePart: function (oEvent) {
            // Stop event propagation to prevent navigation
            oEvent.stopPropagation();
            
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("view");
            var sSparePartId = oContext.getProperty("id");
            
            MessageToast.show("Edit spare part with ID: " + sSparePartId);
            // In a real app, navigate to edit form or open dialog
            // this.getOwnerComponent().getRouter().navTo("sparePartEdit", { id: sSparePartId });
        },

        /**
         * Handle delete spare part
         * @param {sap.ui.base.Event} oEvent event object
         */
        onDeleteSparePart: function (oEvent) {
            // Stop event propagation to prevent navigation
            oEvent.stopPropagation();
            
            var oButton = oEvent.getSource();
            var oContext = oButton.getBindingContext("view");
            var sSparePartId = oContext.getProperty("id");
            var sSparePartName = oContext.getProperty("name");
            
            // Confirm delete
            MessageBox.confirm("Are you sure you want to delete spare part '" + sSparePartName + "'?", {
                title: "Confirm Delete",
                onClose: function (oAction) {
                    if (oAction === MessageBox.Action.OK) {
                        // Delete spare part
                        this._deleteSparePart(sSparePartId);
                    }
                }.bind(this)
            });
        },

        /**
         * Delete spare part
         * @param {string} sSparePartId spare part ID
         * @private
         */
        _deleteSparePart: function (sSparePartId) {
            var oViewModel = this.getView().getModel("view");
            oViewModel.setProperty("/busy", true);
            
            // Call API to delete spare part
            RestModel.delete("/api/spare-parts/parts/" + sSparePartId + "/").then(function () {
                // Reload spare parts
                this._loadSpareParts();
                MessageToast.show("Spare part deleted successfully");
            }.bind(this)).catch(function (error) {
                console.error("Error deleting spare part:", error);
                oViewModel.setProperty("/busy", false);
                MessageBox.error("Failed to delete spare part. Please try again.");
            });
        },

        /**
         * Handle table update finished
         * @param {sap.ui.base.Event} oEvent event object
         */
        onUpdateFinished: function (oEvent) {
            var iTotalItems = oEvent.getParameter("total");
            var oViewModel = this.getView().getModel("view");
            
            // Update spare part count
            oViewModel.setProperty("/sparePartsCount", iTotalItems);
        }
    });
}); 