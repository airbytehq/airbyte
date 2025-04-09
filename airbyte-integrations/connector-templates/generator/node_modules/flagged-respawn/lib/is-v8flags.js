function isV8flags(flag, v8flags) {
  return v8flags.indexOf(flag) >= 0;
}

module.exports = isV8flags;
