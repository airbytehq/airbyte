import type { Connect, Plugin } from "vite";

import express from "express";

export function docMiddleware(): Plugin {
  return {
    name: "airbyte/doc-middleware",
    configureServer(server) {
      // Serve the docs used in the sidebar. During building Gradle will copy those into the docker image
      // Relavant gradle task :airbyte-webapp:copyDocs
      server.middlewares.use(
        "/docs/integrations",
        express.static(`${__dirname}/../../../docs/integrations`) as Connect.NextHandleFunction
      );
      // workaround for adblockers to serve google ads docs in development
      server.middlewares.use(
        "/docs/integrations/sources/gglad.md",
        express.static(`${__dirname}/../../../docs/integrations/sources/google-ads.md`) as Connect.NextHandleFunction
      );
      // Server assets that can be used during. Related gradle task: :airbyte-webapp:copyDocAssets
      server.middlewares.use(
        "/docs/.gitbook",
        express.static(`${__dirname}/../../../docs/.gitbook`) as Connect.NextHandleFunction
      );
    },
  };
}
