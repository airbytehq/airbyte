const path = require('path')

const CopyWebpackPlugin = require('copy-webpack-plugin')
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin')
const { DefinePlugin, HotModuleReplacementPlugin } = require('webpack')
const { merge: webpackMerge } = require('webpack-merge')

const isDevelopment = process.env.NODE_ENV !== 'production'

const options = {
    mode: 'none',
    resolve: {
        alias: {
            'components': path.resolve(__dirname, '../src/app/components'),
        },
        extensions: ['.js', '.jsx', '.ts', '.tsx', '.html'],
        modules: ['node_modules', 'src'],
    },
    resolveLoader: {
        modules: ['node_modules', 'src'],
    },
    entry: {
        main: ['@babel/polyfill', './src/index.tsx'],
    },
    module: {
        rules: [
            {
                test: /\.[jt]sx?$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: require.resolve('babel-loader'),
                        options: {
                            plugins: [
                                isDevelopment &&
                                    require.resolve('react-refresh/babel'),
                            ].filter(Boolean),
                        },
                    },
                ],
            },
        ],
    },
    plugins: [
        new CopyWebpackPlugin({
            patterns: [
                {
                    from: 'public',
                    to: '',
                    globOptions: {
                        ignore: ['.gitkeep', '**/.DS_Store', '**/Thumbs.db'],
                    },
                },
            ],
        }),
        new DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'development'),
            },
        }),
        isDevelopment && new HotModuleReplacementPlugin(),
        isDevelopment && new ReactRefreshWebpackPlugin(),
    ].filter(Boolean),
}

module.exports = isDevelopment
    ? webpackMerge(options, require('./webpack.dev'))
    : webpackMerge(options, require('./webpack.dist'))
