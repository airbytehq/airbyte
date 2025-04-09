import fs from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

export const getFileHelper = () => {
  let cleanupFile = null;

  afterEach(() => {
    if (!cleanupFile) return;
    try {
      fs.unlinkSync(cleanupFile);
    } catch (e) {}
    cleanupFile = null;
  });

  const getFilePath = async (path) => {
    const expectedFilePath = resolve(__dirname, path);

    cleanupFile = expectedFilePath;
    try {
      await fs.promises.unlink(cleanupFile);
    } catch (e) {}

    return expectedFilePath;
  };

  return {
    getFilePath,
  };
};
