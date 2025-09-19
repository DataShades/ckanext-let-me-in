this.ckan.module('lmi-impostor-session-table', function ($) {
    return {
        options: {
            perPage: 10,
        },
        initialize: function () {
            $.proxyAll(this, /_/);

            new simpleDatatables.DataTable(this.el[0], {
                searchable: true,
                fixedHeight: true,
                perPage: this.options.perPage,
                perPageSelect: this._getPerPageOptions(),
                fixedHeight: true,
                labels: {
                    placeholder: ckan.i18n._('Search...'),
                    perPage: "",
                    noRows: ckan.i18n._('No entries found'),
                    info: ckan.i18n._('Showing {start} to {end} of {rows} entries')
                }
            });
        },


        /**
         * Get the available options for the number of entries per page.
         *
         * Includes the default perPage option if it's not already in the list.
         *
         * @returns {number[]}
         */
        _getPerPageOptions: function() {
            const perPageOptions = [5, 10, 20, 50, 100];

            if (this.options.perPage && !perPageOptions.includes(this.options.perPage)) {
                perPageOptions.push(this.options.perPage);
                perPageOptions.sort((a, b) => a - b);
            }

            return perPageOptions;
        }
    };
});
