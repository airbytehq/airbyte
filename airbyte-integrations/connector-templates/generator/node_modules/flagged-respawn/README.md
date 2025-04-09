<p align="center">
  <a href="http://gulpjs.com">
    <img height="257" width="114" src="https://raw.githubusercontent.com/gulpjs/artwork/master/gulp-2x.png">
  </a>
</p>

# flagged-respawn

[![NPM version][npm-image]][npm-url] [![Downloads][downloads-image]][npm-url] [![Build Status][ci-image]][ci-url] [![Coveralls Status][coveralls-image]][coveralls-url]

A tool for respawning node binaries when special flags are present.

## What is it?

Say you wrote a command line tool that runs arbitrary javascript (e.g. task runner, test framework, etc). For the sake of discussion, let's pretend it's a testing harness you've named `testify`.

Everything is going splendidly until one day you decide to test some code that relies on a feature behind a v8 flag in node (`--harmony`, for example). Without much thought, you run `testify --harmony spec tests.js`.

It doesn't work. After digging around for a bit, you realize this produces a [`process.argv`](http://nodejs.org/docs/latest/api/process.html#process_process_argv) of:

`['node', '/usr/local/bin/test', '--harmony', 'spec', 'tests.js']`

Crap. The `--harmony` flag is in the wrong place! It should be applied to the **node** command, not our binary. What we actually wanted was this:

`['node', '--harmony', '/usr/local/bin/test', 'spec', 'tests.js']`

Flagged-respawn fixes this problem and handles all the edge cases respawning creates, such as:

- Providing a method to determine if a respawn is needed.
- Piping stderr/stdout from the child into the parent.
- Making the parent process exit with the same code as the child.
- If the child is killed, making the parent exit with the same signal.

To see it in action, clone this repository and run `npm install` / `npm run respawn` / `npm run nospawn`.

## Sample Usage

```js
#!/usr/bin/env node

const flaggedRespawn = require('flagged-respawn');

// get a list of all possible v8 flags for the running version of node
const v8flags = require('v8flags').fetch();

flaggedRespawn(v8flags, process.argv, function (ready, child) {
  if (ready) {
    console.log('Running!');
    // your cli code here
  } else {
    console.log('Special flags found, respawning.');
  }
  if (process.pid !== child.pid) {
    console.log('Respawned to PID:', child.pid);
  }
});
```

## API

### <u>flaggedRespawn(flags, argv, [ forcedFlags, ] callback) : Void</u>

Respawns the script itself when _argv_ has special flag contained in _flags_ and/or _forcedFlags_ is not empty. Because members of _flags_ and _forcedFlags_ are passed to `node` command, each of them needs to be a node flag or a V8 flag.

#### Forbid respawning

If `--no-respawning` flag is given in _argv_, this function does not respawned even if _argv_ contains members of flags or _forcedFlags_ is not empty. (This flag is also used internally to prevent from respawning more than once).

#### Parameter:

| Parameter     |      Type       | Description                                                                              |
| :------------ | :-------------: | :--------------------------------------------------------------------------------------- |
| _flags_       |      Array      | An array of node flags and V8 flags which are available when present in _argv_.          |
| _argv_        |      Array      | Command line arguments to respawn.                                                       |
| _forcedFlags_ | Array or String | An array of node flags or a string of a single flag and V8 flags for respawning forcely. |
| _callback_    |    function     | A called function when not respawning or after respawned.                                |

- **<u><i>callback</i>(ready, proc, argv) : Void</u>**

  _callback_ function is called both when respawned or not, and it can be distinguished by callback's argument: _ready_. (_ready_ indicates whether a process spawned its child process (false) or not (true), but it does not indicate whether a process is a spawned child process or not. _ready_ for a spawned child process is true.)

  _argv_ is an array of command line arguments which is respawned (when _ready_ is false) or is passed current process except flags within _flags_ and `--no-respawning` (when _ready_ is true).

  **Parameter:**

  | Parameter |  Type   | Description                                                          |
  | :-------- | :-----: | :------------------------------------------------------------------- |
  | _ready_   | boolean | True, if not respawning and is ready to execute main function.       |
  | _proc_    | object  | Child process object if respawned, otherwise current process object. |
  | _argv_    |  Array  | An array of command line arguments.                                  |

## License

MIT

<!-- prettier-ignore-start -->
[downloads-image]: https://img.shields.io/npm/dm/flagged-respawn.svg?style=flat-square
[npm-url]: https://www.npmjs.com/package/flagged-respawn
[npm-image]: https://img.shields.io/npm/v/flagged-respawn.svg?style=flat-square

[ci-url]: https://github.com/gulpjs/flagged-respawn/actions?query=workflow:dev
[ci-image]: https://img.shields.io/github/workflow/status/gulpjs/flagged-respawn/dev?style=flat-square

[coveralls-url]: https://coveralls.io/r/gulpjs/flagged-respawn
[coveralls-image]: https://img.shields.io/coveralls/gulpjs/flagged-respawn/master.svg?style=flat-square
<!-- prettier-ignore-end -->
