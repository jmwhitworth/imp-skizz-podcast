
# Installation

## Python

To install, use `pipenv`:
```bash
pipenv install
```

To then run the project locally:
```bash
# To use the installed Python environment
pipenv shell

python manage.js runserver
```

## Node

To install, use NPM:
```bash
npm install
```

> Node version `21` required.

To watch for changes:
```bash
npm run start
```

To build for production:
```bash
npm run build
```

## Others

To fix template indentation:
```bash
djhtml ./podcasts/templates/podcasts/**/*.html
```
