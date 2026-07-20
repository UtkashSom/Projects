const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Your Flask backend URL
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/api': '' // Remove /api when forwarding to Flask
        }
      }
    }
  }
})
