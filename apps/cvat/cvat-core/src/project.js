// Copyright (C) 2019-2021 Intel Corporation
//
// SPDX-License-Identifier: MIT

(() => {
    const PluginRegistry = require('./plugins');
    const { ArgumentError } = require('./exceptions');
    const { Label } = require('./labels');
    const User = require('./user');
    const { FieldUpdateTrigger } = require('./common');

    /**
     * Class representing a project
     * @memberof module:API.cvat.classes
     */
    class Project {
        /**
         * In a fact you need use the constructor only if you want to create a project
         * @param {object} initialData - Object which is used for initialization
         * <br> It can contain keys:
         * <br> <li style="margin-left: 10px;"> name
         * <br> <li style="margin-left: 10px;"> labels
         */
        constructor(initialData) {
            const data = {
                id: undefined,
                name: undefined,
                status: undefined,
                assignee: undefined,
                owner: undefined,
                bug_tracker: undefined,
                created_date: undefined,
                updated_date: undefined,
                task_subsets: undefined,
                training_project: undefined,
                task_ids: undefined,
                dimension: undefined,
            };

            const updateTrigger = new FieldUpdateTrigger();

            for (const property in data) {
                if (Object.prototype.hasOwnProperty.call(data, property) && property in initialData) {
                    data[property] = initialData[property];
                }
            }

            data.labels = [];

            if (Array.isArray(initialData.labels)) {
                for (const label of initialData.labels) {
                    const classInstance = new Label(label);
                    data.labels.push(classInstance);
                }
            }

            if (typeof initialData.training_project === 'object') {
                data.training_project = { ...initialData.training_project };
            }

            Object.defineProperties(
                this,
                Object.freeze({
                    /**
                     * @name id
                     * @type {integer}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    id: {
                        get: () => data.id,
                    },
                    /**
                     * @name name
                     * @type {string}
                     * @memberof module:API.cvat.classes.Project
                     * @instance
                     * @throws {module:API.cvat.exceptions.ArgumentError}
                     */
                    name: {
                        get: () => data.name,
                        set: (value) => {
                            if (!value.trim().length) {
                                throw new ArgumentError('Value must not be empty');
                            }
                            data.name = value;
                            updateTrigger.update('name');
                        },
                    },

                    /**
                     * @name status
                     * @type {module:API.cvat.enums.TaskStatus}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    status: {
                        get: () => data.status,
                    },
                    /**
                     * Instance of a user who was assigned for the project
                     * @name assignee
                     * @type {module:API.cvat.classes.User}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    assignee: {
                        get: () => data.assignee,
                        set: (assignee) => {
                            if (assignee !== null && !(assignee instanceof User)) {
                                throw new ArgumentError('Value must be a user instance');
                            }
                            data.assignee = assignee;
                            updateTrigger.update('assignee');
                        },
                    },
                    /**
                     * Instance of a user who has created the project
                     * @name owner
                     * @type {module:API.cvat.classes.User}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    owner: {
                        get: () => data.owner,
                    },
                    /**
                     * @name bugTracker
                     * @type {string}
                     * @memberof module:API.cvat.classes.Project
                     * @instance
                     * @throws {module:API.cvat.exceptions.ArgumentError}
                     */
                    bugTracker: {
                        get: () => data.bug_tracker,
                        set: (tracker) => {
                            data.bug_tracker = tracker;
                            updateTrigger.update('bugTracker');
                        },
                    },
                    /**
                     * @name createdDate
                     * @type {string}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    createdDate: {
                        get: () => data.created_date,
                    },
                    /**
                     * @name updatedDate
                     * @type {string}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    updatedDate: {
                        get: () => data.updated_date,
                    },
                    /**
                     * Dimesion of the tasks in the project, if no task dimension is null
                     * @name dimension
                     * @type {string}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    dimension: {
                        get: () => data.dimension,
                    },
                    /**
                     * After project has been created value can be appended only.
                     * @name labels
                     * @type {module:API.cvat.classes.Label[]}
                     * @memberof module:API.cvat.classes.Project
                     * @instance
                     * @throws {module:API.cvat.exceptions.ArgumentError}
                     */
                    labels: {
                        get: () => [...data.labels],
                        set: (labels) => {
                            if (!Array.isArray(labels)) {
                                throw new ArgumentError('Value must be an array of Labels');
                            }

                            if (!Array.isArray(labels) || labels.some((label) => !(label instanceof Label))) {
                                throw new ArgumentError(
                                    `Each array value must be an instance of Label. ${typeof label} was found`,
                                );
                            }

                            const IDs = labels.map((_label) => _label.id);
                            const deletedLabels = data.labels.filter((_label) => !IDs.includes(_label.id));
                            deletedLabels.forEach((_label) => {
                                _label.deleted = true;
                            });

                            data.labels = [...deletedLabels, ...labels];
                            updateTrigger.update('labels');
                        },
                    },
                    /**
                     * Subsets array for related tasks
                     * @name subsets
                     * @type {string[]}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    subsets: {
                        get: () => [...data.task_subsets],
                    },
                    /**
                     * Training project associated with this annotation project
                     * This is a simple object which contains
                     * keys like host, username, password, enabled, project_class
                     * @name trainingProject
                     * @type {object}
                     * @memberof module:API.cvat.classes.Project
                     * @readonly
                     * @instance
                     */
                    trainingProject: {
                        get: () => {
                            if (typeof data.training_project === 'object') {
                                return { ...data.training_project };
                            }
                            return data.training_project;
                        },
                        set: (updatedProject) => {
                            if (typeof training === 'object') {
                                data.training_project = { ...updatedProject };
                            } else {
                                data.training_project = updatedProject;
                            }
                            updateTrigger.update('trainingProject');
                        },
                    },
                    _internalData: {
                        get: () => data,
                    },
                    _updateTrigger: {
                        get: () => updateTrigger,
                    },
                }),
            );

            // When we call a function, for example: project.annotations.get()
            // In the method get we lose the project context
            // So, we need return it
            this.annotations = {
                exportDataset: Object.getPrototypeOf(this).annotations.exportDataset.bind(this),
                importDataset: Object.getPrototypeOf(this).annotations.importDataset.bind(this),
            };
        }

        /**
         * Get the first frame of the first task of a project for preview
         * @method preview
         * @memberof Project
         * @returns {string} - jpeg encoded image
         * @instance
         * @async
         * @throws {module:API.cvat.exceptions.PluginError}
         * @throws {module:API.cvat.exceptions.ServerError}
         * @throws {module:API.cvat.exceptions.ArgumentError}
         */
        async preview() {
            const result = await PluginRegistry.apiWrapper.call(this, Project.prototype.preview);
            return result;
        }

        /**
         * Method updates data of a created project or creates new project from scratch
         * @method save
         * @returns {module:API.cvat.classes.Project}
         * @memberof module:API.cvat.classes.Project
         * @readonly
         * @instance
         * @async
         * @throws {module:API.cvat.exceptions.ServerError}
         * @throws {module:API.cvat.exceptions.PluginError}
         */
        async save() {
            const result = await PluginRegistry.apiWrapper.call(this, Project.prototype.save);
            return result;
        }

        /**
         * Method deletes a project from a server
         * @method delete
         * @memberof module:API.cvat.classes.Project
         * @readonly
         * @instance
         * @async
         * @throws {module:API.cvat.exceptions.ServerError}
         * @throws {module:API.cvat.exceptions.PluginError}
         */
        async delete() {
            const result = await PluginRegistry.apiWrapper.call(this, Project.prototype.delete);
            return result;
        }

        /**
         * Method makes a backup of a project
         * @method export
         * @memberof module:API.cvat.classes.Project
         * @readonly
         * @instance
         * @async
         * @throws {module:API.cvat.exceptions.ServerError}
         * @throws {module:API.cvat.exceptions.PluginError}
         * @returns {string} URL to get result archive
         */
        async backup() {
            const result = await PluginRegistry.apiWrapper.call(this, Project.prototype.backup);
            return result;
        }

        /**
         * Method restores a project from a backup
         * @method restore
         * @memberof module:API.cvat.classes.Project
         * @readonly
         * @instance
         * @async
         * @throws {module:API.cvat.exceptions.ServerError}
         * @throws {module:API.cvat.exceptions.PluginError}
         * @returns {number} ID of the imported project
         */
        static async restore(file) {
            const result = await PluginRegistry.apiWrapper.call(this, Project.restore, file);
            return result;
        }
    }

    Object.defineProperties(
        Project.prototype,
        Object.freeze({
            annotations: Object.freeze({
                value: {
                    async exportDataset(format, saveImages, customName = '') {
                        const result = await PluginRegistry.apiWrapper.call(
                            this,
                            Project.prototype.annotations.exportDataset,
                            format,
                            saveImages,
                            customName,
                        );
                        return result;
                    },
                    async importDataset(format, file, updateStatusCallback = null) {
                        const result = await PluginRegistry.apiWrapper.call(
                            this,
                            Project.prototype.annotations.importDataset,
                            format,
                            file,
                            updateStatusCallback,
                        );
                        return result;
                    },
                },
                writable: true,
            }),
        }),
    );

    module.exports = {
        Project,
    };
})();
