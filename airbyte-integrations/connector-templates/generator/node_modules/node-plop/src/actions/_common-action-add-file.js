import path from 'path';
import del from 'del';
import {
	getRenderedTemplate,
	getTransformedTemplate,
	makeDestPath,
	throwStringifiedError,
	getRelativeToBasePath
} from './_common-action-utils.js';
import {isBinaryFileSync} from 'isbinaryfile';
import * as fspp from '../fs-promise-proxy.js';

export default async function addFile(data, cfg, plop) {
	const fileDestPath = makeDestPath(data, cfg, plop);
	const { force, skipIfExists = false } = cfg;
	try {
		// check path
		let destExists = await fspp.fileExists(fileDestPath);

		// if we are forcing and the file already exists, delete the file
		if (force === true && destExists) {
			await del([fileDestPath], {force});
			destExists = false;
		}

		// we can't create files where one already exists
		if (destExists) {
			if (skipIfExists) { return `[SKIPPED] ${fileDestPath} (exists)`; }
			throw `File already exists\n -> ${fileDestPath}`;
		} else {
			await fspp.makeDir(path.dirname(fileDestPath));

			const absTemplatePath = cfg.templateFile
				&& path.resolve(plop.getPlopfilePath(), cfg.templateFile)
				|| null;

			if (absTemplatePath != null && isBinaryFileSync(absTemplatePath)) {
				const rawTemplate = await fspp.readFileRaw(cfg.templateFile);
				await fspp.writeFileRaw(fileDestPath, rawTemplate);
			} else {
				const renderedTemplate = await getRenderedTemplate(data, cfg, plop);

				const transformedTemplate = await getTransformedTemplate(
					renderedTemplate,
					data,
					cfg
				);

				await fspp.writeFile(fileDestPath, transformedTemplate);
			}

			// keep the executable flags
			if (absTemplatePath != null) {
				const sourceStats = await fspp.stat(absTemplatePath);
				const destStats = await fspp.stat(fileDestPath);
				const executableFlags = sourceStats.mode & (
					fspp.constants.S_IXUSR | fspp.constants.S_IXGRP | fspp.constants.S_IXOTH
				);
				await fspp.chmod(fileDestPath, destStats.mode | executableFlags);
			}
		}

		// return the added file path (relative to the destination path)
		return getRelativeToBasePath(fileDestPath, plop);
	} catch (err) {
		throwStringifiedError(err);
	}
}
