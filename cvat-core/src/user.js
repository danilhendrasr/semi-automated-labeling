// Copyright (C) 2019-2021 Intel Corporation
//
// SPDX-License-Identifier: MIT

(() => {
    /**
     * Class representing a user
     * @memberof module:API.cvat.classes
     * @hideconstructor
     */
    class User {
        constructor(initialData) {
            const data = {
                id: null,
                username: null,
                email: null,
                first_name: null,
                last_name: null,
                groups: null,
                last_login: null,
                date_joined: null,
                is_staff: null,
                is_superuser: null,
                is_active: null,
                email_verification_required: null,
            };

            for (const property in data) {
                if (Object.prototype.hasOwnProperty.call(data, property) && property in initialData) {
                    data[property] = initialData[property];
                }
            }

            Object.defineProperties(
                this,
                Object.freeze({
                    id: {
                        /**
                         * @name id
                         * @type {integer}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.id,
                    },
                    username: {
                        /**
                         * @name username
                         * @type {string}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.username,
                    },
                    email: {
                        /**
                         * @name email
                         * @type {string}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.email,
                    },
                    firstName: {
                        /**
                         * @name firstName
                         * @type {string}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.first_name,
                    },
                    lastName: {
                        /**
                         * @name lastName
                         * @type {string}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.last_name,
                    },
                    groups: {
                        /**
                         * @name groups
                         * @type {string[]}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => JSON.parse(JSON.stringify(data.groups)),
                    },
                    lastLogin: {
                        /**
                         * @name lastLogin
                         * @type {string}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.last_login,
                    },
                    dateJoined: {
                        /**
                         * @name dateJoined
                         * @type {string}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.date_joined,
                    },
                    isStaff: {
                        /**
                         * @name isStaff
                         * @type {boolean}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.is_staff,
                    },
                    isSuperuser: {
                        /**
                         * @name isSuperuser
                         * @type {boolean}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.is_superuser,
                    },
                    isActive: {
                        /**
                         * @name isActive
                         * @type {boolean}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => data.is_active,
                    },
                    isVerified: {
                        /**
                         * @name isVerified
                         * @type {boolean}
                         * @memberof module:API.cvat.classes.User
                         * @readonly
                         * @instance
                         */
                        get: () => !data.email_verification_required,
                    },
                }),
            );
        }

        serialize() {
            return {
                id: this.id,
                username: this.username,
                email: this.email,
                first_name: this.firstName,
                last_name: this.lastName,
                groups: this.groups,
                last_login: this.lastLogin,
                date_joined: this.dateJoined,
                is_staff: this.isStaff,
                is_superuser: this.isSuperuser,
                is_active: this.isActive,
                email_verification_required: this.isVerified,
            };
        }
    }

    module.exports = User;
})();
