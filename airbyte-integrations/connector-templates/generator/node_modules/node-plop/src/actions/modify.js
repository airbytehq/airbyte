import * as fspp from '../fs-promise-proxy.js';
import {
	getRenderedTemplate,
	makeDestPath,
	throwStringifiedError,
	getRelativeToBasePath,
	getRenderedTemplatePath,
	getTransformedTemplate
} from './_common-action-utils.js';

import actionInterfaceTest from './_common-action-interface-check.js';

export default async function (data, cfg, plop) {
	const interfaceTestResult = actionInterfaceTest(cfg);
	if (interfaceTestResult !== true) {
		throw interfaceTestResult;
	}
	const fileDestPath = makeDestPath(data, cfg, plop);
	try {
		// check path
		const pathExists = await fspp.fileExists(fileDestPath);

		if (!pathExists) {
			throw 'File does not exist';
		} else {
			let fileData = await fspp.readFile(fileDestPath);
			cfg.templateFile = getRenderedTemplatePath(data, cfg, plop);
			const replacement = await getRenderedTemplate(data, cfg, plop);

			if (typeof cfg.pattern === 'string' || cfg.pattern instanceof RegExp) {
				fileData = fileData.replace(cfg.pattern, replacement);
			}

			const transformed = await getTransformedTemplate(fileData, data, cfg);
			await fspp.writeFile(fileDestPath, transformed);
		}
		return getRelativeToBasePath(fileDestPath, plop);
	} catch (err) {
		throwStringifiedError(err);
	}
}
