const path = require('path')

const CopyWebpackPlugin = require('copy-webpack-plugin')
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin')
const { HotModuleReplacementPlugin } = require('webpack')
const { merge: webpackMerge } = require('webpack-merge')
const Dotenv = require('dotenv-webpack')

const isDevelopment = process.env.NODE_ENV !== 'production'

const options = {
    mode: 'none',
    resolve: {
        alias: {
            // TODO: replace all aliases with `@app/` (+tsconfig.json)
            '@app': path.resolve(__dirname, '../src'),
            hooks: path.resolve(__dirname, '../src/hooks'),
            locales: path.resolve(__dirname, '../src/locales'),
            packages: path.resolve(__dirname, '../src/packages'),
            pages: path.resolve(__dirname, '../src/pages'),
            types: path.resolve(__dirname, '../src/types'),
            utils: path.resolve(__dirname, '../src/utils'),
            views: path.resolve(__dirname, '../src/views'),
        },
        extensions: ['.js', '.jsx', '.ts', '.tsx', '.html'],
        modules: ['node_modules', 'src'],
    },
    resolveLoader: {
        modules: ['node_modules', 'src'],
    },
    entry: {
        main: ['@babel/polyfill', './src/main.ts'],
    },
    module: {
        rules: [
            {
                test: /\.[jt]sx?$/,
                resolve: {
                    fullySpecified: false,
                },
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
        new Dotenv({
            path:
                process.env.NODE_ENV === 'production'
                    ? './.env.prod'
                    : './.env.dev',
        }),
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
        isDevelopment && new HotModuleReplacementPlugin(),
        isDevelopment && new ReactRefreshWebpackPlugin(),
    ].filter(Boolean),
}

module.exports = isDevelopment
    ? webpackMerge(options, require('./webpack.dev'))
    : webpackMerge(options, require('./webpack.dist'))
