const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const webpack = require('webpack')

module.exports = {
    target: 'web',
    mode: 'development',
    output: {
        chunkFilename: '[id].chunk.js',
        filename: '[name].bundle.js',
        path: path.join(__dirname, 'build'),
        publicPath: '/',
    },
    devServer: {
        allowedHosts: ['*'],
        historyApiFallback: true,
        hot: true,
        host: '0.0.0.0',
        port: 3000,
    },
    stats: {
        children: true,
        errorDetails: true,
    },
    plugins: [
        new webpack.SourceMapDevToolPlugin({}),
        new HtmlWebpackPlugin({
            filename: './index.html',
            template: './src/index.html',
            inject: 'body',
        }),
    ],
}
