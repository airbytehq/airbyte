import { lazy, Suspense } from "react";
import ReactDOM from "react-dom";

import "react-reflex/styles.css";
import { isCloudApp } from "utils/app";
import { initDatadogRum } from "utils/datadog";
import { loadOsano } from "utils/dataPrivacy";
import { initSentry } from "utils/sentry";

import "./globals";

// We do not follow default config approach since we want to init sentry/datadog asap
initSentry();
initDatadogRum();

// In Cloud load the Osano script (GDPR consent tool before anything else)
if (isCloudApp()) {
  loadOsano();
}

const CloudApp = lazy(() => import(`packages/cloud/App`));
const App = lazy(() => import(`./App`));

ReactDOM.render(
  <Suspense fallback={null}>{isCloudApp() ? <CloudApp /> : <App />}</Suspense>,
  document.getElementById("root")
);
