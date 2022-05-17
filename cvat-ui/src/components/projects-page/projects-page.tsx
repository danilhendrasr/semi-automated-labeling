// Copyright (C) 2020-2022 Intel Corporation
//
// SPDX-License-Identifier: MIT

import './styles.scss';
import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router';
import { useDispatch, useSelector } from 'react-redux';
import Spin from 'antd/lib/spin';

import { CombinedState, Indexable } from 'reducers/interfaces';
import { getProjectsAsync, restoreProjectAsync } from 'actions/projects-actions';
import FeedbackComponent from 'components/feedback/feedback';
import { updateHistoryFromQuery } from 'components/resource-sorting-filtering';
import ImportDatasetModal from 'components/import-dataset-modal/import-dataset-modal';
import EmptyListComponent from './empty-list';
import TopBarComponent from './top-bar';
import ProjectListComponent from './project-list';

export default function ProjectsPageComponent(): JSX.Element {
    const dispatch = useDispatch();
    const history = useHistory();
    const fetching = useSelector((state: CombinedState) => state.projects.fetching);
    const count = useSelector((state: CombinedState) => state.projects.current.length);
    const query = useSelector((state: CombinedState) => state.projects.gettingQuery);
    const tasksQuery = useSelector((state: CombinedState) => state.projects.tasksGettingQuery);
    const importing = useSelector((state: CombinedState) => state.projects.restoring);
    const [isMounted, setIsMounted] = useState(false);
    const anySearch = Object.keys(query).some((value: string) => value !== 'page' && (query as any)[value] !== null);

    const queryParams = new URLSearchParams(history.location.search);
    const updatedQuery = { ...query };
    for (const key of Object.keys(updatedQuery)) {
        (updatedQuery as Indexable)[key] = queryParams.get(key) || null;
        if (key === 'page') {
            updatedQuery.page = updatedQuery.page ? +updatedQuery.page : 1;
        }
    }

    useEffect(() => {
        dispatch(getProjectsAsync({ ...updatedQuery }));
        setIsMounted(true);
    }, []);

    useEffect(() => {
        if (isMounted) {
            history.replace({
                search: updateHistoryFromQuery(query),
            });
        }
    }, [query]);

    const content = count ? <ProjectListComponent /> : <EmptyListComponent notFound={anySearch} />;

    return (
        <div className='cvat-projects-page'>
            <TopBarComponent
                onApplySearch={(search: string | null) => {
                    dispatch(
                        getProjectsAsync({
                            ...query,
                            search,
                            page: 1,
                        }, { ...tasksQuery, page: 1 }),
                    );
                }}
                onApplyFilter={(filter: string | null) => {
                    dispatch(
                        getProjectsAsync({
                            ...query,
                            filter,
                            page: 1,
                        }, { ...tasksQuery, page: 1 }),
                    );
                }}
                onApplySorting={(sorting: string | null) => {
                    dispatch(
                        getProjectsAsync({
                            ...query,
                            sort: sorting,
                            page: 1,
                        }, { ...tasksQuery, page: 1 }),
                    );
                }}
                query={updatedQuery}
                onImportProject={(file: File) => dispatch(restoreProjectAsync(file))}
                importing={importing}
            />
            { fetching ? (
                <div className='cvat-empty-project-list'>
                    <Spin size='large' className='cvat-spinner' />
                </div>
            ) : content }
            <FeedbackComponent />
            <ImportDatasetModal />
        </div>
    );
}
