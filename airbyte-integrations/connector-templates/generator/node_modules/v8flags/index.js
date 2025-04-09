// this entire module is depressing. i should have spent my time learning
// how to patch v8 so that these options would just be available on the
// process object.

var os = require('os');
var fs = require('fs');
var path = require('path');
var crypto = require('crypto');
var execFile = require('child_process').execFile;
var configPath = require('./config-path.js')(process.platform);
var env = process.env;
var user = env.LOGNAME || env.USER || env.LNAME || env.USERNAME || '';
var exclusions = ['--help', '--completion-bash'];

// This number must be incremented whenever the generated cache file changes.
var CACHE_VERSION = 3;

var configfile =
  '.v8flags-' +
  CACHE_VERSION +
  '-' +
  process.versions.v8 +
  '.' +
  crypto.createHash('sha256').update(user).digest('hex') +
  '.json';

var failureMessage = [
  'Unable to cache a config file for v8flags to your home directory',
  'or a temporary folder. To fix this problem, please correct your',
  'environment by setting HOME=/path/to/home or TEMP=/path/to/temp.',
  'NOTE: the user running this must be able to access provided path.',
  'If all else fails, please open an issue here:',
  'http://github.com/tkellen/js-v8flags',
].join('\n');

function fail(err) {
  err.message += '\n\n' + failureMessage;
  return err;
}

function openConfig(cb) {
  fs.mkdir(configPath, function () {
    tryOpenConfig(path.join(configPath, configfile), function (err, fd) {
      if (err) {
        return tryOpenConfig(path.join(os.tmpdir(), configfile), cb);
      }
      return cb(null, fd);
    });
  });
}

function tryOpenConfig(configpath, cb) {
  try {
    // if the config file is valid, it should be json and therefore
    // node should be able to require it directly. if this doesn't
    // throw, we're done!
    var content = require(configpath);
    process.nextTick(function () {
      cb(null, content);
    });
  } catch (e) {
    // if requiring the config file failed, maybe it doesn't exist, or
    // perhaps it has become corrupted. instead of calling back with the
    // content of the file, call back with a file descriptor that we can
    // write the cached data to
    fs.open(configpath, 'w+', function (err, fd) {
      if (err) {
        return cb(err);
      }
      return cb(null, fd);
    });
  }
}

function normalizeFlagName(flag) {
  return flag.trim();
}

// i can't wait for the day this whole module is obsolete because these
// options are available on the process object. this executes node with
// `--v8-options` and parses the result, returning an array of command
// line flags.
function getFlags(cb) {
  var flags = Array.from(process.allowedNodeEnvironmentFlags);

  execFile(process.execPath, ['--v8-options'], function (execErr, result) {
    if (execErr) {
      cb(execErr);
      return;
    }

    var index = result.indexOf('\nOptions:');
    if (index >= 0) {
      var regexp = /^\s\s--[\w-]+/gm;
      regexp.lastIndex = index;
      var matchedFlags = result.match(regexp);
      if (matchedFlags) {
        flags = flags.concat(
          matchedFlags.map(normalizeFlagName).filter(function (name) {
            return exclusions.indexOf(name) === -1;
          })
        );
      }
    }

    cb(null, flags);
  });
}

// write some json to a file descriptor. if this fails, call back
// with both the error and the data that was meant to be written.
function writeConfig(fd, flags, cb) {
  var json = JSON.stringify(flags);
  var buf = Buffer.from(json);
  return fs.write(fd, buf, 0, buf.length, 0, function (writeErr) {
    fs.close(fd, function (closeErr) {
      var err = writeErr || closeErr;
      if (err) {
        return cb(fail(err), flags);
      }
      return cb(null, flags);
    });
  });
}

module.exports = function (cb) {
  // bail early if this is not node
  var isElectron = process.versions && process.versions.electron;
  if (isElectron) {
    return process.nextTick(function () {
      cb(null, []);
    });
  }

  // attempt to open/read cache file
  openConfig(function (openErr, result) {
    if (!openErr && typeof result !== 'number') {
      return cb(null, result);
    }
    // if the result is not an array, we need to go fetch
    // the flags by invoking node with `--v8-options`
    getFlags(function (flagsErr, flags) {
      // if there was an error fetching the flags, bail immediately
      if (flagsErr) {
        return cb(flagsErr);
      }
      // if there was a problem opening the config file for writing
      // throw an error but include the flags anyway so that users
      // can continue to execute (at the expense of having to fetch
      // flags on every run until they fix the underyling problem).
      if (openErr) {
        return cb(fail(openErr), flags);
      }
      // write the config file to disk so subsequent runs can read
      // flags out of a cache file.
      return writeConfig(result, flags, cb);
    });
  });
};

module.exports.configfile = configfile;
module.exports.configPath = configPath;
