// Attach Django's CSRF token as a header on every htmx request.
// Required for DELETE/PUT/PATCH: Django's CsrfViewMiddleware only reads
// the csrfmiddlewaretoken body field for POST, and falls back to the
// X-CSRFToken header for every other unsafe method.
function getCookie(name) {
    const match = document.cookie.match(
        new RegExp('(^|;\\s*)' + name + '=([^;]*)')
    )
    return match ? decodeURIComponent(match[2]) : null
}

document.body.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-CSRFToken'] = getCookie('csrftoken')
})