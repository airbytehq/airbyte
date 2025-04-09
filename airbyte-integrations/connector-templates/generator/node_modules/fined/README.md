<p align="center">
  <a href="http://gulpjs.com">
    <img height="257" width="114" src="https://raw.githubusercontent.com/gulpjs/artwork/master/gulp-2x.png">
  </a>
</p>

# fined

[![NPM version][npm-image]][npm-url] [![Downloads][downloads-image]][npm-url] [![Build Status][ci-image]][ci-url] [![Coveralls Status][coveralls-image]][coveralls-url]

Find a file given a declaration of locations.

## Usage

```js
var fined = require('fined');

fined({ path: 'path/to/file', extensions: ['.js', '.json'] });
// => { path: '/absolute/path/to/file.js', extension: '.js' }  (if file exists)
// => null  (if file does not exist)

var opts = {
  name: '.app',
  cwd: '.',
  extensions: {
    rc: 'default-rc-loader',
    '.yml': 'default-yml-loader',
  },
};

fined({ path: '.' }, opts);
// => { path: '/absolute/of/cwd/.app.yml', extension: { '.yml': 'default-yml-loader' } }

fined({ path: '~', extensions: { rc: 'some-special-rc-loader' } }, opts);
// => { path: '/User/home/.apprc', extension: { 'rc': 'some-special-rc-loader' } }
```

## API

### fined(pathObj, opts) => object | null

#### Arguments:

- **pathObj** [string | object] : a path setting for finding a file.
- **opts** [object] : a plain object supplements `pathObj`.

  `pathObj` and `opts` can have same properties:

  - **path** [string] : a path string.
  - **name** [string] : a basename.
  - **extensions**: [string | array | object] : extensions.
  - **cwd**: a base directory of `path` and for finding up.
  - **findUp**: [boolean] : a flag to find up.

#### Return:

This function returns a plain object which consists of following properties if a file exists otherwise null.

- **path** : an absolute path
- **extension** : a string or a plain object of extension.

## License

MIT

<!-- prettier-ignore-start -->
[downloads-image]: https://img.shields.io/npm/dm/fined.svg?style=flat-square
[npm-url]: https://www.npmjs.com/package/fined
[npm-image]: https://img.shields.io/npm/v/fined.svg?style=flat-square

[ci-url]: https://github.com/gulpjs/fined/actions?query=workflow:dev
[ci-image]: https://img.shields.io/github/workflow/status/gulpjs/fined/dev?style=flat-square

[coveralls-url]: https://coveralls.io/r/gulpjs/fined
[coveralls-image]: https://img.shields.io/coveralls/gulpjs/fined/master.svg
<!-- prettier-ignore-end -->
