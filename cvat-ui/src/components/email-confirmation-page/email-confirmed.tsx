// Copyright (C) 2021 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React, { useRef } from 'react';
import { Link } from 'react-router-dom';
import { Col, Row } from 'antd/lib/grid';
import Layout from 'antd/lib/layout';
import Statistic from 'antd/lib/statistic';
import './styles.scss';

const { Content } = Layout;
const { Countdown } = Statistic;

/**
 * Component for displaying email confirmation message and then redirecting to the login page
 */

function EmailConfirmationPage(): JSX.Element {
    const linkRef = useRef();
    const onFinish = () => {
        linkRef.current.click();
    };
    return (
        <Layout>
            <Content>
                <Row justify='center' align='middle' id='email-confirmation-page-container'>
                    <Col>
                        <h1>Your email is confirmed</h1>
                        <Countdown format='ss' title='Redirecting to login page after...' value={Date.now() + 1000 * 6} onFinish={onFinish} />
                        <Link to='/auth/login' ref={linkRef}>Or click this link</Link>
                    </Col>
                </Row>
            </Content>
        </Layout>
    );
}

export default EmailConfirmationPage;
