import fs from 'fs';
import path from 'path';
import inquirer from 'inquirer';
import handlebars from 'handlebars';
import _get from 'lodash.get';
import resolve from 'resolve';

import bakedInHelpers from './baked-in-helpers.js';
import generatorRunner from './generator-runner.js';

import { createRequire } from 'node:module';
import {pathToFileURL} from 'url';
const require = createRequire(import.meta.url);

async function nodePlop(plopfilePath = '', plopCfg = {}) {

	let pkgJson = {};
	let defaultInclude = {generators: true};

	let welcomeMessage;
	const {destBasePath, force} = plopCfg;
	const generators = {};
	const partials = {};
	const actionTypes = {};
	const helpers = Object.assign({
		pkg: (propertyPath) => _get(pkgJson, propertyPath, '')
	}, bakedInHelpers);
	const baseHelpers = Object.keys(helpers);

	const setPrompt = inquirer.registerPrompt;
	const setWelcomeMessage = (message) => { welcomeMessage = message; };
	const setHelper = (name, fn) => { helpers[name] = fn; };
	const setPartial = (name, str) => { partials[name] = str; };
	const setActionType = (name, fn) => { actionTypes[name] = fn; };

	function renderString(template, data) {
		Object.keys(helpers).forEach(h => handlebars.registerHelper(h, helpers[h]));
		Object.keys(partials).forEach(p => handlebars.registerPartial(p, partials[p]));
		return handlebars.compile(template)(data);
	}

	const getWelcomeMessage = () => welcomeMessage;
	const getHelper = name => helpers[name];
	const getPartial = name => partials[name];
	const getActionType = name => actionTypes[name];
	const getGenerator = name => generators[name];
	function setGenerator(name = '', config = {}) {
		// if no name is provided, use a default
		name = name || `generator-${Object.keys(generators).length + 1}`;

		// add the generator to this context
		generators[name] = Object.assign(config, {
			name: name,
			basePath: plopfilePath
		});

		return generators[name];
	}

	const getHelperList = () => Object.keys(helpers).filter(h => !baseHelpers.includes(h));
	const getPartialList = () => Object.keys(partials);
	const getActionTypeList = () => Object.keys(actionTypes);
	function getGeneratorList() {
		return Object.keys(generators).map(function (name) {
			const {description} = generators[name];
			return {name, description};
		});
	}

	const setDefaultInclude = inc => defaultInclude = inc;
	const getDefaultInclude = () => defaultInclude;
	const getDestBasePath = () => destBasePath || plopfilePath;
	const getPlopfilePath = () => plopfilePath;
	const setPlopfilePath = filePath => {
		const pathStats = fs.statSync(filePath);
		if (pathStats.isFile()) {
			plopfilePath = path.dirname(filePath);
		} else {
			plopfilePath = filePath;
		}
	};

	async function load(targets, loadCfg = {}, includeOverride) {
		if (typeof targets === 'string') { targets = [targets]; }
		const config = Object.assign({
			destBasePath: getDestBasePath()
		}, loadCfg);

		await Promise.all(targets.map(async function (target) {
			const targetPath = resolve.sync(target, {basedir: getPlopfilePath()});
			const proxy = await nodePlop(targetPath, config);
			const proxyDefaultInclude = proxy.getDefaultInclude() || {};
			const includeCfg = includeOverride || proxyDefaultInclude;
			const include = Object.assign({
				generators: false,
				helpers: false,
				partials: false,
				actionTypes: false
			}, includeCfg);

			const genNameList = proxy.getGeneratorList().map(g => g.name);
			loadAsset(genNameList, include.generators, setGenerator, proxyName => ({proxyName, proxy}));
			loadAsset(proxy.getPartialList(), include.partials, setPartial, proxy.getPartial);
			loadAsset(proxy.getHelperList(), include.helpers, setHelper, proxy.getHelper);
			loadAsset(proxy.getActionTypeList(), include.actionTypes, setActionType, proxy.getActionType);
		}));
	}

	function loadAsset(nameList, include, addFunc, getFunc) {
		var incArr;
		if (include === true) { incArr = nameList; }
		if (include instanceof Array) {
			incArr = include.filter(n => typeof n === 'string');
		}
		if (incArr != null) {
			include = incArr.reduce(function (inc, name) {
				inc[name] = name;
				return inc;
			}, {});
		}

		if (include instanceof Object) {
			Object.keys(include).forEach(i => addFunc(include[i], getFunc(i)));
		}
	}

	function loadPackageJson() {
		// look for a package.json file to use for the "pkg" helper
		try { pkgJson = require(path.join(getDestBasePath(), 'package.json')); }
		catch(error) { pkgJson = {}; }
	}

	/////////
	// the API that is exposed to the plopfile when it is executed
	// it differs from the nodePlopApi in that it does not include the
	// generator runner methods
	//
	const plopfileApi = {
		// main methods for setting and getting plop context things
		setPrompt,
		setWelcomeMessage, getWelcomeMessage,
		setGenerator, getGenerator, getGeneratorList,
		setPartial, getPartial, getPartialList,
		setHelper, getHelper, getHelperList,
		setActionType, getActionType, getActionTypeList,

		// path context methods
		setPlopfilePath, getPlopfilePath,
		getDestBasePath,

		// plop.load functionality
		load, setDefaultInclude, getDefaultInclude,

		// render a handlebars template
		renderString,

		// passthrough properties
		inquirer, handlebars,

		// passthroughs for backward compatibility
		addPrompt: setPrompt,
		addPartial: setPartial,
		addHelper: setHelper
	};

	// the runner for this instance of the nodePlop api
	const runner = generatorRunner(plopfileApi, {force});
	const nodePlopApi = Object.assign({}, plopfileApi, {
		getGenerator(name) {
			var generator = plopfileApi.getGenerator(name);

			if (generator == null) { throw Error(`Generator "${name}" does not exist.`); }

			// if this generator was loaded from an external plopfile, proxy the
			// generator request through to the external plop instance
			if (generator.proxy) {
				return generator.proxy.getGenerator(generator.proxyName);
			}

			return Object.assign({}, generator, {
				runActions: (data, hooks) => runner.runGeneratorActions(generator, data, hooks),
				runPrompts: (bypassArr = []) => runner.runGeneratorPrompts(generator, bypassArr)
			});
		},
		setGenerator(name, config) {
			const g = plopfileApi.setGenerator(name, config);
			return this.getGenerator(g.name);
		}
	});

	if (plopfilePath) {
		plopfilePath = path.resolve(plopfilePath);
		const plopFileName = path.basename(plopfilePath);
		setPlopfilePath(plopfilePath);
		loadPackageJson();

		const joinedPath = path.join(plopfilePath, plopFileName);
		const plopFileExport = await import(pathToFileURL(joinedPath).href);
		const plop = typeof plopFileExport === 'function' ? plopFileExport : plopFileExport.default;

		await plop(plopfileApi, plopCfg);
	} else {
		setPlopfilePath(process.cwd());
		loadPackageJson();
	}

	return nodePlopApi;
}

export default nodePlop;
