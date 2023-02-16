import { statSync, existsSync } from "fs";
import { resolve } from "path";

import conf from "../orval.config";

const lastTouched = (filepath: string) => statSync(resolve(filepath)).mtime;

for (const [, api] of Object.entries(conf)) {
  if (!existsSync(api.output.target) || lastTouched(api.input) > lastTouched(api.output.target)) {
    // no need to read and parse the orval lib if all files are up to date
    require("orval").generate(api);
  }
}
