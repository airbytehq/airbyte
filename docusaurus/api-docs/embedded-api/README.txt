Embedded API Documentation
==========================

This directory contains auto-generated API documentation files that are created during the build process.

The files in this directory are generated from the OpenAPI specification defined in:
- docusaurus/src/data/embedded_api_spec.json
- docusaurus/src/scripts/embedded-api/prepare-embedded-api-spec.js

Why is this folder gitignored?
-------------------------------

The API documentation files (*.api.mdx, sidebar.ts, etc.) are generated during `pnpm build` and should NOT be committed to git.
This folder must exist for the build to succeed, but the generated files will be recreated each build.

To regenerate the documentation files locally, run:
  pnpm build

For more information about the embedded API docs generation, see:
- docusaurus/src/scripts/embedded-api/openapi-validator.js
- docusaurus/src/scripts/embedded-api/prepare-embedded-api-spec.js
