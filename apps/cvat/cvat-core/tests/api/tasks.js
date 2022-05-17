// Copyright (C) 2020-2022 Intel Corporation
//
// SPDX-License-Identifier: MIT

// Setup mock for a server
jest.mock('../../src/server-proxy', () => {
    const mock = require('../mocks/server-proxy.mock');
    return mock;
});

// Initialize api
window.cvat = require('../../src/api');

const { Task } = require('../../src/session');

// Test cases
describe('Feature: get a list of tasks', () => {
    test('get all tasks', async () => {
        const result = await window.cvat.tasks.get();
        expect(Array.isArray(result)).toBeTruthy();
        expect(result).toHaveLength(6);
        for (const el of result) {
            expect(el).toBeInstanceOf(Task);
        }
    });

    test('get a task by an id', async () => {
        const result = await window.cvat.tasks.get({
            id: 3,
        });
        expect(Array.isArray(result)).toBeTruthy();
        expect(result).toHaveLength(1);
        expect(result[0]).toBeInstanceOf(Task);
        expect(result[0].id).toBe(3);
    });

    test('get a task by an unknown id', async () => {
        const result = await window.cvat.tasks.get({
            id: 50,
        });
        expect(Array.isArray(result)).toBeTruthy();
        expect(result).toHaveLength(0);
    });

    test('get a task by an invalid id', async () => {
        expect(
            window.cvat.tasks.get({
                id: '50',
            }),
        ).rejects.toThrow(window.cvat.exceptions.ArgumentError);
    });

    test('get tasks by filters', async () => {
        const result = await window.cvat.tasks.get({
            filter: '{"and":[{"==":[{"var":"filter"},"interpolation"]}]}',
        });
        expect(result).toBeInstanceOf(Array);
    });

    test('get tasks by invalid query', async () => {
        expect(
            window.cvat.tasks.get({
                unknown: '5',
            }),
        ).rejects.toThrow(window.cvat.exceptions.ArgumentError);
    });
});

describe('Feature: save a task', () => {
    test('save some changed fields in a task', async () => {
        let result = await window.cvat.tasks.get({
            id: 2,
        });

        result[0].bugTracker = 'newBugTracker';
        result[0].name = 'New Task Name';
        result[0].projectId = 6;

        result[0].save();

        result = await window.cvat.tasks.get({
            id: 2,
        });

        expect(result[0].bugTracker).toBe('newBugTracker');
        expect(result[0].name).toBe('New Task Name');
        expect(result[0].projectId).toBe(6);
    });

    test('save some new labels in a task', async () => {
        let result = await window.cvat.tasks.get({
            id: 2,
        });

        const labelsLength = result[0].labels.length;
        const newLabel = new window.cvat.classes.Label({
            name: 'My boss\'s car',
            attributes: [
                {
                    default_value: 'false',
                    input_type: 'checkbox',
                    mutable: true,
                    name: 'parked',
                    values: ['false'],
                },
            ],
        });

        result[0].labels = [...result[0].labels, newLabel];
        result[0].save();

        result = await window.cvat.tasks.get({
            id: 2,
        });

        expect(result[0].labels).toHaveLength(labelsLength + 1);
        const appendedLabel = result[0].labels.filter((el) => el.name === 'My boss\'s car');
        expect(appendedLabel).toHaveLength(1);
        expect(appendedLabel[0].attributes).toHaveLength(1);
        expect(appendedLabel[0].attributes[0].name).toBe('parked');
        expect(appendedLabel[0].attributes[0].defaultValue).toBe('false');
        expect(appendedLabel[0].attributes[0].mutable).toBe(true);
        expect(appendedLabel[0].attributes[0].inputType).toBe('checkbox');
    });

    test('save new task without an id', async () => {
        const task = new window.cvat.classes.Task({
            name: 'New Task',
            labels: [
                {
                    name: 'My boss\'s car',
                    attributes: [
                        {
                            default_value: 'false',
                            input_type: 'checkbox',
                            mutable: true,
                            name: 'parked',
                            values: ['false'],
                        },
                    ],
                },
            ],
            bug_tracker: 'bug tracker value',
            image_quality: 50,
        });

        const result = await task.save();
        expect(typeof result.id).toBe('number');
    });

    test('save new task in project', async () => {
        const task = new window.cvat.classes.Task({
            name: 'New Task',
            project_id: 2,
            bug_tracker: 'bug tracker value',
            image_quality: 50,
            z_order: true,
        });

        const result = await task.save();
        expect(result.projectId).toBe(2);
    });
});

describe('Feature: delete a task', () => {
    test('delete a task', async () => {
        let result = await window.cvat.tasks.get({
            id: 3,
        });

        await result[0].delete();
        result = await window.cvat.tasks.get({
            id: 3,
        });

        expect(Array.isArray(result)).toBeTruthy();
        expect(result).toHaveLength(0);
    });
});

describe('Feature: delete a label', () => {
    test('delete a label', async () => {
        let result = await window.cvat.tasks.get({
            id: 100,
        });

        const labelsLength = result[0].labels.length;
        const deletedLabels = result[0].labels.filter((el) => el.name !== 'person');
        result[0].labels = deletedLabels;
        result[0].save();
        result = await window.cvat.tasks.get({
            id: 100,
        });
        expect(result[0].labels).toHaveLength(labelsLength - 1);
    });
});
