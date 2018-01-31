const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');
const webpack = require('webpack');

const extractPlugin = new ExtractTextPlugin({
  filename: '[name].[hash].css'
});

const assetRoot = path.resolve('frontend');

module.exports = {

  context: assetRoot,

  entry: './js/index.js',

  output: {
    filename: '[name].[hash].js',
    path: path.resolve('build', 'public'),
    publicPath: 'http://localhost:3000/',
  },

  module: {
    rules: [

      // babel-loader
      {
        test: /\.js$/,
        include: [path.resolve('frontend', 'js')],
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      },

      // sass-loader
      {
        test: /\.scss$/,
        include: [path.resolve('frontend', 'scss')],
        use: extractPlugin.extract({
          use: [
            {
              loader: 'css-loader',
              options: {
                sourceMap: true
              }
            },
            {
              loader: 'sass-loader',
              options: {
                sourceMap: true
              }
            }
          ],
          fallback: 'style-loader'
        })
      },
    ]
  },

  plugins: [
    new CleanWebpackPlugin(['build/public']),
    extractPlugin,
    new ManifestRevisionPlugin(path.join('build', 'manifest.json'), {
      rootAssetPath: assetRoot,
      ignorePaths: ['/scss', '/js']
    })
  ]
}
