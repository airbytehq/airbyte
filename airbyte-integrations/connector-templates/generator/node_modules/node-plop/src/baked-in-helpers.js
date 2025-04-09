import * as changeCase from 'change-case';
import {titleCase} from 'title-case';
import {upperCase} from 'upper-case';
import {lowerCase} from 'lower-case';

export default {
	camelCase: changeCase.camelCase,
	snakeCase: changeCase.snakeCase,
	dotCase: changeCase.dotCase,
	pathCase: changeCase.pathCase,
	lowerCase: lowerCase,
	upperCase: upperCase,
	sentenceCase: changeCase.sentenceCase,
	constantCase: changeCase.constantCase,
	titleCase: titleCase,

	dashCase: changeCase.paramCase,
	kabobCase: changeCase.paramCase,
	kebabCase: changeCase.paramCase,

	properCase: changeCase.pascalCase,
	pascalCase: changeCase.pascalCase
};
