const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  context: __dirname,
  entry: {
    // Add your app entry points here
    // Format: AppName: './project/gameengine/app_name/webpack/app_name_root.js'
    // Example:
    // GameApp: './project/gameengine/game/webpack/game_root.js',
    gameengine: './project/gameengine/gameengine/webpack/gameengine_root.js',
  },
  output: {
    path: path.resolve('./project/gameengine/static/webpack_bundles/'),
    filename: 'web_pack_bundle_[name]-[hash].js',
    publicPath: '/static/webpack_bundles/'
  },
  plugins: [
    new BundleTracker({
      path: path.resolve('./'),
      filename: 'webpack-stats.json'
    }),
    new MiniCssExtractPlugin({
      filename: '[name]-[hash].css',
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      }
    ]
  },
  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.jsx']
  }
};
