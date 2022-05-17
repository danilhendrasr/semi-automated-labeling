// Copyright (C) 2020-2022 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router';
import { Row, Col } from 'antd/lib/grid';
import Button from 'antd/lib/button';
import Dropdown from 'antd/lib/dropdown';
import Input from 'antd/lib/input';
import { PlusOutlined, UploadOutlined, LoadingOutlined } from '@ant-design/icons';
import Upload from 'antd/lib/upload';

import { usePrevious } from 'utils/hooks';
import { ProjectsQuery } from 'reducers/interfaces';
import { SortingComponent, ResourceFilterHOC, defaultVisibility } from 'components/resource-sorting-filtering';

import {
    localStorageRecentKeyword, localStorageRecentCapacity, predefinedFilterValues, config,
} from './projects-filter-configuration';

const FilteringComponent = ResourceFilterHOC(
    config, localStorageRecentKeyword, localStorageRecentCapacity, predefinedFilterValues,
);

interface Props {
    onImportProject(file: File): void;
    onApplyFilter(filter: string | null): void;
    onApplySorting(sorting: string | null): void;
    onApplySearch(search: string | null): void;
    query: ProjectsQuery;
    importing: boolean;
}

function TopBarComponent(props: Props): JSX.Element {
    const {
        importing, query, onApplyFilter, onApplySorting, onApplySearch, onImportProject,
    } = props;
    const [visibility, setVisibility] = useState(defaultVisibility);
    const prevImporting = usePrevious(importing);

    useEffect(() => {
        if (prevImporting && !importing) {
            onApplyFilter(query.filter);
        }
    }, [importing]);
    const history = useHistory();

    return (
        <Row className='cvat-projects-page-top-bar' justify='center' align='middle'>
            <Col md={22} lg={18} xl={16} xxl={16}>
                <div className='cvat-projects-page-filters-wrapper'>
                    <Input.Search
                        enterButton
                        onSearch={(phrase: string) => {
                            onApplySearch(phrase);
                        }}
                        defaultValue={query.search || ''}
                        className='cvat-projects-page-search-bar'
                        placeholder='Search ...'
                    />
                    <div>
                        <SortingComponent
                            visible={visibility.sorting}
                            onVisibleChange={(visible: boolean) => (
                                setVisibility({ ...defaultVisibility, sorting: visible })
                            )}
                            defaultFields={query.sort?.split(',') || ['-ID']}
                            sortingFields={['ID', 'Assignee', 'Owner', 'Status', 'Name', 'Updated date']}
                            onApplySorting={onApplySorting}
                        />
                        <FilteringComponent
                            value={query.filter}
                            predefinedVisible={visibility.predefined}
                            builderVisible={visibility.builder}
                            recentVisible={visibility.recent}
                            onPredefinedVisibleChange={(visible: boolean) => (
                                setVisibility({ ...defaultVisibility, predefined: visible })
                            )}
                            onBuilderVisibleChange={(visible: boolean) => (
                                setVisibility({ ...defaultVisibility, builder: visible })
                            )}
                            onRecentVisibleChange={(visible: boolean) => (
                                setVisibility({ ...defaultVisibility, builder: visibility.builder, recent: visible })
                            )}
                            onApplyFilter={onApplyFilter}
                        />
                    </div>
                </div>
                <div>
                    <Dropdown
                        trigger={['click']}
                        overlay={(
                            <div className='cvat-projects-page-control-buttons-wrapper'>
                                <Button
                                    id='cvat-create-project-button'
                                    className='cvat-create-project-button'
                                    type='primary'
                                    onClick={(): void => history.push('/projects/create')}
                                    icon={<PlusOutlined />}
                                >
                                    Create a new project
                                </Button>
                                <Upload
                                    accept='.zip'
                                    multiple={false}
                                    showUploadList={false}
                                    beforeUpload={(file: File): boolean => {
                                        onImportProject(file);
                                        return false;
                                    }}
                                    className='cvat-import-project'
                                >
                                    <Button
                                        className='cvat-import-project-button'
                                        type='primary'
                                        disabled={importing}
                                        icon={<UploadOutlined />}
                                    >
                                        Create from backup
                                        {importing && <LoadingOutlined className='cvat-import-project-button-loading' />}
                                    </Button>
                                </Upload>
                            </div>
                        )}
                    >
                        <Button type='primary' className='cvat-create-project-dropdown' icon={<PlusOutlined />} />
                    </Dropdown>
                </div>
            </Col>
        </Row>
    );
}

export default React.memo(TopBarComponent);
