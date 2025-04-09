Node-Plop
======

[![npm](https://img.shields.io/npm/v/node-plop.svg)](https://www.npmjs.com/package/node-plop)
[![GitHub actions](https://img.shields.io/github/workflow/status/plopjs/node-plop/test)](https://github.com/plopjs/node-plop/actions/workflows/test.yml)

This is an early publication of the plop core logic being removed from the CLI tool. Main purpose for this is to make it easier for others to automate code generation through processes and tools OTHER than the command line. This also makes it easier to test the code functionality of PLOP without needing to test via the CLI interface.

This is the backend code that drives the plop CLI tool using node-plop.

``` javascript
import nodePlop from 'node-plop';
// load an instance of plop from a plopfile
const plop = await nodePlop(`./path/to/plopfile.js`);
// get a generator by name
const basicAdd = plop.getGenerator('basic-add');

// run all the generator actions using the data specified
basicAdd.runActions({name: 'this is a test'}).then(function (results) {
  // do something after the actions have run
});
```
