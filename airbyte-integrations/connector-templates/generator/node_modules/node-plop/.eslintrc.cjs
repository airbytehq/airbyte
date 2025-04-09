const ts = {
	files: ['**/*.ts'],
	extends: [
		'eslint:recommended',
		'plugin:@typescript-eslint/eslint-recommended',
		'plugin:@typescript-eslint/recommended'
	],
	parser: '@typescript-eslint/parser',
	parserOptions: {
		ecmaVersion: 2018,
		sourceType: 'module',
		project: './tsconfig.json',
		allowImportExportEverywhere: true
	},
	plugins: ['@typescript-eslint'],
	rules: {
		'@typescript-eslint/no-explicit-any': 0
	}
};

module.exports = {
	env: {
		es6: true,
		node: true
	},
	extends: 'eslint:recommended',
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2021,
		allowImportExportEverywhere: true
	},
	rules: {
		'require-atomic-updates': 0,
		indent: ['error', 'tab'],
		quotes: ['error', 'single'],
		semi: ['error', 'always']
	},
	overrides: [ts]
};
