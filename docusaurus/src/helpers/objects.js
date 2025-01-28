const get = require("lodash/get");

/**
 * Generate all possible combinations of a string with options
 *
 * Example:
 * generateCombinations("a_[foo|bar]") // ['a_foo', 'a_bar']
 *
 * @param {string} str - The string to generate the combinations from
 * @returns {string[]} All possible combinations of the string with options
 */
const generateCombinations = (str) => {
  const regex = /\[([^\[\]]+)\]/;
  let match = str.match(regex);

  if (!match) {
    return [str];
  }

  const options = match[1];

  // Check if options are integers
  // If so, return the original string
  // This is to maintain compatibility with arrays
  if (/^\d+$/.test(options)) {
    return [str];
  }

  const splitOptions = options.split("|");
  const prefix = str.substring(0, match.index);
  const suffix = str.substring(match.index + match[0].length);

  let results = [];
  for (let option of splitOptions) {
    const newStr = prefix + option + suffix;
    results = results.concat(newStr);
  }

  return results;
};

/**
 * Merge a path tree into a flat array of paths
 *
 * Example:
 * mergePathTree([['a'], ['b', 'c'], ['d']]) // ['a.b.d', 'a.c.d']
 *
 * @param {string[][]} pathTree - The path tree to merge
 * @returns {string[]} A flat array of paths
 */
const mergePathTree = (pathTree) => {
  return (
    pathTree
      // reduce [[a], [b,c], [d]] to [[a,b,d], [a,c,d]]
      .reduce(
        (a, b) =>
          a
            .map((x) => b.map((y) => x.concat(y)))
            .reduce((a, b) => a.concat(b), []),
        [[]]
      )
      // then flatten to ['a.b.d', 'a.c.d']
      .map((x) => x.join("."))
  );
};

/**
 * Generate all possible paths from a given path
 *
 * Example:
 * generatePaths("a.b_[foo|bar].c") // ['a.b_foo.c', 'a.b_bar.c']
 *
 * @param {string} path - The path to generate the paths from
 * @returns {string[]} All possible paths from the given path
 */
const generatePaths = (path) => {
  const pathChunks = path.split(".");
  const pathTree = pathChunks.map(generateCombinations);
  const paths = mergePathTree(pathTree);
  return paths;
};

/**
 * Get a value from an object using a path OR multiple possible paths
 *
 * Example:
 * const obj = { a: { b_foo: { c: 1 }, b_bar: { c: 2 } } };
 * getFromPaths(obj, "a.b_bar.c", "default"); // 2
 * getFromPaths(obj, "a.b_[foo|bar].c", "default"); // 1
 * getFromPaths(obj, "a.b_[bar|foo].c", "default"); // 2
 * getFromPaths(obj, "a.b_[qux|foo].c", "default"); // 1
 * getFromPaths(obj, "a.b_[baz|qux].c", "default"); // "default"
 *
 * @param {object} obj - The object to get the value from
 * @param {string} path - The path to get the value from
 * @param {any} defaultValue - The value to return if the path does not exist
 * @returns {any} The value from the object at the given path
 */
const getFromPaths = (obj, path, defaultValue = undefined) => {
  // Generate all possible paths from the given path
  const possiblePaths = generatePaths(path);

  // Try to get the value from each possible path
  for (let possiblePath of possiblePaths) {
    const value = get(obj, possiblePath);
    if (value !== undefined && value !== null) {
      return value;
    }
  }

  // Return default value if no value is found
  return defaultValue;
};

/** REMARK UTILS */

const removeUndefined = ([key, value]) => {
  if (value === undefined) return false;
  return [key, value];
};

const kvToAttribute = ([key, value]) => ({
  type: "mdxJsxAttribute",
  name: key,
  value: value,
});

const toAttributes = (props) =>
  Object.entries(props).filter(removeUndefined).map(kvToAttribute);

module.exports = {
  getFromPaths,
  toAttributes,
};
