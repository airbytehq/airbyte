/* eslint-disable @typescript-eslint/no-var-requires */

/**
 * This file is used by create-react-app to configure the express instance used
 * to serve files during development.
 */
const express = require("express");

module.exports = (app) => {
  // Set the CSP header in development to detect potential breakages.
  // This should always match the header in airbyte-webapp/nginx/default.conf.template
  app.use((req, resp, next) => {
    resp.header("Content-Security-Policy", "script-src * 'unsafe-inline'; worker-src self blob:;");
    next();
  });
  // Serve the doc markdowns and assets that are also bundled into the docker image
  app.use("/docs/integrations", express.static(`${__dirname}/../../docs/integrations`));
  // workaround for adblockers to serve google ads docs in development
  app.use(
    "/docs/integrations/sources/gglad.md",
    express.static(`${__dirname}/../../docs/integrations/sources/google-ads.md`)
  );
  app.use("/docs/.gitbook", express.static(`${__dirname}/../../docs/.gitbook`));
};
