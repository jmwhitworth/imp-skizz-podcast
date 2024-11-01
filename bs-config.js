module.exports = {
    proxy: "127.0.0.1:8000", // Your Django development server address
    files: [
        "static/css/output.css",
        "static/js/*.js",
        "podcasts/templates/**/*.html"
    ],
    open: false,
    notify: false
};