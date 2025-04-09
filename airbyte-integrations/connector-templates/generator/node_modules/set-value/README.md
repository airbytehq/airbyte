# set-value [![NPM version](https://img.shields.io/npm/v/set-value.svg?style=flat)](https://www.npmjs.com/package/set-value) [![NPM monthly downloads](https://img.shields.io/npm/dm/set-value.svg?style=flat)](https://npmjs.org/package/set-value) [![NPM total downloads](https://img.shields.io/npm/dt/set-value.svg?style=flat)](https://npmjs.org/package/set-value)  [![Tests](https://github.com/jonschlinkert/set-value/actions/workflows/main.yml/badge.svg)](https://github.com/jonschlinkert/set-value/actions/workflows/main.yml)

> Set nested properties on an object using dot notation.

Please consider following this project's author, [Jon Schlinkert](https://github.com/jonschlinkert), and consider starring the project to show your :heart: and support.

## Install

Install with [npm](https://www.npmjs.com/) (requires [Node.js](https://nodejs.org/en/) >=11.0):

```sh
$ npm install --save set-value
```

## Heads up!

[Please update](https://github.com/update/update) to version 3.0.1 or later, a critical bug was fixed in that version.

## Usage

```js
const set = require('set-value');

const obj = {};
set(obj, 'a.b.c', 'd');

console.log(obj);
//=> { a: { b: { c: 'd' } } }
```

### Params

Signature:

```js
set(object, property_path, value[, options]);
```

* `object` **{Object}**: The object to set `value` on
* `path` **{String|Symbol|Array}**: The [path](#object-paths) of the property to set.
* `value` **{any}**: The value to set on `obj[prop]`
* `options` **{Object}**: See all [available options](#options)

### Object paths

You may pass a string, symbol, or array of strings or symbols. By default, when a string is passed this library will split the string on `.` or a [custom separator](#options-separator) It's useful to pass an array

### Escaping

**Escaping with backslashes**

Prevent set-value from splitting on a dot by prefixing it with backslashes:

```js
console.log(set({}, 'a\\.b.c', 'd'));
//=> { 'a.b': { c: 'd' } }

console.log(set({}, 'a\\.b\\.c', 'd'));
//=> { 'a.b.c': 'd' }
```

## Options

### options.preservePaths

Do not split properties that include a `/`. By default, set-value assumes that properties with a `/` are not intended to be split. This option allows you to disable default behavior.

Note that this option cannot be used if `options.separator` is set to `/`.

**Type**: `boolean`

**Default**: `true`

**Example**

```js
console.log(set({}, 'https://github.com', true));
//=> { 'https://github.com': true }

console.log(set({}, 'https://github.com', true, { preservePaths: false }));
//=> { 'https://github': { com: true } }
```

### options.separator

Custom separator to use for splitting object paths.

**Type**: `string`

**Default**: `.`

**Example**

```js
console.log(set(obj, 'auth/userpass/users/bob', '*****', { separator: '/' }));
//=> { auth: { userpass: { users: { bob: '*****' } } } }
```

### options.split

Custom `.split()` function to use.

### options.merge

Allows you to update plain object values, instead of overwriting them.

**Type**: `boolean|function` - A custom `merge` function may be defined if you need to deep merge. Otherwise, when `merge` is `true`, a shallow merge will be performed by `Object.assign()`.

**Default**: `undefined`

**Example**

```js
const obj = { foo: { bar: { baz: 'qux' } } };
set(obj, 'foo.bar.fez', 'zzz', { merge: true });
//=> { foo: { bar: { baz: 'qux', fez: 'zzz' } } }
```

## Benchmarks

Benchmarks were run on a MacBook Pro 2.5 GHz Intel Core i7, 16 GB 1600 MHz DDR3.

```
# deep (194 bytes)
  deep-object x 823,287 ops/sec ±1.00% (90 runs sampled)
  deep-property x 1,787,990 ops/sec ±0.82% (92 runs sampled)
  deephas x 840,700 ops/sec ±0.95% (93 runs sampled)
  dot-prop x 1,249,663 ops/sec ±0.89% (90 runs sampled)
  dot2val x 2,067,212 ops/sec ±1.08% (91 runs sampled)
  es5-dot-prop x 1,668,806 ops/sec ±0.92% (92 runs sampled)
  lodash-set x 1,286,725 ops/sec ±0.82% (90 runs sampled)
  object-path-set x 1,261,242 ops/sec ±1.63% (90 runs sampled)
  object-set x 285,369 ops/sec ±0.91% (90 runs sampled)
  set-value x 2,076,931 ops/sec ±0.86% (93 runs sampled)

  fastest is set-value, dot2val (by 203% avg)

# medium (98 bytes)
  deep-object x 5,811,161 ops/sec ±1.12% (90 runs sampled)
  deep-property x 4,075,885 ops/sec ±0.91% (90 runs sampled)
  deephas x 1,508,136 ops/sec ±0.82% (92 runs sampled)
  dot-prop x 2,809,838 ops/sec ±1.16% (87 runs sampled)
  dot2val x 4,600,890 ops/sec ±0.76% (91 runs sampled)
  es5-dot-prop x 3,263,790 ops/sec ±0.97% (91 runs sampled)
  lodash-set x 3,486,628 ops/sec ±1.20% (90 runs sampled)
  object-path-set x 3,729,018 ops/sec ±0.90% (92 runs sampled)
  object-set x 973,961 ops/sec ±0.80% (92 runs sampled)
  set-value x 6,941,474 ops/sec ±1.24% (90 runs sampled)

  fastest is set-value (by 206% avg)

# shallow (101 bytes)
  deep-object x 9,416,410 ops/sec ±1.19% (89 runs sampled)
  deep-property x 5,108,536 ops/sec ±0.98% (93 runs sampled)
  deephas x 1,706,979 ops/sec ±0.98% (86 runs sampled)
  dot-prop x 4,045,902 ops/sec ±1.10% (92 runs sampled)
  dot2val x 5,862,418 ops/sec ±0.88% (91 runs sampled)
  es5-dot-prop x 4,439,646 ops/sec ±1.18% (90 runs sampled)
  lodash-set x 9,303,292 ops/sec ±1.19% (89 runs sampled)
  object-path-set x 5,657,479 ops/sec ±0.95% (93 runs sampled)
  object-set x 2,020,041 ops/sec ±0.92% (91 runs sampled)
  set-value x 11,272,227 ops/sec ±1.36% (88 runs sampled)

  fastest is set-value (by 213% avg)

```

### Running the benchmarks

Clone this library into a local directory:

```sh
$ git clone https://github.com/jonschlinkert/set-value.git
```

Then install devDependencies and run benchmarks:

```sh
$ npm install && node benchmark
```

## Comparisons to other libs, or _"the list of shame"_

These are just a few of the duplicate libraries on NPM.

* [bury](https://github.com/kalmbach/bury) fails all of the tests. I even wrapped it to have it return the object instead of the value, but with all of that work it still fails the vast majority of tests.
* [deep-get-set](https://github.com/acstll/deep-get-set) fails 22 of 26 unit tests.
* [deep-object](https://github.com/ayushgp/deep-object) fails 25 of 26 unit tests, completely butchered given objects.
* [deep-property](https://github.com/mikattack/node-deep-property) fails 17 of 26 unit tests.
* [deep-set](https://github.com/klaemo/deep-set) fails 13 of 26 unit tests.
* [deephas](https://github.com/sharpred/deepHas) fails 17 of 26 unit tests.
* [dot-prop](https://github.com/sindresorhus/dot-prop) fails 9 of 26 unit tests.
* [dot2val](https://github.com/yangg/dot2val) fails 17 of 26 unit tests.
* [es5-dot-prop](https://github.com/sindresorhus/dot-prop) fails 15 of 26 unit tests.
* [getsetdeep](https://github.com/bevry/getsetdeep) fails all unit tests due to `this` being used improperly in the methods. I was able to patch it by binding the (plain) object to the methods, but it still fails 17 of 26 unit tests.
* [lodash.set](https://lodash.com/) fails 11 of 26 unit tests.
* [object-path-set](https://github.com/skratchdot/object-path-set) fails 12 of 26 unit tests.
* [object-path](https://github.com/mariocasciaro/object-path) fails 16 of 26 unit tests.
* [object-set](https://github.com/gearcase/object-set) fails 13 of 26 unit tests.
* [set-nested-prop](https://github.com/tiaanduplessis/set-nested-prop) fails 24 of 26 unit tests.
* [setvalue](https://github.com/blakeembrey/setvalue) (this library is almost identical to a previous version of this library)
* Many dozens of others

**Others that do the same thing, but use a completely different API**

* [deep-set-in](https://github.com/KulikovskyIgor/deep-set-in)
* [set-deep](https://github.com/radubrehar/set-deep)
* [set-deep-prop](https://github.com/mmckelvy/set-deep-prop)
* [bury](https://github.com/kalmbach/bury)
* Many dozens of others

## History

### v3.0.0

* Added support for a custom `split` function to be passed on the options.
* Removed support for splitting on brackets, since a [custom function](https://github.com/jonschlinkert/split-string) can be passed to do this now.

### v2.0.0

* Adds support for escaping with double or single quotes. See [escaping](#escaping) for examples.
* Will no longer split inside brackets or braces. See [bracket support](#bracket-support) for examples.

If there are any regressions please create a [bug report](../../issues/new). Thanks!

## About

<details>
<summary><strong>Contributing</strong></summary>

Pull requests and stars are always welcome. For bugs and feature requests, [please create an issue](../../issues/new).

</details>

<details>
<summary><strong>Running Tests</strong></summary>

Running and reviewing unit tests is a great way to get familiarized with a library and its API. You can install dependencies and run tests with the following command:

```sh
$ npm install && npm test
```

</details>

<details>
<summary><strong>Building docs</strong></summary>

_(This project's readme.md is generated by [verb](https://github.com/verbose/verb-generate-readme), please don't edit the readme directly. Any changes to the readme must be made in the [.verb.md](.verb.md) readme template.)_

To generate the readme, run the following command:

```sh
$ npm install -g verbose/verb#dev verb-generate-readme && verb
```

</details>

### Related projects

You might also be interested in these projects:

* [assign-value](https://www.npmjs.com/package/assign-value): Assign a value or extend a deeply nested property of an object using object path… [more](https://github.com/jonschlinkert/assign-value) | [homepage](https://github.com/jonschlinkert/assign-value "Assign a value or extend a deeply nested property of an object using object path notation.")
* [get-value](https://www.npmjs.com/package/get-value): Use property paths like 'a.b.c' to get a nested value from an object. Even works… [more](https://github.com/jonschlinkert/get-value) | [homepage](https://github.com/jonschlinkert/get-value "Use property paths like 'a.b.c' to get a nested value from an object. Even works when keys have dots in them (no other dot-prop library can do this!).")
* [has-value](https://www.npmjs.com/package/has-value): Returns true if a value exists, false if empty. Works with deeply nested values using… [more](https://github.com/jonschlinkert/has-value) | [homepage](https://github.com/jonschlinkert/has-value "Returns true if a value exists, false if empty. Works with deeply nested values using object paths.")
* [merge-value](https://www.npmjs.com/package/merge-value): Similar to assign-value but deeply merges object values or nested values using object path/dot notation. | [homepage](https://github.com/jonschlinkert/merge-value "Similar to assign-value but deeply merges object values or nested values using object path/dot notation.")
* [omit-value](https://www.npmjs.com/package/omit-value): Omit properties from an object or deeply nested property of an object using object path… [more](https://github.com/jonschlinkert/omit-value) | [homepage](https://github.com/jonschlinkert/omit-value "Omit properties from an object or deeply nested property of an object using object path notation.")
* [set-value](https://www.npmjs.com/package/set-value): Set nested properties on an object using dot notation. | [homepage](https://github.com/jonschlinkert/set-value "Set nested properties on an object using dot notation.")
* [union-value](https://www.npmjs.com/package/union-value): Set an array of unique values as the property of an object. Supports setting deeply… [more](https://github.com/jonschlinkert/union-value) | [homepage](https://github.com/jonschlinkert/union-value "Set an array of unique values as the property of an object. Supports setting deeply nested properties using using object-paths/dot notation.")
* [unset-value](https://www.npmjs.com/package/unset-value): Delete nested properties from an object using dot notation. | [homepage](https://github.com/jonschlinkert/unset-value "Delete nested properties from an object using dot notation.")

### Contributors

| **Commits** | **Contributor** |  
| --- | --- |  
| 87 | [jonschlinkert](https://github.com/jonschlinkert) |  
| 4  | [doowb](https://github.com/doowb) |  
| 2  | [mbelsky](https://github.com/mbelsky) |  
| 1  | [dkebler](https://github.com/dkebler) |  
| 1  | [GlennKintscher](https://github.com/GlennKintscher) |  
| 1  | [petermorlion](https://github.com/petermorlion) |  
| 1  | [abetomo](https://github.com/abetomo) |  
| 1  | [zeidoo](https://github.com/zeidoo) |  
| 1  | [ready-research](https://github.com/ready-research) |  
| 1  | [wtgtybhertgeghgtwtg](https://github.com/wtgtybhertgeghgtwtg) |  

### Author

**Jon Schlinkert**

* [GitHub Profile](https://github.com/jonschlinkert)
* [Twitter Profile](https://twitter.com/jonschlinkert)
* [LinkedIn Profile](https://linkedin.com/in/jonschlinkert)

### License

Copyright © 2021, [Jon Schlinkert](https://github.com/jonschlinkert).
Released under the [MIT License](LICENSE).

***

_This file was generated by [verb-generate-readme](https://github.com/verbose/verb-generate-readme), v0.8.0, on September 12, 2021._