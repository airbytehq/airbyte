/**
 * using the @types/prismjs does not fix the following warning:
 *
 * TS7016: Could not find a declaration file for module 'prismjs/components/prism-core'. '/Users/evan/workspace/airbyte/airbyte/airbyte-webapp/node_modules/prismjs/components/prism-core.js' implicitly has an 'any' type.
 * Try `npm i --save-dev @types/prismjs` if it exists or add a new declaration (.d.ts) file containing `declare module 'prismjs/components/prism-core';`
 */

declare module "prismjs/components/prism-core";
