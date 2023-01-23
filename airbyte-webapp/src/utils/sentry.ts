import * as Sentry from "@sentry/react";
import { Integrations } from "@sentry/tracing";

import { config } from "config";

export const loadSentry = (): void => {
  const { sentryDsn, webappTag } = config;
  if (!sentryDsn) {
    return;
  }

  const integrations = [new Integrations.BrowserTracing()];

  Sentry.init({
    dsn: sentryDsn,
    release: webappTag,
    integrations,
    tracesSampleRate: 1.0,
  });
};
