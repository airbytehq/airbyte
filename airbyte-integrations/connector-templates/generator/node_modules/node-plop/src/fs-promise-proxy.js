import fs from 'fs';
import mkdirp from 'mkdirp';
import {promisify} from 'util';

const _readFile = promisify(fs.readFile);
const _writeFile = promisify(fs.writeFile);
const _access = promisify(fs.access);

export const makeDir = mkdirp;
export const readdir = promisify(fs.readdir);
export const stat = promisify(fs.stat);
export const chmod = promisify(fs.chmod);
export const readFile = path => _readFile(path, 'utf8');
export const writeFile = (path, data) => _writeFile(path, data, 'utf8');
export const readFileRaw = path => _readFile(path, null);
export const writeFileRaw = (path, data) => _writeFile(path, data, null);
export const fileExists = path => _access(path).then(() => true, () => false);

export const constants = fs.constants;
