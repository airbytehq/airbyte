/* eslint-disable @typescript-eslint/no-unused-vars */
import nodePlop, {
	NodePlopAPI,
	AddManyActionConfig,
	AddActionConfig,
	CustomActionConfig,
	Actions,
	ModifyActionConfig, AppendActionConfig
} from './index';
import inquirer from "inquirer";
import prompt from 'inquirer-autocomplete-prompt';

const plop = await nodePlop('./file', {
	destBasePath: './',
	force: false,
});

const generators = plop.getGeneratorList();

const names = generators.map((v) => v.name);

const generator = plop.getGenerator(names[0]);

plop.getWelcomeMessage();

// @ts-expect-error "Undefined method on plop"
plop.test();

generator.runPrompts(['test']).then((answers) => {
	const onComment = (): void => {
		console.log('Start');
	};
	const onSuccess = (): void => {
		console.log('This worked!');
	};
	const onFailure = (): void => {
		console.log('Failed');
	};
	return generator.runActions(answers, { onSuccess, onFailure, onComment }).then(() => {
		console.log('Done');
	});
});

plop.setGenerator('test', {
	description: 'test generator',
	prompts: [{
		type: 'input',
		name: 'name',
		message(): string {
			return 'test name';
		},
		validate(value): true | string {
			if ((/.+/).test(value)) { return true; }
			return 'test name is required';
		}
	}],
	actions: [{
		type: 'add',
		path: 'tests/{{dashCase name}}.ava.js',
		templateFile: 'plop-templates/ava-test.js'
	}]
});

plop.setGenerator('test-dynamic-prompts-only', {
	description: 'test dynamic prompts only',
	prompts: async (inquirer) => ({
		name: 'something-dynamic'
	}),
	actions: [{
		type: 'add',
		path: 'tests/{{dashCase name}}.ava.js',
		templateFile: 'plop-templates/ava-test.js'
	}]
});


plop.setGenerator('test-dynamic-actions-only', {
	description: 'test dynamic actions only',
	prompts: [{
		type: 'input',
		name: 'name',
		message(): string {
			return 'test name';
		},
		validate(value): true | string {
			if ((/.+/).test(value)) { return true; }
			return 'test name is required';
		}
	}],
	actions(data) {
		return [{
			type: 'add',
			path: 'tests/{{dashCase name}}.ava.js',
			templateFile: 'plop-templates/ava-test.js',
		}];
	}
});

plop.setGenerator('test-dynamic-prompts-and-actions', {
	description: 'Uses dynamic prompts and actions',
	async prompts(inquirer) {
		return {
			name: 'something-dynamic'
		};
	},
	actions(data) {
		return [{
			type: 'add',
			path: 'tests/{{dashCase name}}.ava.js',
			templateFile: 'plop-templates/ava-test.js',
		}];
	}
});

const useAddManyAction = (): AddManyActionConfig => ({
	type: 'addMany',
	base: '',
	templateFiles: '',
	path: '',
	destination: '',
	stripExtensions: ['hbs'],
	globOptions: {
		dot: true
	},
});

const useAddManyTransformAction = (): AddManyActionConfig => ({
	type: 'addMany',
	base: '',
	templateFiles: '',
	path: '',
	destination: '',
	stripExtensions: ['hbs'],
	transform: (): string => 'hello',
	globOptions: {
		dot: true
	},
});

const useAddActionTemplateOnly = (): AddActionConfig => ({
	type: 'add',
	path: '/some/path',
	template: 'a template {{ someVar }}'
});

const useAddActionTemplateFileOnly = (): AddActionConfig => ({
	type: 'add',
	path: '/some/path',
	templateFile: 'path/to/some/template.hbs'
});

// @ts-expect-error "Only partial type"
const useAddActionNoTemplateOrFileErrors = (): AddActionConfig => ({
	type: 'add',
	path: 'some/path'
});

function a(plop: NodePlopAPI) {
	plop.setGenerator('basics', {
		description: 'this is a skeleton plopfile',
		prompts: [], // array of inquirer prompts
		actions: []  // array of actions
	});
}

function b(plop: NodePlopAPI) {
	plop.setGenerator('controller', {
		description: 'application controller logic',
		prompts: [{
			type: 'input',
			name: 'name',
			message: 'controller name please'
		}],
		actions: [{
			type: 'add',
			path: 'src/{{name}}.js',
			templateFile: 'plop-templates/controller.hbs'
		}]
	});
}

function c(plop: NodePlopAPI) {
	plop.setHelper('upperCase', function (text) {
		return text.toUpperCase();
	});

	// or in es6/es2015
	plop.setHelper('upperCase', (txt) => txt.toUpperCase());
}

function d(plop: NodePlopAPI) {
	plop.setPartial('myTitlePartial', '<h1>{{titleCase name}}</h1>');
}

function e(plop: NodePlopAPI) {
	function doSomething(...args: any[]) {}

	plop.setActionType('doTheThing', function (answers, config, plop) {
		// do something
		doSomething(config.configProp);
		// if something went wrong
		if (!!doSomething) throw 'error message';
		// otherwise
		return 'success status message';
	});

	// or do async things inside of an action
	plop.setActionType('doTheAsyncThing', function (answers, config, plop) {
		// do something
		return new Promise((resolve, reject) => {
			if (!!answers) {
				resolve('success status message');
			} else {
				reject('error message');
			}
		});
	});

	// use the custom action
	plop.setGenerator('test', {
		prompts: [],
		actions: [{
			type: 'doTheThing',
			configProp: 'available from the config param'
		} as CustomActionConfig<'doTheThing'>,
		{
			type: 'doTheAsyncThing',
			speed: 'slow'
		}  as CustomActionConfig<'doTheAsyncThing'>
		]
	});
}

function ee(plop: NodePlopAPI) {
	plop.setPrompt('directory', prompt);
	plop.setGenerator('test', {
		prompts: [{
			type: 'directory'
		}]
	});
}

function f(plop: NodePlopAPI) {
	plop.setGenerator('test', {
		prompts: [{
			type: 'confirm',
			name: 'wantTacos',
			message: 'Do you want tacos?'
		}],
		actions: function(data) {
			var actions: Actions = [];

			if(data && data.wantTacos) {
				actions.push({
					type: 'add',
					path: 'folder/{{dashCase name}}.txt',
					templateFile: 'templates/tacos.txt'
				});
			} else {
				actions.push({
					type: 'add',
					path: 'folder/{{dashCase name}}.txt',
					templateFile: 'templates/burritos.txt'
				});
			}

			return actions;
		}
	});
}

let _;
_ = (async () => {
	// Code from plop itself
	const plop = await nodePlop('test', {
		destBasePath: !!inquirer ? 'test' : undefined,
		force: false,
	});

	const generators = plop.getGeneratorList();
	const generatorNames = generators.map((v) => v.name);
	const generatorNames2 = plop.getGeneratorList().map((v) => v.name);
		let j = generatorNames2.some(function (txt) {
			return txt.indexOf('test') === 0;
		});

	const generator = plop.getGenerator('test');
	if (typeof generator.prompts === "function") {
		return [];
	}

	const promptNames = generator.prompts.map((prompt) => prompt.name);

	generator
		.runPrompts(['a'])
		.then(async (answers) => {
			return answers;
		})
		.then((answers) => {
			return generator
				.runActions(answers, {
					onSuccess: (change) => {
						let line = "";
						if (change.type) {
							line += ` ${change.type}`;
						}
						if (change.path) {
							line += ` ${change.path}`;
						}
					},
					onFailure: (fail) => {
						let line = "";
						if (fail.type) {
							line += ` ${fail.type}`;
						}
						if (fail.path) {
							line += ` ${fail.path}`;
						}
						const errMsg = fail.error || fail.message;
					},
					onComment: (msg) => {
						console.log(msg);
					}
				})
				.then(() => {
					console.log("Test")
				});
		})
		.catch(function (err) {
			process.exit(1);
		});
})

function addActionTests(plop: NodePlopAPI) {
	let action;
	// @ts-expect-error "Only template or template file on add"
	action = {
		type: 'add',
		template: '',
		templateFile: ''
	} as AddActionConfig

	action = {
		type: 'add',
		templateFile: ''
	} as AddActionConfig

	action = {
		type: 'add',
		template: ''
	} as AddActionConfig
}

function modifyActionTests(plop: NodePlopAPI) {
	let action;
	// @ts-expect-error "Only template or template file on modify"
	action = {
		type: 'modify',
		template: '',
		templateFile: '',
		path: '',
		pattern: ''
	} as ModifyActionConfig

	action = {
		type: 'modify',
		templateFile: '',
		path: '',
		pattern: ''
	} as ModifyActionConfig

	action = {
		type: 'modify',
		template: '',
		path: '',
		pattern: ''
	} as ModifyActionConfig
}

function appendActionTests(plop: NodePlopAPI) {
	let action;
	// @ts-expect-error "Only template or template file on modify"
	action = {
		type: 'append',
		template: '',
		templateFile: '',
		path: '',
		pattern: ''
	} as AppendActionConfig

	action = {
		type: 'append',
		templateFile: '',
		path: '',
		pattern: ''
	} as AppendActionConfig

	action = {
		type: 'append',
		template: '',
		path: '',
		pattern: ''
	} as AppendActionConfig
}
