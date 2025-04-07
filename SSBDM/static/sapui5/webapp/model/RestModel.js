sap.ui.define([
    "sap/ui/model/json/JSONModel",
    "sap/ui/model/Filter",
    "sap/ui/model/FilterOperator",
    "sap/m/MessageBox"
], function(JSONModel, Filter, FilterOperator, MessageBox) {
    "use strict";

    return {
        /**
         * Make a GET request to a REST API endpoint
         * @param {string} endpoint - API endpoint without leading slash
         * @param {object} [queryParams] - Optional query parameters
         * @returns {Promise} Promise object with response data
         */
        get: function(endpoint, queryParams) {
            var url = this._formatUrl(endpoint, queryParams);
            
            return new Promise(function(resolve, reject) {
                $.ajax({
                    url: url,
                    type: "GET",
                    contentType: "application/json",
                    success: function(data) {
                        resolve(data);
                    },
                    error: function(xhr, status, error) {
                        this._handleError(xhr, status, error);
                        reject(error);
                    }.bind(this)
                });
            }.bind(this));
        },

        /**
         * Make a POST request to a REST API endpoint
         * @param {string} endpoint - API endpoint without leading slash
         * @param {object} data - Data to be sent in the request body
         * @returns {Promise} Promise object with response data
         */
        post: function(endpoint, data) {
            var url = this._formatUrl(endpoint);
            
            return new Promise(function(resolve, reject) {
                $.ajax({
                    url: url,
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify(data),
                    dataType: "json",
                    success: function(data) {
                        resolve(data);
                    },
                    error: function(xhr, status, error) {
                        this._handleError(xhr, status, error);
                        reject(error);
                    }.bind(this)
                });
            }.bind(this));
        },

        /**
         * Make a PUT request to a REST API endpoint
         * @param {string} endpoint - API endpoint without leading slash
         * @param {object} data - Data to be sent in the request body
         * @returns {Promise} Promise object with response data
         */
        put: function(endpoint, data) {
            var url = this._formatUrl(endpoint);
            
            return new Promise(function(resolve, reject) {
                $.ajax({
                    url: url,
                    type: "PUT",
                    contentType: "application/json",
                    data: JSON.stringify(data),
                    dataType: "json",
                    success: function(data) {
                        resolve(data);
                    },
                    error: function(xhr, status, error) {
                        this._handleError(xhr, status, error);
                        reject(error);
                    }.bind(this)
                });
            }.bind(this));
        },

        /**
         * Make a PATCH request to a REST API endpoint
         * @param {string} endpoint - API endpoint without leading slash
         * @param {object} data - Data to be sent in the request body
         * @returns {Promise} Promise object with response data
         */
        patch: function(endpoint, data) {
            var url = this._formatUrl(endpoint);
            
            return new Promise(function(resolve, reject) {
                $.ajax({
                    url: url,
                    type: "PATCH",
                    contentType: "application/json",
                    data: JSON.stringify(data),
                    dataType: "json",
                    success: function(data) {
                        resolve(data);
                    },
                    error: function(xhr, status, error) {
                        this._handleError(xhr, status, error);
                        reject(error);
                    }.bind(this)
                });
            }.bind(this));
        },

        /**
         * Make a DELETE request to a REST API endpoint
         * @param {string} endpoint - API endpoint without leading slash
         * @returns {Promise} Promise object with response data
         */
        delete: function(endpoint) {
            var url = this._formatUrl(endpoint);
            
            return new Promise(function(resolve, reject) {
                $.ajax({
                    url: url,
                    type: "DELETE",
                    contentType: "application/json",
                    success: function(data) {
                        resolve(data || {});
                    },
                    error: function(xhr, status, error) {
                        this._handleError(xhr, status, error);
                        reject(error);
                    }.bind(this)
                });
            }.bind(this));
        },

        /**
         * Load data into a JSONModel
         * @param {string} endpoint - API endpoint without leading slash
         * @param {sap.ui.model.json.JSONModel} model - Model to load data into
         * @param {object} [queryParams] - Optional query parameters
         * @returns {Promise} Promise object with model data
         */
        loadModel: function(endpoint, model, queryParams) {
            return this.get(endpoint, queryParams).then(function(data) {
                model.setData(data);
                return data;
            });
        },

        /**
         * Format URL with query parameters
         * @private
         * @param {string} endpoint - API endpoint without leading slash
         * @param {object} [queryParams] - Optional query parameters
         * @returns {string} Formatted URL
         */
        _formatUrl: function(endpoint, queryParams) {
            var url = endpoint;
            
            // Add query parameters if provided
            if (queryParams) {
                var queryString = Object.keys(queryParams)
                    .filter(function(key) {
                        return queryParams[key] !== undefined && queryParams[key] !== null;
                    })
                    .map(function(key) {
                        return encodeURIComponent(key) + "=" + encodeURIComponent(queryParams[key]);
                    })
                    .join("&");
                
                if (queryString) {
                    url += (url.indexOf("?") === -1 ? "?" : "&") + queryString;
                }
            }
            
            return url;
        },

        /**
         * Handle error response from API
         * @private
         * @param {object} xhr - XMLHttpRequest object
         * @param {string} status - Status text
         * @param {string} error - Error message
         */
        _handleError: function(xhr, status, error) {
            var errorMessage = "An error occurred while communicating with the server.";
            
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                errorMessage = xhr.responseJSON.detail;
            } else if (xhr.responseText) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (response.detail) {
                        errorMessage = response.detail;
                    } else if (typeof response === "string") {
                        errorMessage = response;
                    }
                } catch (e) {
                    // If responseText is not valid JSON, use it directly if not too long
                    if (xhr.responseText.length < 100) {
                        errorMessage = xhr.responseText;
                    }
                }
            }
            
            // Log error to console for debugging
            console.error("API Error:", status, error, xhr.responseText);
            
            // Show error message to user
            MessageBox.error(errorMessage);
        }
    };
}); 