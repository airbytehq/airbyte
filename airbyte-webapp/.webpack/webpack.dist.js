const path = require('path')
const TerserPlugin = require('terser-webpack-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
    mode: 'production',
    output: {
        path: path.join(process.cwd(), 'dist'),
        chunkFilename: '[id].[chunkhash].chunk.js',
        filename: '[contenthash:24].js',
    },
    plugins: [
        new HtmlWebpackPlugin({
            chunks: ['main'],
            filename: './index.html',
            inject: 'body',
            template: './src/index.html',
            scriptLoading: 'defer',
        }),
    ],
    optimization: {
        minimizer: [
            new TerserPlugin({
                parallel: true,
            }),
        ],
        chunkIds: 'named',
        moduleIds: 'named',
        emitOnErrors: true,

        splitChunks: {
            chunks: 'async',
            minSize: 195000,
            minRemainingSize: 0,
            maxSize: 395000,
            minChunks: 1,
            maxAsyncRequests: 30,
            maxInitialRequests: 30,
            automaticNameDelimiter: '~',
            enforceSizeThreshold: 50000,
            cacheGroups: {
                defaultVendors: {
                    test: /[\\/]node_modules[\\/]/,
                    priority: -10,
                },
                default: {
                    minChunks: 2,
                    priority: -20,
                    reuseExistingChunk: true,
                },
            },
        },
    },
}
