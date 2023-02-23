// A mock that will return the name of the property called on it.
// Useful for mocking out (S)CSS modules.

module.exports = new Proxy(
  {},
  {
    get: (target, key) => {
      if (key === "__esModule") {
        return false;
      }
      return key;
    },
  }
);
