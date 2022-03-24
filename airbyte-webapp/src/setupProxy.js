/* eslint-disable @typescript-eslint/no-var-requires */

/**
 * This file is used by create-react-app to configure the express instance used
 * to serve files during development.
 */
const express = require("express");

module.exports = (app) => {
  // Serve the doc markdowns and assets that are also bundled into the docker image
  app.use(
    "/docs/integrations",
    express.static(`${__dirname}/../../docs/integrations`)
  );
  app.use("/docs/.gitbook", express.static(`${__dirname}/../../docs/.gitbook`));
};
