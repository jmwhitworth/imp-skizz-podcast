// Load all CSS files in the src directory
import.meta.glob('../css/vendor/*.css', {
    eager: true,
})
import.meta.glob('../css/*.css', {
    eager: true,
})

// Load all JavaScript files in the current directory
import.meta.glob('./vendor/*.js', {
    eager: true,
})
import.meta.glob('./*.js', {
    eager: true,
})

import 'htmx.org'

import { library, dom } from '@fortawesome/fontawesome-svg-core'
import {
    faPatreon,
    faYoutube,
    faSpotify,
    faApple,
} from '@fortawesome/free-brands-svg-icons'
import { faArrowUpRightFromSquare } from '@fortawesome/free-solid-svg-icons'
library.add(faPatreon, faYoutube, faSpotify, faApple, faArrowUpRightFromSquare)
dom.watch()
