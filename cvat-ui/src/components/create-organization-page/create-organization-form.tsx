// Copyright (C) 2021 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { useHistory } from 'react-router';
import { useDispatch, useSelector } from 'react-redux';
import Form from 'antd/lib/form';
import Input from 'antd/lib/input';
import Button from 'antd/lib/button';
import Space from 'antd/lib/space';
import { Store } from 'antd/lib/form/interface';
import { useForm } from 'antd/lib/form/Form';
import notification from 'antd/lib/notification';

import { createOrganizationAsync } from 'actions/organization-actions';
import validationPatterns from 'utils/validation-patterns';
import { CombinedState } from 'reducers/interfaces';

function CreateOrganizationForm(): JSX.Element {
    const [form] = useForm<Store>();
    const dispatch = useDispatch();
    const history = useHistory();
    const creating = useSelector((state: CombinedState) => state.organizations.creating);
    const MAX_SLUG_LEN = 16;
    const MAX_NAME_LEN = 64;

    const onFinish = (values: Store): void => {
        const {
            phoneNumber, location, email, ...rest
        } = values;

        rest.contact = {
            ...(phoneNumber ? { phoneNumber } : {}),
            ...(email ? { email } : {}),
            ...(location ? { location } : {}),
        };

        dispatch(
            createOrganizationAsync(rest, (createdSlug: string): void => {
                form.resetFields();
                notification.info({ message: `Organization ${createdSlug} has been successfully created` });
            }),
        );
    };

    return (
        <Form
            form={form}
            autoComplete='off'
            onFinish={onFinish}
            className='cvat-create-organization-form'
            layout='vertical'
        >
            <Form.Item
                hasFeedback
                name='slug'
                label='Short name'
                rules={[
                    { required: true, message: 'Short name is a required field' },
                    { max: MAX_SLUG_LEN, message: `Short name must not exceed ${MAX_SLUG_LEN} characters` },
                    { ...validationPatterns.validateOrganizationSlug },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item
                hasFeedback
                name='name'
                label='Full name'
                rules={[{ max: MAX_NAME_LEN, message: `Full name must not exceed ${MAX_NAME_LEN} characters` }]}
            >
                <Input />
            </Form.Item>
            <Form.Item hasFeedback name='description' label='Description'>
                <Input.TextArea rows={3} />
            </Form.Item>
            <Form.Item hasFeedback name='email' label='Email' rules={[{ type: 'email', message: 'The input is not a valid E-mail' }]}>
                <Input autoComplete='email' placeholder='support@organization.com' />
            </Form.Item>
            <Form.Item hasFeedback name='phoneNumber' label='Phone number' rules={[{ ...validationPatterns.validatePhoneNumber }]}>
                <Input autoComplete='phoneNumber' placeholder='+44 5555 555555' />
            </Form.Item>
            <Form.Item hasFeedback name='location' label='Location'>
                <Input autoComplete='location' placeholder='Country, State/Province, Address, Postal code' />
            </Form.Item>
            <Form.Item>
                <Space className='cvat-create-organization-form-buttons-block' align='end'>
                    <Button onClick={() => history.goBack()}>Cancel</Button>
                    <Button loading={creating} disabled={creating} htmlType='submit' type='primary'>
                        Submit
                    </Button>
                </Space>
            </Form.Item>
        </Form>
    );
}

export default React.memo(CreateOrganizationForm);
