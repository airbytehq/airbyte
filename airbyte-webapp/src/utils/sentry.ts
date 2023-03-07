import * as Sentry from "@sentry/react";
import { Integrations } from "@sentry/tracing";

export const loadSentry = (): void => {
  const dsn = window.REACT_APP_SENTRY_DSN ?? process.env.REACT_APP_SENTRY_DSN;
  if (!dsn) {
    return;
  }

  const release = window.REACT_APP_WEBAPP_TAG ?? process.env.REACT_APP_WEBAPP_TAG ?? "dev";
  const integrations = [new Integrations.BrowserTracing()];

  Sentry.init({
    dsn,
    release,
    integrations,
    tracesSampleRate: 1.0,
  });
};
