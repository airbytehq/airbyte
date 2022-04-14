import { exec } from "child_process";
import { dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

const asyncExec = (cmd) =>
  new Promise((res, rej) =>
    exec(cmd, { cwd: __dirname }, (err, stdout, stderr) => {
      if (err || stderr) {
        console.error(err);
        console.error(stderr);
        rej(err || stderr);
      } else {
        console.log(stdout);
        res();
      }
    })
  );

(async () => {
  await asyncExec("orval");
  await asyncExec("npx eslint --fix ./src/core/request/GeneratedApi.ts");
  await asyncExec("npx prettier ./src/core/request/GeneratedApi.ts --write");
})();
