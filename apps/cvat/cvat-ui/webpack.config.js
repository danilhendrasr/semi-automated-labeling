// Copyright (C) 2020-2021 Intel Corporation
//
// SPDX-License-Identifier: MIT

/* global
    __dirname:true
*/

const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');
const Dotenv = require('dotenv-webpack');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = (env) => ({
    target: 'web',
    mode: 'production',
    devtool: 'source-map',
    entry: {
        'cvat-ui': './src/index.tsx',
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'assets/[name].[contenthash].min.js',
        publicPath: '/',
    },
    devServer: {
        contentBase: path.join(__dirname, 'dist'),
        compress: false,
        inline: true,
        host: process.env.CVAT_UI_HOST || 'localhost',
        port: 3000,
        historyApiFallback: true,
        proxy: [
            {
                context: (param) =>
                    param.match(
                        /\/api\/.*|git\/.*|opencv\/.*|analytics\/.*|static\/.*|admin(?:\/(.*))?.*|documentation\/.*|django-rq(?:\/(.*))?/gm,
                    ),
                target: env && env.API_URL,
                secure: false,
                changeOrigin: true,
            },
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.jsx', '.js', '.json'],
        plugins: [new TsconfigPathsPlugin({ configFile: './tsconfig.json' })],
    },
    module: {
        rules: [
            {
                test: /\.(ts|tsx)$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        plugins: [
                            '@babel/plugin-proposal-class-properties',
                            '@babel/plugin-proposal-optional-chaining',
                            [
                                'import',
                                {
                                    libraryName: 'antd',
                                },
                            ],
                        ],
                        presets: ['@babel/preset-env', '@babel/preset-react', '@babel/typescript'],
                        sourceType: 'unambiguous',
                    },
                },
            },
            {
                test: /\.(css|scss)$/,
                use: [
                    'style-loader',
                    {
                        loader: 'css-loader',
                        options: {
                            importLoaders: 2,
                        },
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            plugins: [require('postcss-preset-env')],
                        },
                    },
                    'sass-loader',
                ],
            },
            {
                test: /\.svg$/,
                exclude: /node_modules/,
                use: [
                    'babel-loader',
                    {
                        loader: 'react-svg-loader',
                        query: {
                            svgo: {
                                plugins: [{ pretty: true }, { cleanupIDs: false }],
                            },
                        },
                    },
                ],
            },
            {
                test: /3rdparty\/.*\.worker\.js$/,
                use: {
                    loader: 'worker-loader',
                    options: {
                        publicPath: '/',
                        name: 'assets/3rdparty/[name].[contenthash].js',
                    },
                },
            },
            {
                test: /\.worker\.js$/,
                exclude: /3rdparty/,
                use: {
                    loader: 'worker-loader',
                    options: {
                        publicPath: '/',
                        name: 'assets/[name].[contenthash].js',
                    },
                },
            },
        ],
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './src/index.html',
            inject: 'body',
        }),
        new Dotenv({
            systemvars: true,
        }),
        new CopyPlugin([
            {
                from: '../cvat-data/src/js/3rdparty/avc.wasm',
                to: 'assets/3rdparty/',
            },
        ]),
    ],
    node: { fs: 'empty' },
});
