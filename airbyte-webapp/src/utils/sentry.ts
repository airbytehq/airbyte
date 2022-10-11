export const loadSentry = async (): Promise<void> => {
  const dsn = process.env.REACT_APP_SENTRY_DSN ?? window.REACT_APP_SENTRY_DSN;
  if (!dsn) {
    return;
  }

  const [Sentry, { Integrations }] = await Promise.all([import("@sentry/react"), import("@sentry/tracing")]);

  const release = process.env.REACT_APP_WEBAPP_TAG ?? window.REACT_APP_WEBAPP_TAG ?? "dev";
  const integrations = [new Integrations.BrowserTracing()];

  Sentry.init({
    dsn,
    release,
    integrations,
    tracesSampleRate: 1.0,
  });
};
