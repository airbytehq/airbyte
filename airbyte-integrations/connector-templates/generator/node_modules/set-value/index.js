/*!
 * set-value <https://github.com/jonschlinkert/set-value>
 *
 * Copyright (c) Jon Schlinkert (https://github.com/jonschlinkert).
 * Released under the MIT License.
 */

'use strict';

const { deleteProperty } = Reflect;
const isPrimitive = require('is-primitive');
const isPlainObject = require('is-plain-object');

const isObject = value => {
  return (typeof value === 'object' && value !== null) || typeof value === 'function';
};

const isUnsafeKey = key => {
  return key === '__proto__' || key === 'constructor' || key === 'prototype';
};

const validateKey = key => {
  if (!isPrimitive(key)) {
    throw new TypeError('Object keys must be strings or symbols');
  }

  if (isUnsafeKey(key)) {
    throw new Error(`Cannot set unsafe key: "${key}"`);
  }
};

const toStringKey = input => {
  return Array.isArray(input) ? input.flat().map(String).join(',') : input;
};

const createMemoKey = (input, options) => {
  if (typeof input !== 'string' || !options) return input;
  let key = input + ';';
  if (options.arrays !== undefined) key += `arrays=${options.arrays};`;
  if (options.separator !== undefined) key += `separator=${options.separator};`;
  if (options.split !== undefined) key += `split=${options.split};`;
  if (options.merge !== undefined) key += `merge=${options.merge};`;
  if (options.preservePaths !== undefined) key += `preservePaths=${options.preservePaths};`;
  return key;
};

const memoize = (input, options, fn) => {
  const key = toStringKey(options ? createMemoKey(input, options) : input);
  validateKey(key);

  const value = setValue.cache.get(key) || fn();
  setValue.cache.set(key, value);
  return value;
};

const splitString = (input, options = {}) => {
  const sep = options.separator || '.';
  const preserve = sep === '/' ? false : options.preservePaths;

  if (typeof input === 'string' && preserve !== false && /\//.test(input)) {
    return [input];
  }

  const parts = [];
  let part = '';

  const push = part => {
    let number;
    if (part.trim() !== '' && Number.isInteger((number = Number(part)))) {
      parts.push(number);
    } else {
      parts.push(part);
    }
  };

  for (let i = 0; i < input.length; i++) {
    const value = input[i];

    if (value === '\\') {
      part += input[++i];
      continue;
    }

    if (value === sep) {
      push(part);
      part = '';
      continue;
    }

    part += value;
  }

  if (part) {
    push(part);
  }

  return parts;
};

const split = (input, options) => {
  if (options && typeof options.split === 'function') return options.split(input);
  if (typeof input === 'symbol') return [input];
  if (Array.isArray(input)) return input;
  return memoize(input, options, () => splitString(input, options));
};

const assignProp = (obj, prop, value, options) => {
  validateKey(prop);

  // Delete property when "value" is undefined
  if (value === undefined) {
    deleteProperty(obj, prop);

  } else if (options && options.merge) {
    const merge = options.merge === 'function' ? options.merge : Object.assign;

    // Only merge plain objects
    if (merge && isPlainObject(obj[prop]) && isPlainObject(value)) {
      obj[prop] = merge(obj[prop], value);
    } else {
      obj[prop] = value;
    }

  } else {
    obj[prop] = value;
  }

  return obj;
};

const setValue = (target, path, value, options) => {
  if (!path || !isObject(target)) return target;

  const keys = split(path, options);
  let obj = target;

  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    const next = keys[i + 1];

    validateKey(key);

    if (next === undefined) {
      assignProp(obj, key, value, options);
      break;
    }

    if (typeof next === 'number' && !Array.isArray(obj[key])) {
      obj = obj[key] = [];
      continue;
    }

    if (!isObject(obj[key])) {
      obj[key] = {};
    }

    obj = obj[key];
  }

  return target;
};

setValue.split = split;
setValue.cache = new Map();
setValue.clear = () => {
  setValue.cache = new Map();
};

module.exports = setValue;
